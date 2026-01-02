"""
Django REST Framework serializers for Project Manager Agent features
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    EmailTemplate, EmailLog, EmailReminder,
    NotificationPreference, Notification,
    TaskTag, TaskActivityLog, DashboardView,
    TaskComment, CommentAttachment,
    TimeEntry, TimerSession,
    ProjectHealthScore, ProjectRisk, ProjectIssue,
    TaskAttachment, Task, Project, ProjectMilestone, Meeting
)


# Email & Communication Serializers
class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EmailLogSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = '__all__'
        read_only_fields = ('sent_at',)


class EmailReminderSerializer(serializers.ModelSerializer):
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    milestone_title = serializers.CharField(source='milestone.title', read_only=True)
    meeting_title = serializers.CharField(source='meeting.title', read_only=True)
    
    class Meta:
        model = EmailReminder
        fields = '__all__'
        read_only_fields = ('created_at', 'sent_at')


# Notification Serializers
class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at', 'read_at')


# Task Monitoring Serializers
class TaskTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskTag
        fields = '__all__'
        read_only_fields = ('created_at',)


class TaskActivityLogSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskActivityLog
        fields = '__all__'
        read_only_fields = ('created_at',)


class DashboardViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardView
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Task Comments Serializers
class CommentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentAttachment
        fields = '__all__'
        read_only_fields = ('created_at',)


class TaskCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    attachments = CommentAttachmentSerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'edited_at')
    
    def get_replies_count(self, obj):
        return obj.replies.count()


# Time Tracking Serializers
class TimeEntrySerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'approved_at')


class TimerSessionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TimerSession
        fields = '__all__'
        read_only_fields = ('started_at', 'ended_at')


# Project Health & Risk Serializers
class ProjectHealthScoreSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectHealthScore
        fields = '__all__'
        read_only_fields = ('calculated_at',)


class ProjectRiskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    identified_by_username = serializers.CharField(source='identified_by.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = ProjectRisk
        fields = '__all__'
        read_only_fields = ('identified_at', 'updated_at', 'resolved_at')


class ProjectIssueSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = ProjectIssue
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'resolved_at')


# Task Attachment Serializer
class TaskAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = '__all__'
        read_only_fields = ('created_at',)


# Simplified serializers for nested/related objects
class SimpleTaskSerializer(serializers.ModelSerializer):
    """Simplified task serializer for nested representations"""
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    tags = TaskTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'priority', 'due_date', 'assignee_username', 'tags', 'progress_percentage')


class SimpleProjectSerializer(serializers.ModelSerializer):
    """Simplified project serializer for nested representations"""
    class Meta:
        model = Project
        fields = ('id', 'name', 'status', 'priority')

