from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status


class CustomResponse:
    @staticmethod
    def not_found(message):
        return Response({'detail': message}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def bad_request(detail=None):
        return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def unauthenticated(detail=None):
        return Response({'detail': detail}, status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def successful_200(result=None, message=None):
        return Response({'result': result, 'detail': message}, status=status.HTTP_200_OK)

    @staticmethod
    def successful_201(result=None, message=None):
        return Response({'result': result, 'detail': message}, status=status.HTTP_201_CREATED)

    @staticmethod
    def successful_202(result=None, message=None):
        return Response({'result': result, 'detail': message}, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def successful_204_no_content():
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def server_error(message):
        return Response({'detail': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def have_gone(message):
        return Response({'detail': message}, status=status.HTTP_410_GONE)

    @staticmethod
    def json_response(data):
        return JsonResponse(data)
