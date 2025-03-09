from django.contrib.auth import authenticate
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserSerializer, UserLoginSerializer, UserSignupSerializerRequest, \
    UserLoginSerializerRequest, UserUpdateSerializer
from drf_spectacular.utils import extend_schema
from .models import User
from django.utils.timezone import now
from utils.responses import CustomResponse
import time


class LoginView(APIView):
    serializer_class = UserLoginSerializerRequest
    authentication_classes = []

    @extend_schema(
        request=UserLoginSerializerRequest
    )
    def post(self, request):
        request_serializer = UserLoginSerializerRequest(data=request.data)
        if not request_serializer.is_valid():
            return CustomResponse.bad_request(request_serializer.errors)
        username = request_serializer.validated_data.get('email', None)
        password = request_serializer.validated_data.get('password', None)
        start_time = time.time()
        authenticated_user = authenticate(username=username, password=password)
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        start_time = time.time()
        if authenticated_user:
            start_time = time.time()
            authenticated_user.last_login = now()
            authenticated_user.save(update_fields=['last_login'])
            serializer = UserLoginSerializer(authenticated_user)
            end_time = time.time()
            print(f"Query executed in {end_time - start_time:.4f} seconds")
            return CustomResponse.successful_200(
                result=serializer.data,
                message='you logged in successfully')
        end_time = time.time()
        print(f"Query executed in {end_time - start_time:.4f} seconds")
        return CustomResponse.unauthenticated('Wrong Credentials')


class SignUpView(APIView):
    serializer_class = UserSignupSerializerRequest
    authentication_classes = []

    @extend_schema(
        request=UserSignupSerializerRequest
    )
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return CustomResponse.successful_201(
                    result=serializer.data,
                    message='Successfully Signed Up'
                )
            elif serializer.errors is not None and serializer.errors.get('phone_number') is not None and serializer.errors.get('phone_number')[0] is not None and str(serializer.errors.get('phone_number')[0]) == 'user with this phone number already exists.':
                return CustomResponse.bad_request('You are already registered.')
            return CustomResponse.bad_request("Bad Request")
        except Exception as e:
            return CustomResponse.bad_request(str(e))


class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            response = super().update(request, *args, **kwargs)
            if not self.get_object().id:
                return CustomResponse.have_gone("User has been deleted.")
            return response
        except User.DoesNotExist:
            return CustomResponse.have_gone("User has been deleted.")


class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']

    def get_object(self):
        return self.request.user
