from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
import json
from pymongo import MongoClient
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from rest_framework_simplejwt.tokens import (
    RefreshToken,
    api_settings,
    datetime_from_epoch,
    TokenError,
)
from .events import ESClient


class MyRefreshToken(RefreshToken):
    def check_blacklist(self):
        """
        Checks if this token is present in the token blacklist.  Raises
        `TokenError` if so.
        """
        jti = self.payload[api_settings.JTI_CLAIM]

        # This is used in relational DB to support join.
        # if BlacklistedToken.objects.filter(token__jti=jti).exists():
        #     raise TokenError(_("Token is blacklisted"))
        # This is used in MongoDB to avoid join.
        client = MongoClient(
            host=settings.MONGO_HOST,
            port=int(settings.MONGO_PORT),
            username=settings.MONGO_USERNAME,
            password=settings.MONGO_PASSWORD,
            replicaSet=settings.MONGO_RSNAME,
        )
        db = client[settings.MONGO_DATABASE]
        token = db["token_blacklist_blacklistedtoken"].find_one({"jti": jti})
        client.close()

        if token:
            raise TokenError(_("Token is blacklisted"))

    def blacklist(self):
        """
        Ensures this token is included in the outstanding token list and
        adds it to the blacklist.
        """
        jti = self.payload[api_settings.JTI_CLAIM]
        exp = self.payload["exp"]

        # Use transaction to ensure atomicity of token blacklisting and event sending.
        with transaction.atomic():
            # Ensure outstanding token exists with given jti
            token, _ = OutstandingToken.objects.get_or_create(
                jti=jti,
                defaults={
                    "token": str(self),
                    "expires_at": datetime_from_epoch(exp),
                },
            )
            object, created = BlacklistedToken.objects.get_or_create(token=token)
            data = json.dumps(
                {
                    "id": object.id,
                    "blacklisted_at": object.blacklisted_at.isoformat(),
                    "token_id": object.token_id,
                    "jti": jti,
                }
            )
            client = ESClient(
                "token",
                "TokenBlacklisted",
                data,
            )
            client.send()
            client.close()

        return object, created
