from django.db import models

# Create your models here.
# models.py (New Standalone TicketPanel Model - No Foreign Keys)
from django.db import models

class TicketPanel(models.Model):
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    location = models.CharField(max_length=100, blank=True, null=True)   # Changed to CharField
    role = models.CharField(max_length=100, blank=True, null=True)
    imageupload = models.ImageField(upload_to='ticket_images/', null=True, blank=True)
    message = models.TextField()
    paneltype = models.CharField(max_length=50)
    raw_payload = models.JSONField(null=True, blank=True, default=dict)  # Built-in JSONField for MySQL
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "create_ticket_panel"
        ordering = ['-created_date']