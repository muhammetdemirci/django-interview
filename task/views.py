from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.authentication import UserAuthentication
from authentication.permission import UserAccessPermission
from django.core import serializers

from task.serializers import TaskSerializer
from task.models import Task
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.forms.models import model_to_dict

class TasksView(APIView):
    """
        GET /api/tasks/
    """

    authentication_classes = (UserAuthentication,)
    permission_classes = (UserAccessPermission,)

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        qs_json = serializers.serialize('json', tasks)

        return Response(qs_json, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='title'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='description'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='status'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, description='due_date'),
        }
    ))
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            title = request.data.get('title', None)
            description = request.data.get('description', None)
            task_status = request.data.get('status', None)
            due_date = request.data.get('due_date', None)
            
            task = Task.objects.create(title=title,description=description, status=task_status, assignee=request.user, due_date=due_date)
            return Response(model_to_dict(task), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
