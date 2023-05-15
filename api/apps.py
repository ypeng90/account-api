from django.apps import AppConfig
import os


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Django starts two processes at the same time, one for the server
        # and the other for reloading on changes. We only want to subscribe
        # once.
        if os.environ.get("RUN_MAIN"):
            from .events import subscribe_events

            subscribe_events()
