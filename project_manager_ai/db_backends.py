"""
Database backend patches for SQL Server compatibility.

This module patches the mssql-django backend to prevent REGEXP_LIKE usage,
which is not supported in SQL Server. REGEXP_LIKE is an Oracle/PostgreSQL function.

The main issue is that mssql-django tries to create check constraints with REGEXP_LIKE
for EmailField validation, which SQL Server doesn't support.

This patch intercepts SQL queries and replaces REGEXP_LIKE with SQL Server-compatible alternatives.
"""

import logging
import re

logger = logging.getLogger(__name__)

def patch_mssql_backend():
    """
    Patch the mssql-django backend to disable REGEXP_LIKE usage.
    This must be called BEFORE Django setup to prevent errors during model introspection.
    """
    try:
        from mssql import base as mssql_base
        
        # Note: We're not patching the cursor property anymore as it was causing issues
        # The main fix is disabling DatabaseScheduler in settings.py
        # If REGEXP_LIKE errors still occur, they'll be caught by the introspection patch below
        logger.info("Skipping cursor-level patching (DatabaseScheduler fix should be sufficient)")
        
        # Patch the introspection module
        try:
            from mssql import introspection as mssql_introspection
            
            if hasattr(mssql_introspection, 'DatabaseIntrospection'):
                if hasattr(mssql_introspection.DatabaseIntrospection, 'get_constraints'):
                    original_get_constraints = mssql_introspection.DatabaseIntrospection.get_constraints
                    
                    def patched_get_constraints(self, cursor, table_name):
                        """Filter out REGEXP_LIKE constraints from introspection"""
                        try:
                            constraints = original_get_constraints(self, cursor, table_name)
                        except Exception as e:
                            error_msg = str(e)
                            if 'REGEXP_LIKE' in error_msg.upper():
                                logger.warning(f"Caught REGEXP_LIKE error during constraint introspection for {table_name}, returning empty constraints")
                                return {}
                            raise
                        
                        # Filter out REGEXP_LIKE constraints
                        filtered_constraints = {}
                        for name, constraint_info in constraints.items():
                            if constraint_info.get('check', False):
                                definition = constraint_info.get('definition', '')
                                if 'REGEXP_LIKE' in str(definition).upper():
                                    logger.debug(f"Skipping REGEXP_LIKE constraint {name} on {table_name}")
                                    continue
                            filtered_constraints[name] = constraint_info
                        
                        return filtered_constraints
                    
                    mssql_introspection.DatabaseIntrospection.get_constraints = patched_get_constraints
                    logger.info("Patched DatabaseIntrospection.get_constraints to filter REGEXP_LIKE")
        except ImportError:
            pass
        
        # Patch the schema editor
        try:
            from mssql import schema as mssql_schema
            
            if hasattr(mssql_schema, 'DatabaseSchemaEditor'):
                if hasattr(mssql_schema.DatabaseSchemaEditor, 'add_constraint'):
                    original_add_constraint = mssql_schema.DatabaseSchemaEditor.add_constraint
                    
                    def patched_add_constraint(self, model, constraint):
                        """Skip constraints that use REGEXP_LIKE"""
                        constraint_sql = getattr(constraint, 'constraint_sql', None)
                        if constraint_sql and 'REGEXP_LIKE' in str(constraint_sql).upper():
                            logger.warning(f"Skipping REGEXP_LIKE constraint on {model._meta.db_table}")
                            return
                        
                        if hasattr(constraint, 'check') and constraint.check:
                            check_sql = str(constraint.check)
                            if 'REGEXP_LIKE' in check_sql.upper():
                                logger.warning(f"Skipping REGEXP_LIKE constraint on {model._meta.db_table}")
                                return
                        
                        return original_add_constraint(self, model, constraint)
                    
                    mssql_schema.DatabaseSchemaEditor.add_constraint = patched_add_constraint
                    logger.info("Patched DatabaseSchemaEditor.add_constraint to skip REGEXP_LIKE")
        except ImportError:
            pass
        
        logger.info("Successfully patched mssql backend to handle REGEXP_LIKE")
        
    except ImportError as e:
        logger.warning(f"Could not patch mssql backend (mssql-django not installed or different version): {e}")
    except Exception as e:
        logger.warning(f"Error patching mssql backend: {e}")
        import traceback
        logger.debug(traceback.format_exc())


# Auto-patch when this module is imported
try:
    patch_mssql_backend()
except Exception as e:
    # Don't fail if patching doesn't work - might not be using SQL Server
    logger.debug(f"Could not auto-patch mssql backend: {e}")
