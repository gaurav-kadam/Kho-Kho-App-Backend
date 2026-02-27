from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import LoginPass


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    userid = request.data.get('username')
    password = request.data.get('password')

    try:
        user = LoginPass.objects.get(userid=userid, password=password)

        return Response({
            "userid": user.userid,
            "role": user.role
        })

    except LoginPass.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )