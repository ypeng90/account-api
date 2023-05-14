from django.apps import AppConfig
import os
import pickle
from threading import Thread


def subscribe_events():
    from .events import ESClient

    def catch_up_user_events():
        client = ESClient("user")
        for event in client.subscribe(2):
            print(event.type)
            print(pickle.loads(event.data))

    # TODO: Implement this function
    # def catch_up_token_events():
    #     while True:
    #         print("Hello from token events")
    #         time.sleep(60)

    # Daemon=True to terminate the threads when the main process terminates.
    # No joinning the threads so that the caller function subscribe_events
    # can finish and thus function ready can finish to let the server do the
    # work.
    thread_user = Thread(target=catch_up_user_events, daemon=True)
    thread_user.start()
    # thread_token = Thread(target=catch_up_token_events, daemon=True)
    # thread_token.start()


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Django starts two processes at the same time, one for the server
        # and the other for reloading on changes. We only want to subscribe
        # once.
        if os.environ.get("RUN_MAIN"):
            subscribe_events()
