# from django.apps import AppConfig


# class TicketConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'Ticket'
from django.apps import AppConfig


class TicketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ticket'

    def ready(self):
        # Import Celery tasks only when Django apps are fully loaded
        import Ticket.tasks  # noqa
