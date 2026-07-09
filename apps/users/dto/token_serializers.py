from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "name": self.user.name,
                    "email": self.user.email,
                    "role": self.user.role,
                }
            }
        )
        return data
