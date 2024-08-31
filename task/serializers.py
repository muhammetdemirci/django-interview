from rest_framework import serializers

from task.models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'due_date')

    def create(self, validated_data):
        task = Task(**validated_data)
        task.save()
        return task

