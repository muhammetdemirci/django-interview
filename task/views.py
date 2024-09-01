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

   
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Title",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'description',
                openapi.IN_QUERY,
                description="Description",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'task_status',
                openapi.IN_QUERY,
                description="Task Status, Options are PG, IG, CD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'assignee_id',
                openapi.IN_QUERY,
                description="Assignee Id",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                'due_date',
                openapi.IN_QUERY,
                description="Due date, format must be YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                },)
            ),
        }
    )
    def get(self, request):
        title = request.GET.get('title', '')
        description = request.GET.get('description', '')
        task_status = request.GET.get('task_status', '')
        assignee_id = request.GET.get('assignee_id', None)
        due_date = request.GET.get('due_date', None)
        tasks = Task.objects.all()
        if title:
            tasks = tasks.filter(title__icontains=title)
        if description:
            tasks = tasks.filter(description__icontains=description)
        if task_status:
            tasks = tasks.filter(status=task_status)
        if assignee_id:
            tasks = tasks.filter(assignee=assignee_id)
        if due_date:
            tasks = tasks.filter(due_date=due_date)
        return Response(tasks.values(), status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT, 
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='title'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='description'),
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='status'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, description='due_date'),
        },
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
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

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
        }
    )
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
    ), responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
        })
    def patch(self, request, id):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            title = request.data.get('title', None)
            description = request.data.get('description', None)
            task_status = request.data.get('status', None)
            due_date = request.data.get('due_date', None)
            task = Task.objects.get(pk=id, assignee=request.user)
            if (title):
                task.title = title
            if (description):
                task.description = description
            if (task_status):
                task.status = task_status
            if (due_date):
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Title",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'description',
                openapi.IN_QUERY,
                description="Description",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'task_status',
                openapi.IN_QUERY,
                description="Task Status, Options are PG, IG, CD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'assignee_id',
                openapi.IN_QUERY,
                description="Assignee Id",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                'due_date',
                openapi.IN_QUERY,
                description="Due date, format must be YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                },)
            ),
        }
    )
    def get(self, request):
        title = request.GET.get('title', '')
        description = request.GET.get('description', '')
        task_status = request.GET.get('task_status', '')
        assignee_id = request.GET.get('assignee_id', None)
        due_date = request.GET.get('due_date', None)
        tasks = Task.objects.all()
        if title:
            tasks = tasks.filter(title__icontains=title)
        if description:
            tasks = tasks.filter(description__icontains=description)
        if task_status:
            tasks = tasks.filter(status=task_status)
        if assignee_id:
            tasks = tasks.filter(assignee=assignee_id)
        if due_date:
            tasks = tasks.filter(due_date=due_date)
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
    ), responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={
                    "id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "task_status": openapi.Schema(type=openapi.TYPE_STRING),
                    "assignee_id": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "due_date": openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
    })
    def patch(self, request, id):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            title = request.data.get('title', None)
            description = request.data.get('description', None)
            task_status = request.data.get('status', None)
            due_date = request.data.get('due_date', None)
            task = Task.objects.get(pk=id)
            if (title):
                task.title = title
            if (description):
                task.description = description
            if (task_status):
                task.status = task_status
            if (due_date):
                task.due_date = due_date
            task.save()
            
            send_task_update_notification.delay(task.user.email)

            return Response(model_to_dict(task), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, id):
        task = Task.objects.get(pk=id)
        task.delete()
        return Response("Deleted", status=status.HTTP_200_OK)
    