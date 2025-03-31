from rest_framework import views
from utils.responses import CustomResponse
from pymongo_wrapper.model import Query
from .serializers import QueriesSerializer


class QueriesView(views.APIView):
    def get(self, request):
        serializer = QueriesSerializer(Query.find(), many=True)
        # print('serializer: ', serializer.data)
        print('result: ', (list(Query.find())))
        try:
            return CustomResponse.successful_200(serializer.data)
        except Exception as e:
            print('e: ', str(e))
            return CustomResponse.successful_200('')
