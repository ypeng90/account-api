from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy
from uuid import uuid4


# Create your models here.
class MyUser(AbstractUser):
    email = models.EmailField(gettext_lazy("email address"))
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
