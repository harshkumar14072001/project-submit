from django.contrib.auth import get_user_model,login,logout,authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
import uuid
from .serializers import UserSerializer, FileSerializer
import os
from rest_framework.parsers import FileUploadParser
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], parser_classes=[FileUploadParser])
    def upload_file(self, request):
        user = self.request.user
        if not user.is_authenticated or not user.is_ops_user:
            return JsonResponse({"error": "Permission denied"}, status=403)

        uploaded_file = request.data['file']
        file_extension = os.path.splitext(uploaded_file.name)[1]
        allowed_extensions = ['.pptx', '.docx', '.xlsx']

        if file_extension not in allowed_extensions:
            return JsonResponse({"error": "Invalid file type"}, status=400)

        file = File(owner=user, file=uploaded_file)
        file.save()

        encrypted_url = str(uuid.uuid4())
        permission = FilePermission(file=file, user=user, encrypted_url=encrypted_url)
        permission.save()

        return JsonResponse({"message": "File uploaded successfully", "encrypted_url": encrypted_url})

    @action(detail=False, methods=['get'])
    def list_files(self, request):
        user = self.request.user
        files = File.objects.filter(owner=user)
        file_list = [{'file_name': file.file.name, 'encrypted_url': file.filepermission_set.first().encrypted_url} for file in files]
        return JsonResponse({"files": file_list})

    @action(detail=True, methods=['get'])
    def download_file(self, request, pk=None):
        user = self.request.user
        file_permission = FilePermission.objects.filter(user=user, encrypted_url=pk).first()
        if not file_permission:
            raise PermissionDenied

        file_path = file_permission.file.file.path
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response

        return JsonResponse({"error": "File not found"}, status=404)


