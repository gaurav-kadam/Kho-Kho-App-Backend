from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework import status
from django.core.exceptions import ValidationError



class OfficialListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get("role")

        if role:
            officials = User.objects.filter(role=role)
        else:
            officials = User.objects.filter(
                role__in=["REFEREE", "SCORER", "UMPIRE", "ADMIN"]
            )

        data = [
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}",
                "role": user.role
            }
            for user in officials
        ]

        return Response(data, status=status.HTTP_200_OK)


class CreateOfficialAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only ADMIN can create official
        if request.user.role != "ADMIN":
            return Response(
                {"error": "Only admin can create officials"},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data

        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "gender",
            "state",
            "city",
            "role",
        ]

        # Validate required fields
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Check duplicate email
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"error": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate role
        allowed_roles = ["REFEREE", "UMPIRE", "SCORER", "ADMIN"]
        if data["role"] not in allowed_roles:
            return Response(
                {"error": "Invalid role"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user
        user = User.objects.create(
            username=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            gender=data["gender"],
            state=data["state"],
            city=data["city"],
            role=data["role"],
        )

        user.set_password("123456")  # temporary password
        user.save()

        return Response(
            {"message": "Official created successfully"},
            status=status.HTTP_201_CREATED
        )
