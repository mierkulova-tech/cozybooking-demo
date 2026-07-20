"""JWT token serialization modules.

This module contains custom serializers extending SimpleJWT functionality
to include user payload data in authentication responses.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customized JWT token obtain pair serializer.

    Extends the default TokenObtainPairSerializer to enrich the token response
    data with user profile details (id, name, email, and role).
    """

    def validate(self, attrs):
        """Validate user credentials and append user details to the token response.

        Args:
            attrs (dict): The input attributes containing user credentials
            (e.g., email and password).

        Returns:
            dict: A dictionary containing the access/refresh tokens and user profile data.
        """
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
