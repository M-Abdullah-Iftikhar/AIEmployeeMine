"""
Serializers for task comments and attachments
"""

from rest_framework import serializers
from core.models import TaskComment, CommentAttachment, Task
from django.contrib.auth.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for comments"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
        read_only_fields = ['id', 'username', 'email', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class CommentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for comment attachments"""
    
    class Meta:
        model = CommentAttachment
        fields = ['id', 'file_name', 'file_path', 'file_size', 'file_type', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments"""
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    attachments = CommentAttachmentSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'task', 'user', 'user_id', 'comment_text', 'parent_comment',
            'is_edited', 'edited_at', 'created_at', 'updated_at',
            'attachments', 'replies', 'replies_count'
        ]
        read_only_fields = ['id', 'is_edited', 'edited_at', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Get nested replies if any"""
        replies = obj.replies.all().order_by('created_at')
        return TaskCommentSerializer(replies, many=True).data
    
    def get_replies_count(self, obj):
        """Get count of replies"""
        return obj.replies.count()
    
    def create(self, validated_data):
        # Get user from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        elif 'user_id' in validated_data:
            validated_data['user'] = User.objects.get(pk=validated_data.pop('user_id'))
        else:
            raise serializers.ValidationError("User must be provided")
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Mark as edited if comment text changed
        if 'comment_text' in validated_data and validated_data['comment_text'] != instance.comment_text:
            validated_data['is_edited'] = True
            from django.utils import timezone
            validated_data['edited_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class TaskCommentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating comments"""
    
    class Meta:
        model = TaskComment
        fields = ['task', 'comment_text', 'parent_comment']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User must be authenticated")
        
        validated_data['user'] = request.user
        return super().create(validated_data)

