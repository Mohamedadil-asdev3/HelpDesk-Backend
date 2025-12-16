# Ticket/tasks.py

import logging
import smtplib

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Ticket.models import CreateTicket
from Authenticate.models import UsersGroup  # Change if your UsersGroup model is in a different app

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to_emails, subject, html_body, cc=None, bcc=None):
    """Reliable SMTP email sender with retry"""
    try:
        cc = cc or []
        bcc = bcc or []
        to_emails = [e for e in to_emails if e]  # Remove empty
        all_recipients = list(set(to_emails + cc + bcc))

        if not all_recipients:
            logger.warning("send_email_task: No valid recipients provided.")
            return

        msg = MIMEMultipart()
        msg["From"] = settings.DEFAULT_FROM_EMAIL
        msg["To"] = ", ".join(to_emails)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30) as server:
            if getattr(settings, "EMAIL_USE_TLS", False):
                server.starttls()
            if getattr(settings, "EMAIL_HOST_USER", None) and getattr(settings, "EMAIL_HOST_PASSWORD", None):
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.DEFAULT_FROM_EMAIL, all_recipients, msg.as_string())

        logger.info(f"Email sent successfully to: {to_emails}")

    except Exception as exc:
        logger.error(f"Email sending failed (will retry): {exc}")
        raise self.retry(exc=exc)


