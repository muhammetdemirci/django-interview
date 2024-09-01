from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.authentication import UserAuthentication, AdminAuthentication
from authentication.permission import UserAccessPermission
from django.core import serializers

from task.serializers import TaskSerializer
from task.models import Task
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.forms.models import model_to_dict

from celery_tasks import send_task_assignment_notification,send_task_update_notification

class TasksView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (UserAccessPermission,)

    def get(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        return Response(tasks.values(), status=status.HTTP_200_OK)
    
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
            send_task_assignment_notification.delay(request.user.email)
            return Response(model_to_dict(task), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (UserAccessPermission,)

    def get(self, request, id):
        task = Task.objects.get(pk=id, assignee=request.user)
        return Response(model_to_dict(task), status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='title'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='description'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='status'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, description='due_date'),
        }
    ))
    def post(self, request, id):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            title = request.data.get('title', None)
            description = request.data.get('description', None)
            task_status = request.data.get('status', None)
            due_date = request.data.get('due_date', None)
            task = Task.objects.get(pk=id, assignee=request.user)
            task.title = title
            task.description = description
            task.status = task_status
            task.due_date = due_date
            task.save()

            send_task_update_notification.delay(request.user.email)

            return Response(model_to_dict(task), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, id):
        task = Task.objects.get(pk=id, assignee=request.user)
        task.delete()
        return Response("Deleted", status=status.HTTP_200_OK)

class AdminTasksView(APIView):
    authentication_classes = (AdminAuthentication,)
    permission_classes = (UserAccessPermission,)

    def get(self, request):
        tasks = Task.objects.all()

        return Response(tasks.values(), status=status.HTTP_200_OK)

class AdminTaskView(APIView):
    authentication_classes = (AdminAuthentication,)
    permission_classes = (UserAccessPermission,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='title'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='description'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='status'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, description='due_date'),
        }
    ))
    def post(self, request, id):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            title = request.data.get('title', None)
            description = request.data.get('description', None)
            task_status = request.data.get('status', None)
            due_date = request.data.get('due_date', None)
            task = Task.objects.get(pk=id)
            task.title = title
            task.description = description
            task.status = task_status
            task.due_date = due_date
            task.save()
            
            send_task_update_notification.delay(task.user.email)

            return Response(model_to_dict(task), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, id):
        task = Task.objects.get(pk=id)
        task.delete()
        return Response("Deleted", status=status.HTTP_200_OK)
    