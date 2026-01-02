"""
Management command to send scheduled meeting reminder emails.
Run this command periodically to send reminders for upcoming meetings.

Usage:
    python manage.py send_meeting_reminders
    python manage.py send_meeting_reminders --hours 1,24  # Remind 1 hour and 24 hours before
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Meeting, EmailReminder
from core.email_service import EmailService


class Command(BaseCommand):
    help = 'Send email reminders for upcoming meetings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=str,
            default='1,24',
            help='Comma-separated list of hours before meeting to send reminders (default: 1,24)',
        )

    def handle(self, *args, **options):
        hours_list = [int(h.strip()) for h in options['hours'].split(',')]
        
        email_service = EmailService()
        now = timezone.now()
        sent_count = 0
        error_count = 0
        
        self.stdout.write(f"Starting meeting reminder check at {now}")
        self.stdout.write(f"Reminder hours: {hours_list}")
        
        # Process each reminder hour
        for hours_before in hours_list:
            target_time = now + timedelta(hours=hours_before)
            target_time_start = target_time.replace(minute=0, second=0, microsecond=0)
            target_time_end = target_time.replace(minute=59, second=59, microsecond=999999)
            
            # Find meetings starting at this time (within 1 hour window)
            meetings = Meeting.objects.filter(
                scheduled_at__gte=target_time_start,
                scheduled_at__lte=target_time_end,
            ).prefetch_related('participants', 'organizer')
            
            self.stdout.write(
                f"\nChecking meetings starting in {hours_before} hour{'s' if hours_before != 1 else ''} "
                f"({target_time_start})..."
            )
            meeting_count = meetings.count()
            self.stdout.write(f"Found {meeting_count} meetings")
            
            for meeting in meetings:
                try:
                    # Get all participants (including organizer)
                    participants = list(meeting.participants.all())
                    if meeting.organizer not in participants:
                        participants.append(meeting.organizer)
                    
                    if not participants:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠ No participants found for meeting: {meeting.title}")
                        )
                        continue
                    
                    # Send reminder to each participant
                    for participant in participants:
                        # Check if we've already sent a reminder for this meeting to this participant
                        existing_reminder = EmailReminder.objects.filter(
                            meeting=meeting,
                            reminder_type='meeting_upcoming',
                            recipient=participant,
                            status='sent',
                            sent_at__date=now.date(),
                        ).exists()
                        
                        if existing_reminder:
                            continue
                        
                        # Send reminder
                        success = email_service.send_meeting_reminder(
                            meeting=meeting,
                            recipient=participant,
                            hours_before=hours_before
                        )
                        
                        if success:
                            # Create or update EmailReminder record
                            EmailReminder.objects.update_or_create(
                                meeting=meeting,
                                reminder_type='meeting_upcoming',
                                recipient=participant,
                                reminder_time=target_time_start,
                                defaults={
                                    'status': 'sent',
                                    'sent_at': now,
                                }
                            )
                            sent_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"  ✓ Sent reminder to {participant.username} for meeting: {meeting.title}"
                                )
                            )
                        else:
                            error_count += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f"  ✗ Failed to send reminder to {participant.username} for meeting: {meeting.title}"
                                )
                            )
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Error processing meeting {meeting.id}: {str(e)}")
                    )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"Reminders sent: {sent_count}"))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write("="*50)