@shared_task
def send_ticket_created_notification(ticket_id):
    """Send notification on ticket creation — supports direct users and full group members"""
    try:
        ticket = CreateTicket.objects.select_related(
            'requested', 'priority', 'department', 'status'
        ).get(id=ticket_id)

        recipients = set()

        # 1. Direct assigned users (assigned_users = list of emails)
        for email in (ticket.assigned_users or []):
            if not email:
                continue
            try:
                user = User.objects.get(email=email, is_active=True)
                recipients.add(user.email)
            except User.DoesNotExist:
                logger.warning(f"Assigned user not found/inactive: {email}")

        # 2. All members from assigned groups
        for group_id in (ticket.assigned_groups or []):
            try:
                group = UsersGroup.objects.get(id=group_id)
                for member in group.get_users():
                    if member.is_active and member.email:
                        recipients.add(member.email)
            except UsersGroup.DoesNotExist:
                logger.warning(f"Assigned group not found: {group_id}")

        # Optional: Notify requester automatically
        # Uncomment if you want the ticket requester to always get a copy
        # if ticket.requested and ticket.requested.is_active and ticket.requested.email:
        #     recipients.add(ticket.requested.email)

        if not recipients:
            logger.info(f"No recipients found for ticket {ticket.ticket_no} (ID: {ticket.id})")
            return

        ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"  # Update domain

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2>New Ticket Assigned: #{ticket.ticket_no}</h2>
            <p>A new helpdesk ticket has been created and assigned to you:</p>
            
            <table style="background:#f9f9f9; border-radius:8px; padding:15px; width:100%; max-width:600px;">
                <tr><td><strong>Ticket No:</strong></td><td><strong>{ticket.ticket_no}</strong></td></tr>
                <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
                <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else 'Normal'}</td></tr>
                <tr><td><strong>Department:</strong></td><td>{ticket.department.field_name if ticket.department else '-'}</td></tr>
                <tr><td><strong>Requested By:</strong></td><td>{getattr(ticket.requested, 'name', ticket.requested.email) if ticket.requested else 'Unknown'}</td></tr>
                <tr><td><strong>Created On:</strong></td><td>{ticket.created_date.strftime('%d %b %Y, %I:%M %p')}</td></tr>
            </table>

            <p style="margin:30px 0;">
                <a href="{ticket_url}" style="background:#0066cc; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold;">
                    View Ticket
                </a>
            </p>

            <hr style="border:none; border-top:1px solid #eee; margin:30px 0;">
            <small>This is an automated notification from Stemz Helpdesk System.</small>
        </body>
        </html>
        """

        subject = f"New Ticket #{ticket.ticket_no}: {ticket.title[:60]}..."

        send_email_task.delay(
            to_emails=list(recipients),
            subject=subject,
            html_body=html_body
        )

        logger.info(
            f"Notification queued for ticket {ticket.ticket_no} (ID: {ticket.id}) → "
            f"{len(recipients)} recipients: {sorted(recipients)}"
        )

    except CreateTicket.DoesNotExist:
        logger.error(f"Ticket ID {ticket_id} does not exist.")
    except Exception as e:
        logger.error(f"Error in send_ticket_created_notification({ticket_id}): {e}", exc_info=True)
# # Ticket/tasks.py

# import logging
# from celery import shared_task
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.template.loader import render_to_string
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from django.utils.html import strip_tags

# from Ticket.models import CreateTicket
# # Ticket/tasks.py
# import smtplib
# from celery import shared_task
# from django.conf import settings
# from django.utils import timezone
# from django.db import transaction
# from datetime import timedelta, datetime
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from django.template import Template, Context
# from django.contrib.auth import get_user_model
# from Ticket.models import CreateTicket, TicketSLA, TicketApprovalLog, TicketEmailTemplate,TicketsMasterConfiguration
# from Ticket.models import Holiday
# from django.db import connection
# from django.conf import settings
# import django
 
# print("=== CELERY DEBUG CHECK ===")
# print("DJANGO VERSION:", django.get_version())
# print("DB SETTINGS:", settings.DATABASES['default'])
 
# cursor = connection.cursor()
# cursor.execute("SELECT DATABASE()")
# print("CURRENT DATABASE():", cursor.fetchone())
 
# cursor.execute("SHOW COLUMNS FROM tickets_createtickets LIKE 'watcher_group_id'")
# print("WATCHER COLUMN SEEN BY CELERY:", cursor.fetchall())
# print("===========================")
 
# User = get_user_model()
# logger = logging.getLogger(__name__)


# @shared_task(bind=True, max_retries=3)
# def send_email_task(self, to_emails, subject, html_body, cc=None, bcc=None):
#     """Your existing working SMTP email task — keep it as-is (just improved logging)"""
#     try:
#         cc = cc or []
#         bcc = bcc or []
#         all_recipients = list(set(to_emails + cc + bcc))

#         if not all_recipients:
#             logger.warning("No recipients for email.")
#             return

#         from email.mime.multipart import MIMEMultipart
#         from email.mime.text import MIMEText
#         import smtplib

#         msg = MIMEMultipart()
#         msg["From"] = settings.DEFAULT_FROM_EMAIL
#         msg["To"] = ", ".join(to_emails)
#         if cc:
#             msg["Cc"] = ", ".join(cc)
#         msg["Subject"] = subject
#         msg.attach(MIMEText(html_body, "html"))

#         with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#             if getattr(settings, "EMAIL_USE_TLS", False):
#                 server.starttls()
#             if settings.DEFAULT_FROM_EMAIL and settings.EMAIL_HOST_PASSWORD:
#                 server.login(settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_PASSWORD)
#             server.sendmail(settings.DEFAULT_FROM_EMAIL, all_recipients, msg.as_string())

#         logger.info(f"Email sent successfully to: {to_emails}")

#     except Exception as exc:
#         logger.error(f"Email failed: {exc}")
#         raise self.retry(exc=exc, countdown=60)


# # ================================================
# # MAIN TASK: Send on Ticket Creation
# # ================================================
# # @shared_task
# # def send_ticket_created_notification(ticket_id):
# #     try:
# #         ticket = CreateTicket.objects.select_related('requested', 'priority', 'department').get(id=ticket_id)

# #         recipients = set()

# #         # Determine recipients
# #         if ticket.assignee and ticket.assignee.startswith('group:'):
# #             # Group assignment → send to all watchers
# #             for watcher in ticket.watchers.all():
# #                 if watcher.email and watcher.is_active:
# #                     recipients.add(watcher.email)
# #         elif ticket.assignee:
# #             # Direct user assignment
# #             try:
# #                 user = User.objects.get(email=ticket.assignee, is_active=True)
# #                 if user.email:
# #                     recipients.add(user.email)
# #             except User.DoesNotExist:
# #                 logger.warning(f"Assignee {ticket.assignee} not found in users.")

# #         if not recipients:
# #             logger.info(f"No valid email recipients for ticket {ticket.ticket_no}")
# #             return

# #         # Build ticket URL (adjust to your frontend)
# #         ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

# #         # Render email (you can use a template file or inline HTML)
# #         html_body = f"""
# #         <html>
# #         <body style="font-family: Arial, sans-serif; color: #333;">
# #             <h2>New Ticket Assigned</h2>
# #             <p>A new helpdesk ticket has been created and assigned to you:</p>
            
