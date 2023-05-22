from celery import Celery
import os


class MyCelery(Celery):

    # change automatic naming
    # moduleA.tasks.taskA -> moduleA.taskA
    # cause KeyError ?
    def gen_task_name(self, name, module):
        # if module.endswith(".tasks"):
        #     module = module[:-6]
        return super().gen_task_name(name, module)


# Set default Django settings module for celery. Put
# before creating the app instances.
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "account.settings"
)

app = MyCelery(__name__)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Setup optional configurations.
# app.conf.update(
#     result_expires=3600,
# )

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Dumps request information.
# @app.task(bind=True)
# def debug_task(self):
#     print(f"Request: {self.request!r}")
