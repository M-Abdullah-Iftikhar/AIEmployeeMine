"""
Django REST Framework API views for Project Manager Agent features
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import (
    EmailTemplate, EmailLog, EmailReminder,
    NotificationPreference, Notification,
    TaskTag, TaskActivityLog, DashboardView,
    TaskComment, CommentAttachment,
    TimeEntry, TimerSession,
    ProjectHealthScore, ProjectRisk, ProjectIssue,
    TaskAttachment, Task, Project
)
from .serializers import (
    EmailTemplateSerializer, EmailLogSerializer, EmailReminderSerializer,
    NotificationPreferenceSerializer, NotificationSerializer,
    TaskTagSerializer, TaskActivityLogSerializer, DashboardViewSerializer,
    TaskCommentSerializer, CommentAttachmentSerializer,
    TimeEntrySerializer, TimerSessionSerializer,
    ProjectHealthScoreSerializer, ProjectRiskSerializer, ProjectIssueSerializer,
    TaskAttachmentSerializer
)


# Email & Communication ViewSets
class EmailTemplateViewSet(viewsets.ModelViewSet):
    """API endpoint for email templates"""
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'template_type']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        queryset = EmailTemplate.objects.all()
        # Manual filtering
        template_type = self.request.query_params.get('template_type')
        is_active = self.request.query_params.get('is_active')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for email logs (read-only)"""
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['recipient', 'subject']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        user_email = self.request.user.email
        queryset = EmailLog.objects.filter(recipient=user_email)
        # Manual filtering
        status_param = self.request.query_params.get('status')
        template_id = self.request.query_params.get('template')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset


class EmailReminderViewSet(viewsets.ModelViewSet):
    """API endpoint for email reminders"""
    serializer_class = EmailReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['reminder_time', 'created_at']
    ordering = ['reminder_time']
    
    def get_queryset(self):
        queryset = EmailReminder.objects.filter(recipient=self.request.user)
        # Manual filtering
        reminder_type = self.request.query_params.get('reminder_type')
        status_param = self.request.query_params.get('status')
        task_id = self.request.query_params.get('task')
        milestone_id = self.request.query_params.get('milestone')
        meeting_id = self.request.query_params.get('meeting')
        if reminder_type:
            queryset = queryset.filter(reminder_type=reminder_type)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if milestone_id:
            queryset = queryset.filter(milestone_id=milestone_id)
        if meeting_id:
            queryset = queryset.filter(meeting_id=meeting_id)
        return queryset


# Notification ViewSets
class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """API endpoint for notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = NotificationPreference.objects.filter(user=self.request.user)
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        # Manual filtering
        type_param = self.request.query_params.get('type')
        notification_type = self.request.query_params.get('notification_type')
        is_read = self.request.query_params.get('is_read')
        if type_param:
            queryset = queryset.filter(type=type_param)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'status': 'marked all as read', 'count': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'count': count})


# Task Monitoring ViewSets
class TaskTagViewSet(viewsets.ModelViewSet):
    """API endpoint for task tags"""
    serializer_class = TaskTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        # Users can see tags for projects they're part of
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = TaskTag.objects.filter(
            Q(project__in=user_projects) | Q(project__isnull=True)
        ).distinct()
        # Manual filtering
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class TaskActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for task activity logs (read-only)"""
    serializer_class = TaskActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see activity logs for tasks in projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = TaskActivityLog.objects.filter(task__project__in=user_projects)
        # Manual filtering
        task_id = self.request.query_params.get('task')
        user_id = self.request.query_params.get('user')
        action_type = self.request.query_params.get('action_type')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        return queryset


class DashboardViewViewSet(viewsets.ModelViewSet):
    """API endpoint for dashboard views"""
    serializer_class = DashboardViewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['-is_default', 'name']
    
    def get_queryset(self):
        queryset = DashboardView.objects.filter(
            Q(user=self.request.user) | Q(is_shared=True)
        )
        # Manual filtering
        view_type = self.request.query_params.get('view_type')
        is_default = self.request.query_params.get('is_default')
        is_shared = self.request.query_params.get('is_shared')
        if view_type:
            queryset = queryset.filter(view_type=view_type)
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == 'true')
        if is_shared is not None:
            queryset = queryset.filter(is_shared=is_shared.lower() == 'true')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Task Comments ViewSets
class CommentAttachmentViewSet(viewsets.ModelViewSet):
    """API endpoint for comment attachments"""
    serializer_class = CommentAttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        comment_id = self.request.query_params.get('comment')
        if comment_id:
            return CommentAttachment.objects.filter(comment_id=comment_id)
        return CommentAttachment.objects.none()


