from django.shortcuts import render
from .serializers import CreateUserSerializer
# Create your views here.


# @api_view(['POST', ])
# @permission_classes([permissions.AllowAny, ])
# def signup(request):
#     serializer = CreateUserSerializer(data=request.data)
#     try:
#         user = User.objects.get(username=request.data.get('username', ''))
#         if user.email == request.data.get('email', ''):
#             send_confirmation_code(user)
#             return Response(serializer.initial_data, status=status.HTTP_200_OK)
#         return Response('username & email pair doesn\'t match',
#                         status=status.HTTP_400_BAD_REQUEST)
#     except User.DoesNotExist:
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         send_confirmation_code(user)
#     return Response(serializer.validated_data, status=status.HTTP_200_OK)