# #             <table border="0" cellpadding="8" cellspacing="0" style="background:#f9f9f9; border-radius:8px;">
# #                 <tr><td><strong>Ticket No:</strong></td><td><strong>{ticket.ticket_no}</strong></td></tr>
# #                 <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
# #                 <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else 'Normal'}</td></tr>
# #                 <tr><td><strong>Requested By:</strong></td><td>{ticket.requested.firstname or ticket.requested.email}</td></tr>
# #                 <tr><td><strong>Created On:</strong></td><td>{ticket.created_date.strftime('%d %b %Y, %I:%M %p')}</td></tr>
# #             </table>

# #             <p style="margin:20px 0;">
# #                 <a href="{ticket_url}" style="background:#0066cc; color:white; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold;">
# #                     View Ticket
# #                 </a>
# #             </p>

# #             <hr>
# #             <small>This is an automated notification from Stemz Helpdesk System.</small>
# #         </body>
# #         </html>
# #         """

# #         subject = f"New Ticket #{ticket.ticket_no}: {ticket.title[:50]}..."

# #         # Send via your working task
# #         send_email_task.delay(
# #             to_emails=list(recipients),
# #             subject=subject,
# #             html_body=html_body
# #         )

# #         logger.info(f"Notification queued for ticket {ticket.ticket_no} → {len(recipients)} recipients")

# #     except CreateTicket.DoesNotExist:
# #         logger.error(f"Ticket {ticket_id} not found")
# #     except Exception as e:
# #         logger.error(f"Error in send_ticket_created_notification: {e}", exc_info=True)
# @shared_task
# def send_ticket_created_notification(ticket_id):
#     try:
#         ticket = CreateTicket.objects.select_related(
#             'requested', 'priority', 'department', 'status'
#         ).get(id=ticket_id)

#         recipients = set()

#         # === NEW LOGIC: Use assigned_users and assigned_groups ===
#         assigned_emails = ticket.assigned_users or []
#         assigned_group_ids = ticket.assigned_groups or []

#         # 1. Add direct user assignees
#         for email in assigned_emails:
#             try:
#                 user = User.objects.get(email=email, is_active=True)
#                 if user.email:
#                     recipients.add(user.email)
#             except User.DoesNotExist:
#                 logger.warning(f"Assigned user email {email} does not exist or is inactive.")

#         # 2. Add all members of assigned groups
#         for group_id in assigned_group_ids:
#             try:
#                 group = UsersGroup.objects.get(id=group_id)
#                 for member in group.get_users():
#                     if member.is_active and member.email:
#                         recipients.add(member.email)
#             except UsersGroup.DoesNotExist:
#                 logger.warning(f"Assigned group {group_id} does not exist.")

#         # Optional: Always notify the requester?
#         # if ticket.requested and ticket.requested.is_active and ticket.requested.email:
#         #     recipients.add(ticket.requested.email)

#         if not recipients:
#             logger.info(f"No valid email recipients for ticket {ticket.ticket_no}")
#             return

#         # Build ticket URL
#         ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#         # Email body (same as before)
#         html_body = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333;">
#             <h2>New Ticket Assigned</h2>
#             <p>A new helpdesk ticket has been created and assigned to you:</p>
            
#             <table border="0" cellpadding="8" cellspacing="0" style="background:#f9f9f9; border-radius:8px;">
#                 <tr><td><strong>Ticket No:</strong></td><td><strong>{ticket.ticket_no}</strong></td></tr>
#                 <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
#                 <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else 'Normal'}</td></tr>
#                 <tr><td><strong>Requested By:</strong></td><td>{getattr(ticket.requested, 'name', None) or ticket.requested.email if ticket.requested else 'Unknown'}</td></tr>
#                 <tr><td><strong>Created On:</strong></td><td>{ticket.created_date.strftime('%d %b %Y, %I:%M %p')}</td></tr>
#             </table>

#             <p style="margin:20px 0;">
#                 <a href="{ticket_url}" style="background:#0066cc; color:white; padding:12px 24px; text-decoration:none; border-radius:5px; font-weight:bold;">
#                     View Ticket
#                 </a>
#             </p>

#             <hr>
#             <small>This is an automated notification from Stemz Helpdesk System.</small>
#         </body>
#         </html>
#         """

#         subject = f"New Ticket #{ticket.ticket_no}: {ticket.title[:50]}..."

#         send_email_task.delay(
#             to_emails=list(recipients),
#             subject=subject,
#             html_body=html_body
#         )

#         logger.info(f"Notification queued for ticket {ticket.ticket_no} → {len(recipients)} recipients: {recipients}")

#     except CreateTicket.DoesNotExist:
#         logger.error(f"Ticket {ticket_id} not found")
#     except Exception as e:
#         logger.error(f"Error in send_ticket_created_notification: {e}", exc_info=True)