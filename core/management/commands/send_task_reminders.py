"""
Management command to send scheduled task reminder emails.
Run this command periodically (e.g., via cron or scheduled task) to send reminders.

Usage:
    python manage.py send_task_reminders
    python manage.py send_task_reminders --days 1,3,7  # Remind 1, 3, and 7 days before due
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Task, EmailReminder
from core.email_service import EmailService


class Command(BaseCommand):
    help = 'Send email reminders for tasks with upcoming due dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=str,
            default='1,3',
            help='Comma-separated list of days before due date to send reminders (default: 1,3)',
        )
        parser.add_argument(
            '--overdue',
            action='store_true',
            help='Also send notifications for overdue tasks',
        )

    def handle(self, *args, **options):
        days_list = [int(d.strip()) for d in options['days'].split(',')]
        send_overdue = options.get('overdue', False)
        
        email_service = EmailService()
        now = timezone.now()
        sent_count = 0
        error_count = 0
        
        self.stdout.write(f"Starting task reminder check at {now}")
        self.stdout.write(f"Reminder days: {days_list}")
        
        # Process each reminder day
        for days_before in days_list:
            target_date = now + timedelta(days=days_before)
            target_date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            target_date_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Find tasks due on this date that have assignees
            tasks = Task.objects.filter(
                due_date__gte=target_date_start,
                due_date__lte=target_date_end,
                assignee__isnull=False,
                status__in=['todo', 'in_progress', 'review'],  # Only active tasks
            ).select_related('assignee', 'project')
            
            self.stdout.write(f"\nChecking tasks due in {days_before} days ({target_date.date()})...")
            task_count = tasks.count()
            self.stdout.write(f"Found {task_count} tasks")
            
            for task in tasks:
                try:
                    # Check if we've already sent a reminder for this task today
                    existing_reminder = EmailReminder.objects.filter(
                        task=task,
                        reminder_type='task_due',
                        status='sent',
                        sent_at__date=now.date(),
                    ).exists()
                    
                    if existing_reminder:
                        continue
                    
                    # Send reminder
                    success = email_service.send_task_due_reminder(
                        task=task,
                        recipient=task.assignee,
                        days_until_due=days_before
                    )
                    
                    if success:
                        # Create or update EmailReminder record
                        EmailReminder.objects.update_or_create(
                            task=task,
                            reminder_type='task_due',
                            recipient=task.assignee,
                            reminder_time=target_date_start,
                            defaults={
                                'status': 'sent',
                                'sent_at': now,
                            }
                        )
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Sent reminder for task: {task.title}")
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Failed to send reminder for task: {task.title}")
                        )
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error processing task {task.id}: {str(e)}")
                    )
        
        # Handle overdue tasks if requested
        if send_overdue:
            self.stdout.write("\nChecking for overdue tasks...")
            overdue_tasks = Task.objects.filter(
                due_date__lt=now,
                assignee__isnull=False,
                status__in=['todo', 'in_progress', 'review'],  # Only active tasks
            ).select_related('assignee', 'project')
            
            overdue_count = overdue_tasks.count()
            self.stdout.write(f"Found {overdue_count} overdue tasks")
            
            for task in overdue_tasks:
                try:
                    # Only send one overdue notification per day per task
                    existing_notification = EmailReminder.objects.filter(
                        task=task,
                        reminder_type='task_overdue',
                        status='sent',
                        sent_at__date=now.date(),
                    ).exists()
                    
                    if existing_notification:
                        continue
                    
                    # Send overdue notification
                    success = email_service.send_task_overdue_notification(
                        task=task,
                        recipient=task.assignee
                    )
                    
                    if success:
                        EmailReminder.objects.update_or_create(
                            task=task,
                            reminder_type='task_overdue',
                            recipient=task.assignee,
                            reminder_time=task.due_date,
                            defaults={
                                'status': 'sent',
                                'sent_at': now,
                            }
                        )
                        sent_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Sent overdue notification for task: {task.title}")
                        )
                    else:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Failed to send overdue notification for task: {task.title}")
                        )
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error processing overdue task {task.id}: {str(e)}")
                    )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write("="*50)

