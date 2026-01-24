# Import db_backends patch FIRST to fix REGEXP_LIKE issues with SQL Server
# This must be imported before Django setup
try:
    import project_manager_ai.db_backends
except ImportError:
    pass

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)