class TaskCommentViewSet(viewsets.ModelViewSet):
    """API endpoint for task comments"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        # Users can see comments for tasks in projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = TaskComment.objects.filter(task__project__in=user_projects)
        # Manual filtering
        task_id = self.request.query_params.get('task')
        user_id = self.request.query_params.get('user')
        parent_comment_id = self.request.query_params.get('parent_comment')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if parent_comment_id:
            queryset = queryset.filter(parent_comment_id=parent_comment_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Time Tracking ViewSets
class TimeEntryViewSet(viewsets.ModelViewSet):
    """API endpoint for time entries"""
    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        # Users can see their own time entries, or time entries for projects they manage
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user)
        ).distinct()
        queryset = TimeEntry.objects.filter(
            Q(user=self.request.user) |
            Q(task__project__in=user_projects)
        )
        # Manual filtering
        task_id = self.request.query_params.get('task')
        user_id = self.request.query_params.get('user')
        date = self.request.query_params.get('date')
        billable = self.request.query_params.get('billable')
        approved_by_id = self.request.query_params.get('approved_by')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if date:
            queryset = queryset.filter(date=date)
        if billable is not None:
            queryset = queryset.filter(billable=billable.lower() == 'true')
        if approved_by_id:
            queryset = queryset.filter(approved_by_id=approved_by_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a time entry (requires project manager/owner permissions)"""
        time_entry = self.get_object()
        project = time_entry.task.project
        
        # Check permissions
        if project.owner != request.user and project.project_manager != request.user:
            return Response(
                {'error': 'Permission denied. Only project owners/managers can approve time entries.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        time_entry.approved_by = request.user
        time_entry.approved_at = timezone.now()
        time_entry.save()
        
        serializer = self.get_serializer(time_entry)
        return Response(serializer.data)


class TimerSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for timer sessions"""
    serializer_class = TimerSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['started_at']
    ordering = ['-started_at']
    
    def get_queryset(self):
        queryset = TimerSession.objects.filter(user=self.request.user)
        # Manual filtering
        task_id = self.request.query_params.get('task')
        user_id = self.request.query_params.get('user')
        is_active = self.request.query_params.get('is_active')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop an active timer session"""
        timer = self.get_object()
        if not timer.is_active:
            return Response(
                {'error': 'Timer is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        timer.ended_at = timezone.now()
        if timer.started_at:
            duration = timer.ended_at - timer.started_at
            timer.duration_minutes = int(duration.total_seconds() / 60)
        timer.is_active = False
        timer.save()
        
        serializer = self.get_serializer(timer)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active timer session for current user"""
        try:
            timer = TimerSession.objects.get(user=request.user, is_active=True)
            serializer = self.get_serializer(timer)
            return Response(serializer.data)
        except TimerSession.DoesNotExist:
            return Response({'active': False})


# Project Health & Risk ViewSets
class ProjectHealthScoreViewSet(viewsets.ModelViewSet):
    """API endpoint for project health scores"""
    serializer_class = ProjectHealthScoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'overall_score']
    ordering = ['-date']
    
    def get_queryset(self):
        # Users can see health scores for projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = ProjectHealthScore.objects.filter(project__in=user_projects)
        # Manual filtering
        project_id = self.request.query_params.get('project')
        date = self.request.query_params.get('date')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset


class ProjectRiskViewSet(viewsets.ModelViewSet):
    """API endpoint for project risks"""
    serializer_class = ProjectRiskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['severity', 'identified_at']
    ordering = ['-severity', '-identified_at']
    
    def get_queryset(self):
        # Users can see risks for projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = ProjectRisk.objects.filter(project__in=user_projects)
        # Manual filtering
        project_id = self.request.query_params.get('project')
        task_id = self.request.query_params.get('task')
        severity = self.request.query_params.get('severity')
        status_param = self.request.query_params.get('status')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if severity:
            queryset = queryset.filter(severity=severity)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(identified_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a risk"""
        risk = self.get_object()
        risk.status = 'resolved'
        risk.resolved_by = request.user
        risk.resolved_at = timezone.now()
        risk.save()
        
        serializer = self.get_serializer(risk)
        return Response(serializer.data)


class ProjectIssueViewSet(viewsets.ModelViewSet):
    """API endpoint for project issues"""
    serializer_class = ProjectIssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['severity', 'created_at']
    ordering = ['-severity', '-created_at']
    
    def get_queryset(self):
        # Users can see issues for projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = ProjectIssue.objects.filter(project__in=user_projects)
        # Manual filtering
        project_id = self.request.query_params.get('project')
        task_id = self.request.query_params.get('task')
        severity = self.request.query_params.get('severity')
        status_param = self.request.query_params.get('status')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        if severity:
            queryset = queryset.filter(severity=severity)
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an issue"""
        issue = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        issue.status = 'resolved'
        issue.resolved_by = request.user
        issue.resolved_at = timezone.now()
        if resolution_notes:
            issue.resolution_notes = resolution_notes
        issue.save()
        
        serializer = self.get_serializer(issue)
        return Response(serializer.data)


# Task Attachment ViewSet
class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """API endpoint for task attachments"""
    serializer_class = TaskAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can see attachments for tasks in projects they have access to
        user_projects = Project.objects.filter(
            Q(owner=self.request.user) |
            Q(project_manager=self.request.user) |
            Q(team_members__user=self.request.user, team_members__removed_at__isnull=True)
        ).distinct()
        queryset = TaskAttachment.objects.filter(task__project__in=user_projects)
        # Manual filtering
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def increment_download(self, request, pk=None):
        """Increment download count for attachment"""
        attachment = self.get_object()
        attachment.download_count += 1
        attachment.save()
        serializer = self.get_serializer(attachment)
        return Response(serializer.data)
