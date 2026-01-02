"""
Views for Email Sending Status and Monitoring
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count

from .models import Campaign, EmailSendHistory, EmailSequence, EmailSequenceStep, Lead


@login_required
def email_sending_status(request, campaign_id):
    """View showing current email sending status for a campaign"""
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    
    # Get recent email activity (last 24 hours)
    last_24_hours = timezone.now() - timedelta(hours=24)
    
    # Get all sequence emails sent in the last 24 hours
    # ALL emails are sent through sequences, so we only track sequence emails
    sequence_emails = EmailSendHistory.objects.filter(
        campaign=campaign,
        email_template__sequence_steps__isnull=False,
        sent_at__gte=last_24_hours
    ).distinct().order_by('-sent_at')
    
    # Get pending emails (status = pending)
    pending_emails = EmailSendHistory.objects.filter(
        campaign=campaign,
        status='pending'
    ).order_by('-created_at')
    
    # Get upcoming sequence sends (emails that should be sent soon)
    upcoming_sequence_sends = []
    if campaign.status == 'active':
        sequences = EmailSequence.objects.filter(campaign=campaign, is_active=True).prefetch_related('steps__template')
        for sequence in sequences:
            steps = list(sequence.steps.all().order_by('step_order'))
            if not steps:
                continue
                
            for lead in campaign.leads.all()[:50]:  # Limit for performance
                # Find last sequence email sent for this lead in this sequence
                last_seq_email = EmailSendHistory.objects.filter(
                    campaign=campaign,
                    lead=lead,
                    email_template__sequence_steps__sequence=sequence
                ).order_by('-sent_at').first()
                
                next_step = None
                # Determine reference time: campaign start date or last sequence email
                if campaign.start_date:
                    from datetime import datetime
                    reference_time = timezone.make_aware(
                        datetime.combine(campaign.start_date, datetime.min.time())
                    )
                else:
                    reference_time = campaign.created_at if hasattr(campaign, 'created_at') else timezone.now()
                
                if last_seq_email:
                    # Find next step after last sent
                    last_step = None
                    for step in steps:
                        if step.template_id == last_seq_email.email_template_id:
                            last_step = step
                            break
                    
                    if last_step:
                        # Find next step
                        for step in steps:
                            if step.step_order > last_step.step_order:
                                next_step = step
                                break
                        if next_step:
                            reference_time = last_seq_email.sent_at
                else:
                    # No sequence email sent yet - use first step
                    next_step = steps[0] if steps else None
                
                if next_step:
                    delay = timedelta(
                        days=next_step.delay_days,
                        hours=next_step.delay_hours,
                        minutes=next_step.delay_minutes
                    )
                    next_send_time = reference_time + delay
                    
                    # Check if already sent
                    already_sent = EmailSendHistory.objects.filter(
                        campaign=campaign,
                        lead=lead,
                        email_template=next_step.template
                    ).exists()
                    
                    if not already_sent and next_send_time > timezone.now() and next_send_time <= timezone.now() + timedelta(hours=24):
                        upcoming_sequence_sends.append({
                            'lead': lead,
                            'sequence': sequence,
                            'next_step': next_step,
                            'next_send_time': next_send_time,
                        })
    
    # Sort upcoming sends by time
    upcoming_sequence_sends.sort(key=lambda x: x['next_send_time'])
    
    # Get statistics - only sequence emails exist now
    stats = {
        'total_sequence_sent': sequence_emails.count(),
        'pending_count': pending_emails.count(),
        'upcoming_count': len(upcoming_sequence_sends),
        'recent_activity': sequence_emails.count(),
    }
    
    # Get current sending status - only sequence emails
    currently_sending = {
        'sequences': sequence_emails.filter(status='pending').exists() or
                    sequence_emails.filter(sent_at__gte=timezone.now() - timedelta(minutes=5)).exists(),
    }
    
    context = {
        'campaign': campaign,
        'sequence_emails': sequence_emails[:20],  # Limit to recent 20
        'pending_emails': pending_emails[:10],
        'upcoming_sequence_sends': upcoming_sequence_sends[:20],
        'stats': stats,
        'currently_sending': currently_sending,
    }
    
    return render(request, 'marketing/email_sending_status.html', context)


@login_required
def email_status_api(request, campaign_id):
    """API endpoint for real-time email status updates"""
    campaign = get_object_or_404(Campaign, id=campaign_id, owner=request.user)
    
    # Get recent activity (last 5 minutes)
    # ALL emails are sequence emails now
    last_5_min = timezone.now() - timedelta(minutes=5)
    
    recent_sequence = EmailSendHistory.objects.filter(
        campaign=campaign,
        email_template__sequence_steps__isnull=False,
        sent_at__gte=last_5_min
    ).distinct().count()
    
    pending = EmailSendHistory.objects.filter(
        campaign=campaign,
        status='pending'
    ).count()
    
    return JsonResponse({
        'success': True,
        'sequence_sending': recent_sequence > 0,
        'pending_count': pending,
        'recent_sequence_count': recent_sequence,
        'timestamp': timezone.now().isoformat(),
    })

