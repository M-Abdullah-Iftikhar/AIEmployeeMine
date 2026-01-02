"""
Management command to send scheduled milestone reminder emails.
Run this command periodically to send reminders for upcoming milestones.

Usage:
    python manage.py send_milestone_reminders
    python manage.py send_milestone_reminders --days 1,7  # Remind 1 and 7 days before
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from core.models import ProjectMilestone, EmailReminder
from core.email_service import EmailService


class Command(BaseCommand):
    help = 'Send email reminders for upcoming project milestones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=str,
            default='1,7',
            help='Comma-separated list of days before due date to send reminders (default: 1,7)',
        )

    def handle(self, *args, **options):
        days_list = [int(d.strip()) for d in options['days'].split(',')]
        
        email_service = EmailService()
        now = timezone.now()
        sent_count = 0
        error_count = 0
        
        self.stdout.write(f"Starting milestone reminder check at {now}")
        self.stdout.write(f"Reminder days: {days_list}")
        
        # Process each reminder day
        for days_before in days_list:
            target_date = now + timedelta(days=days_before)
            target_date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            target_date_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Find milestones due on this date
            milestones = ProjectMilestone.objects.filter(
                due_date__gte=target_date_start.date(),
                due_date__lte=target_date_end.date(),
                status__in=['pending', 'in_progress'],  # Only active milestones
            ).select_related('project')
            
            self.stdout.write(f"\nChecking milestones due in {days_before} days ({target_date.date()})...")
            milestone_count = milestones.count()
            self.stdout.write(f"Found {milestone_count} milestones")
            
            for milestone in milestones:
                try:
                    # Get project team members to notify
                    project = milestone.project
                    recipients = []
                    
                    # Add project owner
                    if project.owner:
                        recipients.append(project.owner)
                    
                    # Add project manager if exists
                    if project.project_manager and project.project_manager != project.owner:
                        recipients.append(project.project_manager)
                    
                    # Add team members
                    team_members = project.team_members.filter(removed_at__isnull=True).select_related('user')
                    for team_member in team_members:
                        if team_member.user not in recipients:
                            recipients.append(team_member.user)
                    
                    if not recipients:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ No recipients found for milestone: {milestone.title}")
                        )
                        continue
                    
                    # Send reminder to each recipient
                    for recipient in recipients:
                        # Check if we've already sent a reminder for this milestone to this recipient today
                        existing_reminder = EmailReminder.objects.filter(
                            milestone=milestone,
                            reminder_type='milestone_due',
                            recipient=recipient,
                            status='sent',
                            sent_at__date=now.date(),
                        ).exists()
                        
                        if existing_reminder:
                            continue
                        
                        # Send reminder
                        success = email_service.send_milestone_reminder(
                            milestone=milestone,
                            recipient=recipient,
                            days_until_due=days_before
                        )
                        
                        if success:
                            # Create or update EmailReminder record
                            EmailReminder.objects.update_or_create(
                                milestone=milestone,
                                reminder_type='milestone_due',
                                recipient=recipient,
                                reminder_time=timezone.make_aware(target_date_start),
                                defaults={
                                    'status': 'sent',
                                    'sent_at': now,
                                }
                            )
                            sent_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  ✓ Sent reminder to {recipient.username} for milestone: {milestone.title}"
                                )
                            )
                        else:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f"  ✗ Failed to send reminder to {recipient.username} for milestone: {milestone.title}"
                                )
                            )
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error processing milestone {milestone.id}: {str(e)}")
                    )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write("="*50)

