from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class StatelessTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff

        return token
