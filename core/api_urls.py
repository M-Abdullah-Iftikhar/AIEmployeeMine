"""
API URL patterns for Project Manager Agent features
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    EmailTemplateViewSet, EmailLogViewSet, EmailReminderViewSet,
    NotificationPreferenceViewSet, NotificationViewSet,
    TaskTagViewSet, TaskActivityLogViewSet, DashboardViewViewSet,
    TaskCommentViewSet, CommentAttachmentViewSet,
    TimeEntryViewSet, TimerSessionViewSet,
    ProjectHealthScoreViewSet, ProjectRiskViewSet, ProjectIssueViewSet,
    TaskAttachmentViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'email-templates', EmailTemplateViewSet, basename='emailtemplate')
router.register(r'email-logs', EmailLogViewSet, basename='emaillog')
router.register(r'email-reminders', EmailReminderViewSet, basename='emailreminder')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notificationpreference')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'task-tags', TaskTagViewSet, basename='tasktag')
router.register(r'task-activity-logs', TaskActivityLogViewSet, basename='taskactivitylog')
router.register(r'dashboard-views', DashboardViewViewSet, basename='dashboardview')
router.register(r'task-comments', TaskCommentViewSet, basename='taskcomment')
router.register(r'comment-attachments', CommentAttachmentViewSet, basename='commentattachment')
router.register(r'time-entries', TimeEntryViewSet, basename='timeentry')
router.register(r'timer-sessions', TimerSessionViewSet, basename='timersession')
router.register(r'project-health-scores', ProjectHealthScoreViewSet, basename='projecthealthscore')
router.register(r'project-risks', ProjectRiskViewSet, basename='projectrisk')
router.register(r'project-issues', ProjectIssueViewSet, basename='projectissue')
router.register(r'task-attachments', TaskAttachmentViewSet, basename='taskattachment')

app_name = 'core_api'

urlpatterns = [
    path('', include(router.urls)),
]

