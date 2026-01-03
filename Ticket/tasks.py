# import logging
# import smtplib
# import base64
# from cryptography.fernet import Fernet

# from celery import shared_task
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# from Ticket.models import CreateTicket, Message
# from Authenticate.models import UsersGroup

# User = get_user_model()
# logger = logging.getLogger(__name__)


# # =====================================================
# # UTILITIES
# # =====================================================
# def format_ist(dt):
#     if not dt:
#         return "-"
#     return timezone.localtime(dt).strftime("%d %b %Y, %I:%M %p")


# def decrypt_message_for_email(msg):
#     """
#     Decrypt protected message for email usage
#     """
#     if not msg.protected:
#         return msg.message

#     if not msg.message.startswith("ENCRYPTED:"):
#         return msg.message

#     try:
#         receiver_id = str(msg.receiver_id)
#         key_material = (settings.SECRET_KEY.encode() + receiver_id.encode()).ljust(32, b"0")[:32]
#         key = base64.urlsafe_b64encode(key_material)
#         fernet = Fernet(key)
#         return fernet.decrypt(msg.message.replace("ENCRYPTED:", "").encode()).decode()
#     except Exception:
#         return "[Unable to decrypt message]"


# # =====================================================
# # HTML BUILDERS
# # =====================================================
# def build_ticket_table(ticket, message_section=""):
#     return f"""
#     <table style="width:100%;border-collapse:collapse;font-size:14px;">
#         <tr><td><strong>Ticket No</strong></td><td>{ticket.ticket_no}</td></tr>
#         <tr><td><strong>Title</strong></td><td>{ticket.title}</td></tr>
#         <tr><td><strong>Status</strong></td><td>{ticket.status.field_name if ticket.status else '-'}</td></tr>
#         <tr><td><strong>Priority</strong></td><td>{ticket.priority.field_name if ticket.priority else '-'}</td></tr>
#         <tr><td><strong>Department</strong></td><td>{ticket.department.field_name if ticket.department else '-'}</td></tr>
#         <tr><td><strong>Location</strong></td><td>{ticket.location.field_name if ticket.location else '-'}</td></tr>
#         <tr><td><strong>Requested By</strong></td>
#             <td>{ticket.requested.firstname if ticket.requested else '-'}</td></tr>
#         <tr><td><strong>Created On</strong></td><td>{format_ist(ticket.created_date)}</td></tr>
#         {message_section}
#     </table>
#     """


# def wrap_html(title, subtitle, table_html, ticket_url):
#     return f"""
#     <html>
#     <body style="font-family:Segoe UI,Arial;background:#f3f4f6;padding:20px;">
#         <div style="max-width:720px;margin:auto;background:#ffffff;
#             border-radius:12px;padding:25px;">

#             <h2 style="color:#1f2937;">{title}</h2>
#             <p style="color:#4b5563;">{subtitle}</p>

#             {table_html}

#             <div style="margin-top:30px;text-align:center;">
#                 <a href="{ticket_url}" style="
#                     background:#2563eb;
#                     color:white;
#                     padding:12px 28px;
#                     border-radius:6px;
#                     text-decoration:none;
#                     font-weight:600;
#                 ">View Ticket</a>
#             </div>

#             <hr style="margin:30px 0;">
#             <small style="color:#6b7280;">
#                 This is an automated notification from Stemz Helpdesk System.
#             </small>
#         </div>
#     </body>
#     </html>
#     """


# # =====================================================
# # EMAIL SENDER
# # =====================================================
# @shared_task(bind=True, max_retries=3, default_retry_delay=60)
# def send_email_task(self, to_emails, subject, html_body):
#     try:
#         to_emails = list(set(filter(None, to_emails)))
#         if not to_emails:
#             return

#         msg = MIMEMultipart()
#         msg["From"] = settings.DEFAULT_FROM_EMAIL
#         msg["To"] = ", ".join(to_emails)
#         msg["Subject"] = subject
#         msg.attach(MIMEText(html_body, "html"))

#         with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#             if settings.EMAIL_USE_TLS:
#                 server.starttls()
#             if settings.EMAIL_HOST_USER:
#                 server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#             server.sendmail(settings.DEFAULT_FROM_EMAIL, to_emails, msg.as_string())

#         logger.info(f"Email sent to {to_emails}")

#     except Exception as exc:
#         raise self.retry(exc=exc)


# # =====================================================
# # TICKET CREATED
# # =====================================================
# @shared_task
# def send_ticket_created_notification(ticket_id):
#     ticket = CreateTicket.objects.select_related(
#         "requested", "priority", "department", "status", "location"
#     ).get(id=ticket_id)

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # ---------- REQUESTER ----------
#     if ticket.requested and ticket.requested.email:
#         html_body = wrap_html(
#             f"Ticket Created: #{ticket.ticket_no}",
#             "Your ticket has been created successfully.",
#             build_ticket_table(ticket),
#             ticket_url
#         )

#         send_email_task.delay(
#             [ticket.requested.email],
#             f"Ticket Created - #{ticket.ticket_no}",
#             html_body
#         )

#     # ---------- ASSIGNEES ----------
#     recipients = set()

#     for email in (ticket.assigned_users or []):
#         try:
#             user = User.objects.get(email=email, is_active=True)
#             recipients.add(user.email)
#         except User.DoesNotExist:
#             pass

#     for group_id in (ticket.assigned_groups or []):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             for member in group.get_users():
#                 if member.is_active and member.email:
#                     recipients.add(member.email)
#         except UsersGroup.DoesNotExist:
#             pass

#     if recipients:
#         html_body = wrap_html(
#             f"New Ticket Assigned: #{ticket.ticket_no}",
#             "A new ticket has been assigned to you.",
#             build_ticket_table(ticket),
#             ticket_url
#         )

#         send_email_task.delay(
#             list(recipients),
#             f"New Ticket Assigned - #{ticket.ticket_no}",
#             html_body
#         )


# # =====================================================
# # STATUS CHANGE (CLARIFICATION)
# # =====================================================
# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     ticket = CreateTicket.objects.select_related(
#         "requested", "priority", "department", "status", "location"
#     ).get(id=ticket_id)

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # ==================================================
#     # ALWAYS GET LATEST MESSAGE (FIX)
#     # ==================================================
#     msg = (
#         Message.objects
#         .filter(ticket_no_id=ticket.id)
#         .order_by("-createdon")
#         .first()
#     )

#     clarification_text = ""
#     if msg:
#         clarification_text = decrypt_message_for_email(msg)

#     message_section = ""
#     if clarification_text:
#         message_section = f"""
#         <tr>
#             <td colspan="2" style="padding-top:16px;">
#                 <strong>Message</strong>
#                 <div style="
#                     margin-top:8px;
#                     padding:14px;
#                     background:#fffbeb;
#                     border-left:5px solid #f59e0b;
#                     white-space:pre-line;
#                     border-radius:6px;
#                 ">
#                     {clarification_text}
#                 </div>
#             </td>
#         </tr>
#         """

#     table_html = build_ticket_table(ticket, message_section)

#     # ==================================================
#     # CLARIFICATION REQUIRED → REQUESTER
#     # ==================================================
#     if notify_type == "clarification_required":
#         if ticket.requested and ticket.requested.email:
#             html_body = wrap_html(
#                 f"Clarification Required: #{ticket.ticket_no}",
#                 "Please provide the requested clarification.",
#                 table_html,
#                 ticket_url
#             )

#             send_email_task.delay(
#                 [ticket.requested.email],
#                 f"Clarification Required - Ticket #{ticket.ticket_no}",
#                 html_body
#             )

#     # ==================================================
#     # CLARIFICATION SUPPLIED → ASSIGNEES
#     # ==================================================
#     elif notify_type == "clarification_supplied":
#         recipients = set()

#         for email in (ticket.assigned_users or []):
#             try:
#                 user = User.objects.get(email=email, is_active=True)
#                 recipients.add(user.email)
#             except User.DoesNotExist:
#                 pass

#         for group_id in (ticket.assigned_groups or []):
#             try:
#                 group = UsersGroup.objects.get(id=group_id)
#                 for member in group.get_users():
#                     if member.is_active and member.email:
#                         recipients.add(member.email)
#             except UsersGroup.DoesNotExist:
#                 pass

#         if recipients:
#             html_body = wrap_html(
#                 f"Clarification Provided: #{ticket.ticket_no}",
#                 "The requester has provided clarification.",
#                 table_html,
#                 ticket_url
#             )

#             send_email_task.delay(
#                 list(recipients),
#                 f"Clarification Provided - Ticket #{ticket.ticket_no}",
#                 html_body
#             )
# =============================================
# Ticket Tasks - Email Notifications
# =============================================
# Ticket/tasks.py

import logging
import base64
from cryptography.fernet import Fernet

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from Ticket.models import CreateTicket, Message
from Authenticate.models import UsersGroup

SECRET_KEY = getattr(settings, 'ENCRYPTION_SECRET', b'default_secret_key_change_me_32_bytes_long!!')
User = get_user_model()
logger = logging.getLogger(__name__)


# -------------------------------------------------
# Utilities
# -------------------------------------------------
def format_ist(dt):
    """Format datetime in IST with nice readable format"""
    if not dt:
        return "-"
    return timezone.localtime(dt).strftime("%d %b %Y, %I:%M %p")





def decrypt_message_for_email(msg, receiver_user_id=None):
    """
    Decrypts protected messages using the EXACT same logic as your MessageSerializer.
    Key = SECRET_KEY (bytes) + receiver_id.encode()  → padded to 32 bytes
    """
    if not msg:
        return "No message provided"

    if not msg.protected:
        return msg.message or "No message content"

    content = (msg.message or "").strip()
    if not content.startswith("ENCRYPTED:"):
        logger.warning(f"Protected message {getattr(msg, 'id', '?')} missing ENCRYPTED: prefix")
        return "[Invalid format]"

    try:
        token = content[len("ENCRYPTED:"):].strip()
        if not token:
            return "[Empty encrypted message]"

        # Get receiver ID (same as serializer uses validated_data['receiver'].id)
        receiver_id = msg.receiver_id or msg.receiver.id
        if not receiver_id:
            return "[Receiver not found]"

        # EXACT SAME KEY DERIVATION AS YOUR SERIALIZER
        # key_material = (SECRET_KEY + receiver_id.encode()).ljust(32, b'\0')[:32]
        key_material = (SECRET_KEY + str(receiver_id).encode('utf-8')).ljust(32, b'\0')[:32]
        key = base64.urlsafe_b64encode(key_material)
        fernet = Fernet(key)

        decrypted = fernet.decrypt(token.encode('utf-8')).decode('utf-8')
        return decrypted.strip()

    except Exception as e:
        logger.error(f"Decryption failed for message {getattr(msg, 'id', '?')}: {e}", exc_info=True)
        return "[Unable to decrypt message – contact support]"
# -------------------------------------------------
# HTML Builders
# -------------------------------------------------
def build_ticket_table(ticket, message_html=""):
    """Build clean ticket info table + optional message block"""
    return f"""
    <table style="width:100%; border-collapse:collapse; font-size:14px; line-height:1.6;">
        <tr><td style="padding:8px 0;"><b>Ticket No</b></td><td>{ticket.ticket_no}</td></tr>
        <tr><td style="padding:8px 0;"><b>Title</b></td><td>{ticket.title}</td></tr>
        <tr><td style="padding:8px 0;"><b>Status</b></td><td>{ticket.status.field_name if ticket.status else "-"}</td></tr>
        <tr><td style="padding:8px 0;"><b>Priority</b></td><td>{ticket.priority.field_name if ticket.priority else "-"}</td></tr>
        <tr><td style="padding:8px 0;"><b>Department</b></td><td>{ticket.department.field_name if ticket.department else "-"}</td></tr>
        <tr><td style="padding:8px 0;"><b>Location</b></td><td>{ticket.location.field_name if ticket.location else "-"}</td></tr>
        <tr><td style="padding:8px 0;"><b>Requested By</b></td><td>{getattr(ticket.requested, 'firstname', 'Unknown')}</td></tr>
        <tr><td style="padding:8px 0;"><b>Created On</b></td><td>{format_ist(ticket.created_date)}</td></tr>
        {message_html}
    </table>
    """


def wrap_html(title, subtitle, body_content, ticket_url):
    """Professional email wrapper"""
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family:'Segoe UI',Arial,sans-serif; background:#f3f4f6; margin:0; padding:24px; color:#333;">
        <div style="max-width:760px; margin:auto; background:#ffffff; border-radius:14px; padding:32px; box-shadow:0 4px 20px rgba(0,0,0,0.05);">
            <h2 style="color:#111827; margin-top:0; font-size:24px;">{title}</h2>
            <p style="color:#4b5563; font-size:16px; margin-bottom:30px;">{subtitle}</p>

            {body_content}

            <div style="margin:40px 0; text-align:center;">
                <a href="{ticket_url}"
                   style="background:#2563eb; color:white; padding:16px 36px; border-radius:8px;
                          text-decoration:none; font-weight:600; font-size:16px; display:inline-block;">
                    View Ticket
                </a>
            </div>

            <hr style="border:none; border-top:1px solid #e5e7eb; margin:32px 0;">
            <p style="color:#6b7280; font-size:13px; text-align:center;">
                Automated notification • Stemz Helpdesk System<br>
                &copy; 2026 Stemz. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """


# -------------------------------------------------
# Email Sender Task
# -------------------------------------------------
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to_emails, subject, html_body):
    """Reliable SMTP sender with retry"""
    try:
        to_emails = list(set(filter(None, [e.strip() for e in to_emails])))
        if not to_emails:
            logger.warning("send_email_task: No valid recipients")
            return

        msg = MIMEMultipart()
        msg["From"] = settings.DEFAULT_FROM_EMAIL
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30) as server:
            if getattr(settings, "EMAIL_USE_TLS", False):
                server.starttls()
            if getattr(settings, "EMAIL_HOST_USER", None):
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.DEFAULT_FROM_EMAIL, to_emails, msg.as_string())

        logger.info(f"Email sent successfully to: {to_emails}")

    except Exception as exc:
        logger.error(f"Email sending failed (retrying): {exc}")
        raise self.retry(exc=exc)


# -------------------------------------------------
# Ticket Created Notification
# -------------------------------------------------
@shared_task
def send_ticket_created_notification(ticket_id):
    try:
        ticket = CreateTicket.objects.select_related(
            "requested", "priority", "department", "status", "location"
        ).get(id=ticket_id)

        ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"
        table_html = build_ticket_table(ticket)

        # 1. Notify Requester
        if ticket.requested and ticket.requested.email:
            send_email_task.delay(
                [ticket.requested.email],
                f"Your Ticket Created - #{ticket.ticket_no}",
                wrap_html(
                    f"Ticket Created: #{ticket.ticket_no}",
                    "Thank you! Your ticket has been successfully submitted.",
                    table_html,
                    ticket_url
                )
            )

        # 2. Notify Assignees (users + groups)
        assignee_users = set()

        # Direct assigned users
        for email in ticket.assigned_users or []:
            user = User.objects.filter(email=email, is_active=True).first()
            if user:
                assignee_users.add(user)

        # Group members
        for gid in ticket.assigned_groups or []:
            group = UsersGroup.objects.filter(id=gid).first()
            if group:
                for member in group.get_users():
                    if member.is_active:
                        assignee_users.add(member)

        if assignee_users:
            assignee_emails = [u.email for u in assignee_users if u.email]
            send_email_task.delay(
                assignee_emails,
                f"New Ticket Assigned - #{ticket.ticket_no}",
                wrap_html(
                    f"New Ticket Assigned: #{ticket.ticket_no}",
                    "A new ticket has been assigned to you or your team.",
                    table_html,
                    ticket_url
                )
            )

        logger.info(f"Ticket created notifications queued for ticket {ticket.ticket_no}")

    except Exception as e:
        logger.error(f"Error in send_ticket_created_notification: {e}", exc_info=True)


# -------------------------------------------------
# Status Change Notification (Clarification Flow)
# -------------------------------------------------
# Ticket/tasks.py (only the task part — keep the rest of your file unchanged)

@shared_task
def send_status_change_notification(ticket_id, notify_type):
    """
    Handles:
      - clarification_required   → Technician asks requester
      - clarification_supplied  → Requester replies to technicians
    """
    logger.info(f"send_status_change_notification START: ticket_id={ticket_id}, notify_type={notify_type}")

    try:
        ticket = CreateTicket.objects.select_related(
            "requested", "status", "priority", "department", "location"
        ).get(id=ticket_id)

        logger.info(f"Ticket loaded: #{ticket.ticket_no} (PK={ticket.pk}), Title: {ticket.title}")
        ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

        # ============================================================
        # 1. CLARIFICATION REQUIRED (Technician → Requester)
        # ============================================================
        if notify_type == "clarification_required":
            logger.info("=== Processing clarification_required ===")

            # EXPLICIT FK lookup using the actual column name
            technician_messages = Message.objects.filter(
                ticket_no_id=ticket.id  # This is the correct, explicit way
            ).exclude(
                sender=ticket.requested
            ).order_by("-createdon")

            logger.info(f"Query executed: ticket_no_id={ticket.id}, exclude sender_id={ticket.requested.id if ticket.requested else 'None'}")
            logger.info(f"Found {technician_messages.count()} technician messages")

            # Log the latest 3 messages for debugging
            for i, m in enumerate(technician_messages[:3]):
                preview = m.message[:60].replace('\n', ' ') if m.message else 'None'
                logger.info(f"  [{i+1}] Msg ID={m.id} | Created={m.createdon} | Protected={m.protected} | Preview: {preview}")

            msg = technician_messages.first()

            if msg:
                logger.info(f"Selected latest technician message: ID={msg.id}")
                decrypted_text = decrypt_message_for_email(msg)
                logger.info(f"Decrypted message: {decrypted_text}")
                message_text = decrypted_text
            else:
                logger.warning("No technician message found — falling back to default text")
                message_text = "No message provided"

            message_html = f"""
            <tr>
              <td colspan="2" style="padding-top:20px;">
                <b>Technician's Message</b>
                <div style="margin-top:10px; padding:16px; background:#fffbeb; 
                            border-left:5px solid #f59e0b; border-radius:8px; 
                            white-space:pre-line; font-size:15px;">
                  {message_text}
                </div>
              </td>
            </tr>
            """

            if ticket.requested and ticket.requested.email:
                logger.info(f"Queueing email to requester: {ticket.requested.email}")
                send_email_task.delay(
                    [ticket.requested.email],
                    f"Clarification Required - Ticket #{ticket.ticket_no}",
                    wrap_html(
                        f"Clarification Required: #{ticket.ticket_no}",
                        "The technician needs more information to proceed.",
                        build_ticket_table(ticket, message_html),
                        ticket_url
                    )
                )
                logger.info("Clarification required email successfully queued")
            else:
                logger.warning("Requester has no email address")

        # ============================================================
        # 2. CLARIFICATION SUPPLIED (Requester → Technicians)
        # ============================================================
        elif notify_type == "clarification_supplied":
            logger.info("=== Processing clarification_supplied ===")

            msg = Message.objects.filter(
                ticket_no_id=ticket.id,
                sender=ticket.requested
            ).order_by("-createdon").first()

            if not msg:
                logger.info(f"No requester message found for ticket #{ticket.ticket_no}")
                return

            logger.info(f"Found requester message ID {msg.id}")

            assignee_users = set()

            for email in ticket.assigned_users or []:
                user = User.objects.filter(email=email, is_active=True).first()
                if user:
                    assignee_users.add(user)

            for gid in ticket.assigned_groups or []:
                group = UsersGroup.objects.filter(id=gid).first()
                if group:
                    for member in group.get_users():
                        if member.is_active:
                            assignee_users.add(member)

            if not assignee_users:
                logger.info("No assignees found")
                return

            logger.info(f"Sending to {len(assignee_users)} assignees")

            for user in assignee_users:
                if not user.email:
                    continue

                decrypted_text = decrypt_message_for_email(msg, user.id)
                logger.info(f"Decrypted for {user.email}: {decrypted_text}")

                message_html = f"""
                <tr>
                  <td colspan="2" style="padding-top:20px;">
                    <b>Requester's Response</b>
                    <div style="margin-top:10px; padding:16px; background:#ecfeff; 
                                border-left:5px solid #06b6d4; border-radius:8px; 
                                white-space:pre-line; font-size:15px;">
                      {decrypted_text}
                    </div>
                  </td>
                </tr>
                """

                send_email_task.delay(
                    [user.email],
                    f"Clarification Provided - Ticket #{ticket.ticket_no}",
                    wrap_html(
                        f"Clarification Provided: #{ticket.ticket_no}",
                        "The requester has responded with additional information.",
                        build_ticket_table(ticket, message_html),
                        ticket_url
                    )
                )

            logger.info("Clarification supplied emails queued")


        elif notify_type == "closed":
            logger.info("Processing closed notification")

            # Optional: Get last technician message for resolution summary
            last_message = Message.objects.filter(
                ticket_no_id=ticket.id
            ).exclude(
                sender=ticket.requested
            ).order_by("-createdon").first()

            resolution_note = ""
            if last_message:
                resolution_note = decrypt_message_for_email(last_message)
                logger.info(f"Using last technician message as resolution note: {resolution_note[:100]}")

            resolution_html = ""
            if resolution_note:
                resolution_html = f"""
                <tr>
                  <td colspan="2" style="padding-top:20px;">
                    <b>Resolution Summary</b>
                    <div style="margin-top:10px; padding:16px; background:#f0fff0; 
                                border-left:5px solid #28a745; border-radius:8px; 
                                white-space:pre-line; font-size:15px;">
                      {resolution_note}
                    </div>
                  </td>
                </tr>
                """

            closed_html = f"""
            <tr>
              <td colspan="2" style="padding-top:20px;">
                <div style="padding:20px; background:#d4edda; border-left:5px solid #28a745; border-radius:8px;">
                  <p style="margin:0; font-size:16px; color:#155724;">
                    <strong>Your ticket has been resolved and closed.</strong>
                  </p>
                  <p style="margin:10px 0 0;">Thank you for your patience.</p>
                </div>
              </td>
            </tr>
            {resolution_html}
            """

            recipients = set()

            # Add requester
            if ticket.requested and ticket.requested.email:
                recipients.add(ticket.requested.email)

            # Add assignees
            for email in ticket.assigned_users or []:
                user = User.objects.filter(email=email, is_active=True).first()
                if user and user.email:
                    recipients.add(user.email)

            for gid in ticket.assigned_groups or []:
                group = UsersGroup.objects.filter(id=gid).first()
                if group:
                    for member in group.get_users():
                        if member.is_active and member.email:
                            recipients.add(member.email)

            if recipients:
                send_email_task.delay(
                    list(recipients),
                    f"Ticket Resolved & Closed: #{ticket.ticket_no}",
                    wrap_html(
                        f"Ticket Closed: #{ticket.ticket_no}",
                        "Your ticket has been successfully resolved.",
                        build_ticket_table(ticket, closed_html),
                        ticket_url
                    )
                )
                logger.info(f"Closed notification queued to {len(recipients)} recipients: {sorted(recipients)}")
            else:
                logger.warning("No recipients found for closed notification")

    except CreateTicket.DoesNotExist:
        logger.error(f"Ticket {ticket_id} does not exist")
    except Exception as e:
        logger.error(f"Unexpected error in send_status_change_notification: {e}", exc_info=True)
# -------------------------------------------------
# STATUS CHANGE NOTIFICATIONS (FIXED)
# -------------------------------------------------
# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     ticket = CreateTicket.objects.select_related(
#         "requested", "status", "priority", "department", "location"
#     ).filter(id=ticket_id).first()

#     if not ticket:
#         return

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # =================================================
#     # CLARIFICATION REQUIRED → REQUESTER
#     # technician → requester
#     # =================================================
#     if notify_type == "clarification_required":

#         msg = Message.objects.filter(
#             ticket_no=ticket.ticket_no,          # ✅ FIXED
#             receiver_id=ticket.requested.id
#         ).exclude(
#             sender_id=ticket.requested.id
#         ).order_by("-createdon").first()

#         text = ""
#         if msg:
#             text = decrypt_message_for_email(msg, msg.receiver_id)

#         message_html = f"""
#         <tr>
#           <td colspan="2" style="padding-top:16px;">
#             <b>Message</b>
#             <div style="margin-top:8px;padding:14px;
#                         background:#fffbeb;border-left:5px solid #f59e0b;
#                         white-space:pre-line;border-radius:6px;">
#               {text or "No message provided"}
#             </div>
#           </td>
#         </tr>
#         """

#         if ticket.requested and ticket.requested.email:
#             send_email_task.delay(
#                 [ticket.requested.email],
#                 f"Clarification Required - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Required: #{ticket.ticket_no}",
#                     "The technician has requested additional information.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )

#     # =================================================
#     # CLARIFICATION SUPPLIED → ASSIGNEES
#     # requester → technicians
#     # =================================================
#     elif notify_type == "clarification_supplied":

#         msg = Message.objects.filter(
#             ticket_no=ticket.ticket_no,          # ✅ FIXED
#             sender_id=ticket.requested.id
#         ).order_by("-createdon").first()

#         if not msg:
#             return

#         recipients = set()

#         for email in ticket.assigned_users or []:
#             user = User.objects.filter(email=email, is_active=True).first()
#             if user:
#                 recipients.add(user)

#         for gid in ticket.assigned_groups or []:
#             group = UsersGroup.objects.filter(id=gid).first()
#             if group:
#                 recipients.update(group.get_users())

#         for user in recipients:
#             text = decrypt_message_for_email(msg, user.id)

#             message_html = f"""
#             <tr>
#               <td colspan="2" style="padding-top:16px;">
#                 <b>Message</b>
#                 <div style="margin-top:8px;padding:14px;
#                             background:#ecfeff;border-left:5px solid #06b6d4;
#                             white-space:pre-line;border-radius:6px;">
#                   {text}
#                 </div>
#               </td>
#             </tr>
#             """

#             send_email_task.delay(
#                 [user.email],
#                 f"Clarification Provided - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Provided: #{ticket.ticket_no}",
#                     "The requester has provided clarification.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )
# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     """
#     notify_type:
#         - clarification_required  (Technician → Requester)
#         - clarification_supplied  (Requester → Technician)
#     """

#     ticket = CreateTicket.objects.select_related(
#         "requested", "status", "priority", "department", "location"
#     ).filter(id=ticket_id).first()

#     if not ticket:
#         return

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # ============================================================
#     # CLARIFICATION REQUIRED (Technician → Requester)
#     # ============================================================
#     if notify_type == "clarification_required":

#         msg = Message.objects.filter(
#             ticket_no=ticket,
#             receiver=ticket.requested
#         ).exclude(
#             sender=ticket.requested
#         ).order_by("-createdon").first()

#         text = decrypt_message_for_email(
#             msg, ticket.requested.id
#         ) if msg else ""

#         message_html = f"""
#         <tr>
#           <td colspan="2" style="padding-top:16px;">
#             <b>Message</b>
#             <div style="margin-top:8px;padding:14px;
#                         background:#fffbeb;
#                         border-left:5px solid #f59e0b;
#                         white-space:pre-line;
#                         border-radius:6px;">
#               {text or "No message provided"}
#             </div>
#           </td>
#         </tr>
#         """

#         if ticket.requested and ticket.requested.email:
#             send_email_task.delay(
#                 [ticket.requested.email],
#                 f"Clarification Required - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Required: #{ticket.ticket_no}",
#                     "The technician has requested additional information.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )

#     # ============================================================
#     # CLARIFICATION SUPPLIED (Requester → Technicians)
#     # ============================================================
#     elif notify_type == "clarification_supplied":

#         msg = Message.objects.filter(
#             ticket_no=ticket,
#             sender=ticket.requested
#         ).order_by("-createdon").first()

#         if not msg:
#             return

#         recipients = set()

#         # Assigned users
#         for email in ticket.assigned_users or []:
#             user = User.objects.filter(email=email, is_active=True).first()
#             if user:
#                 recipients.add(user)

#         # Assigned groups
#         for gid in ticket.assigned_groups or []:
#             group = UsersGroup.objects.filter(id=gid).first()
#             if group:
#                 for member in group.get_users():
#                     if member.is_active:
#                         recipients.add(member)

#         for user in recipients:
#             if not user.email:
#                 continue

#             text = decrypt_message_for_email(msg, user.id)

#             message_html = f"""
#             <tr>
#               <td colspan="2" style="padding-top:16px;">
#                 <b>Message</b>
#                 <div style="margin-top:8px;padding:14px;
#                             background:#ecfeff;
#                             border-left:5px solid #06b6d4;
#                             white-space:pre-line;
#                             border-radius:6px;">
#                   {text}
#                 </div>
#               </td>
#             </tr>
#             """

#             send_email_task.delay(
#                 [user.email],
#                 f"Clarification Provided - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Provided: #{ticket.ticket_no}",
#                     "The requester has provided clarification.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )


# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     ticket = CreateTicket.objects.select_related(
#         "requested", "status", "priority", "department", "location"
#     ).filter(id=ticket_id).first()

#     if not ticket:
#         return

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # =================================================
#     # CLARIFICATION REQUIRED → REQUESTER
#     # Technician asks clarification
#     # =================================================
#     if notify_type == "clarification_required":

#         # Get latest message (technician message)
#         msg = Message.objects.filter(
#             ticket_no_id=ticket.id
#         ).order_by("-createdon").first()

#         text = ""
#         if msg:
#             text = decrypt_message_for_email(msg, ticket.requested.id)

#         message_html = f"""
#         <tr>
#           <td colspan="2" style="padding-top:16px;">
#             <b>Message</b>
#             <div style="margin-top:8px;padding:14px;
#                         background:#fffbeb;border-left:5px solid #f59e0b;
#                         white-space:pre-line;border-radius:6px;">
#               {text or "No message provided"}
#             </div>
#           </td>
#         </tr>
#         """

#         if ticket.requested and ticket.requested.email:
#             send_email_task.delay(
#                 [ticket.requested.email],
#                 f"Clarification Required - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Required: #{ticket.ticket_no}",
#                     "The technician has requested additional information.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )

#     # =================================================
#     # CLARIFICATION SUPPLIED → ASSIGNEES
#     # Requester replies
#     # =================================================
#     elif notify_type == "clarification_supplied":

#         msg = Message.objects.filter(
#             ticket_no_id=ticket.id,
#             sender_id=ticket.requested.id
#         ).order_by("-createdon").first()

#         if not msg:
#             return  # requester reply is mandatory

#         recipients = set()

#         for email in ticket.assigned_users or []:
#             user = User.objects.filter(email=email, is_active=True).first()
#             if user:
#                 recipients.add(user)

#         for gid in ticket.assigned_groups or []:
#             group = UsersGroup.objects.filter(id=gid).first()
#             if group:
#                 recipients.update(group.get_users())

#         for user in recipients:
#             text = decrypt_message_for_email(msg, user.id)

#             message_html = f"""
#             <tr>
#               <td colspan="2" style="padding-top:16px;">
#                 <b>Message</b>
#                 <div style="margin-top:8px;padding:14px;
#                             background:#ecfeff;border-left:5px solid #06b6d4;
#                             white-space:pre-line;border-radius:6px;">
#                   {text}
#                 </div>
#               </td>
#             </tr>
#             """

#             send_email_task.delay(
#                 [user.email],
#                 f"Clarification Provided - Ticket #{ticket.ticket_no}",
#                 wrap_html(
#                     f"Clarification Provided: #{ticket.ticket_no}",
#                     "The requester has provided clarification.",
#                     build_ticket_table(ticket, message_html),
#                     ticket_url
#                 )
#             )



# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     ticket = CreateTicket.objects.select_related(
#         "requested", "priority", "department", "status", "location"
#     ).get(id=ticket_id)

#     ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"

#     # ---------- FETCH MESSAGE ----------
#     clarification_text = ""
#     qs = Message.objects.filter(ticket_no_id=ticket.id)

#     if notify_type == "clarification_required":
#         qs = qs.exclude(sender_id=ticket.requested_id)
#     elif notify_type == "clarification_supplied":
#         qs = qs.filter(sender_id=ticket.requested_id)

#     msg = qs.order_by("-createdon").first()
#     if msg:
#         clarification_text = decrypt_message_for_email(msg)

#     message_section = ""
#     if clarification_text:
#         message_section = f"""
#         <tr>
#             <td colspan="2" style="padding-top:16px;">
#                 <strong>Message</strong>
#                 <div style="margin-top:8px;padding:14px;
#                     background:#fffbeb;border-left:5px solid #f59e0b;
#                     white-space:pre-line;border-radius:6px;">
#                     {clarification_text}
#                 </div>
#             </td>
#         </tr>
#         """

#     table_html = build_ticket_table(ticket, message_section)

#     # ---------- CLARIFICATION REQUIRED → REQUESTER ----------
#     if notify_type == "clarification_required":
#         if ticket.requested and ticket.requested.email:
#             html_body = wrap_html(
#                 f"Clarification Required: #{ticket.ticket_no}",
#                 "Please provide the requested clarification.",
#                 table_html,
#                 ticket_url
#             )

#             send_email_task.delay(
#                 [ticket.requested.email],
#                 f"Clarification Required - #{ticket.ticket_no}",
#                 html_body
#             )

#     # ---------- CLARIFICATION SUPPLIED → ASSIGNEES ----------
#     elif notify_type == "clarification_supplied":
#         recipients = set()

#         for email in (ticket.assigned_users or []):
#             try:
#                 user = User.objects.get(email=email, is_active=True)
#                 recipients.add(user.email)
#             except User.DoesNotExist:
#                 pass

#         for group_id in (ticket.assigned_groups or []):
#             try:
#                 group = UsersGroup.objects.get(id=group_id)
#                 for member in group.get_users():
#                     if member.is_active and member.email:
#                         recipients.add(member.email)
#             except UsersGroup.DoesNotExist:
#                 pass

#         if recipients:
#             html_body = wrap_html(
#                 f"Clarification Provided: #{ticket.ticket_no}",
#                 "The requester has provided clarification.",
#                 table_html,
#                 ticket_url
#             )

#             send_email_task.delay(
#                 list(recipients),
#                 f"Clarification Provided - #{ticket.ticket_no}",
#                 html_body
#             )


# # Ticket/tasks.py

# import logging
# import smtplib

# from celery import shared_task
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# from Ticket.models import CreateTicket,Message
# from Authenticate.models import UsersGroup  # Change if your UsersGroup model is in a different app
# from django.db.models import Q
# User = get_user_model()
# logger = logging.getLogger(__name__)


# from django.utils import timezone

# def format_ist(dt):
#     if not dt:
#         return "-"
#     return timezone.localtime(dt).strftime("%d %b %Y, %I:%M %p")

# def get_latest_clarification_message(ticket_no, notify_type):
#     """
#     Returns the correct message text based on protection flag.
#     Includes protected messages.
#     """
#     qs = Message.objects.filter(ticket_no=ticket_no)

#     # Filter by notify_type
#     qs = Message.objects.filter(ticket_no=ticket_no)
#     if notify_type == "clarification_required":
#         qs = qs.filter(
#             Q(message__icontains="Clarification Required") |
#             Q(protected=True, decrypted_message__icontains="Clarification Required")
#         )
#     elif notify_type == "clarification_supplied":
#         qs = qs.filter(
#             Q(message__icontains="Clarification Supplied") |
#             Q(protected=True, decrypted_message__icontains="Clarification Supplied")
#         )

#     msg = qs.order_by("-createdon").first()

#     if not msg:
#         return None

#     # return decrypted_message if protected
#     if msg.protected:
#         return msg.decrypted_message or ""

#     return msg.message or ""




# @shared_task(bind=True, max_retries=3, default_retry_delay=60)
# def send_email_task(self, to_emails, subject, html_body, cc=None, bcc=None):
#     """Reliable SMTP email sender with retry"""
#     try:
#         cc = cc or []
#         bcc = bcc or []
#         to_emails = [e for e in to_emails if e]  # Remove empty
#         all_recipients = list(set(to_emails + cc + bcc))

#         if not all_recipients:
#             logger.warning("send_email_task: No valid recipients provided.")
#             return

#         msg = MIMEMultipart()
#         msg["From"] = settings.DEFAULT_FROM_EMAIL
#         msg["To"] = ", ".join(to_emails)
#         if cc:
#             msg["Cc"] = ", ".join(cc)
#         msg["Subject"] = subject
#         msg.attach(MIMEText(html_body, "html"))

#         with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30) as server:
#             if getattr(settings, "EMAIL_USE_TLS", False):
#                 server.starttls()
#             if getattr(settings, "EMAIL_HOST_USER", None) and getattr(settings, "EMAIL_HOST_PASSWORD", None):
#                 server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#             server.sendmail(settings.DEFAULT_FROM_EMAIL, all_recipients, msg.as_string())

#         logger.info(f"Email sent successfully to: {to_emails}")

#     except Exception as exc:
#         logger.error(f"Email sending failed (will retry): {exc}")
#         raise self.retry(exc=exc)


# @shared_task
# def send_ticket_created_notification(ticket_id):
#     """Send notification on ticket creation — supports direct users and full group members"""
#     try:
#         ticket = CreateTicket.objects.select_related(
#             'requested', 'priority', 'department', 'status'
#         ).get(id=ticket_id)

#         recipients = set()

#         # 1. Direct assigned users (assigned_users = list of emails)
#         for email in (ticket.assigned_users or []):
#             if not email:
#                 continue
#             try:
#                 user = User.objects.get(email=email, is_active=True)
#                 recipients.add(user.email)
#             except User.DoesNotExist:
#                 logger.warning(f"Assigned user not found/inactive: {email}")

#         # 2. All members from assigned groups
#         for group_id in (ticket.assigned_groups or []):
#             try:
#                 group = UsersGroup.objects.get(id=group_id)
#                 for member in group.get_users():
#                     if member.is_active and member.email:
#                         recipients.add(member.email)
#             except UsersGroup.DoesNotExist:
#                 logger.warning(f"Assigned group not found: {group_id}")

#         # Optional: Notify requester automatically
#         #Uncomment if you want the ticket requester to always get a copy
#         if ticket.requested and ticket.requested.is_active and ticket.requested.email:
#             recipients.add(ticket.requested.email)
#         # if ticket.requested:
#         #     if ticket.requested.is_active and ticket.requested.email:
#         #         recipients.add(ticket.requested.email)
#         #     else:
#         #         logger.warning(
#         #             f"Requester inactive or email missing for ticket {ticket.ticket_no}"
#         #         )
#         if not recipients:
#             logger.info(f"No recipients found for ticket {ticket.ticket_no} (ID: {ticket.id})")
#             return

#         ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"  # Update domain

#         html_body = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
#             <h2>New Ticket Assigned: #{ticket.ticket_no}</h2>
#             <p>A new helpdesk ticket has been created and assigned to you:</p>
            
#             <table style="background:#f9f9f9; border-radius:8px; padding:15px; width:100%; max-width:600px;">
#                 <tr><td><strong>Ticket No:</strong></td><td><strong>{ticket.ticket_no}</strong></td></tr>
#                 <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
#                 <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else 'Normal'}</td></tr>
#                 <tr><td><strong>Department:</strong></td><td>{ticket.department.field_name if ticket.department else '-'}</td></tr>
#                <tr><td><strong>Location:</strong></td><td>{ticket.location.field_name if ticket.location else '-'}</td></tr>
#                  <tr><td><strong>Requested By:</strong></td>
#                <td>{ticket.requested.firstname if ticket.requested and ticket.requested.firstname else ticket.requested.email if ticket.requested else 'Unknown'}</td></tr>
#                 <tr><td><strong>Created On:</strong></td><td>{format_ist(ticket.created_date)}</td></tr>

#             </table>

#             <p style="margin:30px 0;">
#                 <a href="{ticket_url}" style="background:#0066cc; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold;">
#                     View Ticket
#                 </a>
#             </p>

#             <hr style="border:none; border-top:1px solid #eee; margin:30px 0;">
#             <small>This is an automated notification from Stemz Helpdesk System.</small>
#         </body>
#         </html>
#         """

#         subject = f"New Ticket #{ticket.ticket_no}: {ticket.title[:60]}..."

#         send_email_task.delay(
#             to_emails=list(recipients),
#             subject=subject,
#             html_body=html_body
#         )

#         logger.info(
#             f"Notification queued for ticket {ticket.ticket_no} (ID: {ticket.id}) → "
#             f"{len(recipients)} recipients: {sorted(recipients)}"
#         )

#     except CreateTicket.DoesNotExist:
#         logger.error(f"Ticket ID {ticket_id} does not exist.")
#     except Exception as e:
#         logger.error(f"Error in send_ticket_created_notification({ticket_id}): {e}", exc_info=True)
# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     """
#     Send status-specific notifications with clarification messages.

#     notify_type options:
#         - 'clarification_required': notify requester (message from technician/assignee)
#         - 'clarification_supplied': notify assignees (message from requester)
#         - 'closed': notify both requester and assignees
#     """
#     try:
#         # Fetch ticket with related fields
#         ticket = CreateTicket.objects.select_related(
#             'requested', 'priority', 'department', 'status', 'location'
#         ).get(id=ticket_id)

#         message_section = ""
#         clarification_text = None

#         # --- Step 1: Fetch the latest clarification message based on sender ---
#         if notify_type in ["clarification_required", "clarification_supplied"]:
#             qs = Message.objects.filter(ticket_id=ticket.id)

#             if notify_type == "clarification_required":
#                 # Last message from technician/assignee
#                 if ticket.requested:
#                  qs = qs.exclude(sender_id=ticket.requested.id)
#             elif notify_type == "clarification_supplied":
#                 # Last message from requester
#                 if ticket.requested:
#                  qs = qs.filter(sender_id=ticket.requested.id)

#             msg = qs.order_by("-createdon").first()
#             if msg:
#                 clarification_text = msg.decrypted_message if msg.protected else msg.message

#             if clarification_text:
#                 message_section = f"""
#                 <tr>
#                     <td colspan="2" style="padding-top:15px;">
#                         <strong>Message:</strong>
#                         <div style="
#                             margin-top:8px;
#                             padding:12px;
#                             background:#fffbea;
#                             border-left:4px solid #f59e0b;
#                             white-space:pre-line;
#                             font-size:14px;
#                         ">
#                             {clarification_text}
#                         </div>
#                     </td>
#                 </tr>
#                 """

#         # --- Step 2: Determine recipients ---
#         recipients = set()

#         if notify_type in ["clarification_supplied", "closed"]:
#             # Assigned users
#             for email in (ticket.assigned_users or []):
#                 if email:
#                     try:
#                         user = User.objects.get(email=email, is_active=True)
#                         recipients.add(user.email)
#                     except User.DoesNotExist:
#                         logger.warning(f"Assigned user not found/inactive: {email}")

#             # Assigned group members
#             for group_id in (ticket.assigned_groups or []):
#                 try:
#                     group = UsersGroup.objects.get(id=group_id)
#                     for member in group.get_users():
#                         if member.is_active and member.email:
#                             recipients.add(member.email)
#                 except UsersGroup.DoesNotExist:
#                     logger.warning(f"Assigned group not found: {group_id}")

#         if notify_type in ["clarification_required", "closed"]:
#             # Requester
#             if ticket.requested and ticket.requested.is_active and ticket.requested.email:
#                 recipients.add(ticket.requested.email)
#             else:
#                 logger.warning(f"Requester has no valid email for ticket {ticket.ticket_no}")

#         if not recipients:
#             logger.info(f"No recipients for {notify_type} notification on ticket {ticket.ticket_no}")
#             return

#         # --- Step 3: Prepare email content ---
#         ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"  # Update domain
#         status_name = ticket.status.field_name if ticket.status else "Unknown"

#         if notify_type == "clarification_required":
#             subject = f"Clarification Needed: Ticket #{ticket.ticket_no} - {ticket.title[:50]}..."
#             greeting = "Please provide clarification"
#             action_text = "The technician has requested additional information."
#         elif notify_type == "clarification_supplied":
#             subject = f"Clarification Provided: Ticket #{ticket.ticket_no}"
#             greeting = "The requester has provided clarification"
#             action_text = "Please review the updated information and proceed."
#         else:  # closed
#             subject = f"Ticket Closed: #{ticket.ticket_no} - {ticket.title[:50]}..."
#             greeting = "This ticket has been resolved"
#             action_text = f"Status: <strong>{status_name}</strong>"

#         html_body = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
#             <h2>Ticket Update: #{ticket.ticket_no}</h2>
#             <p>{greeting}:</p>

#             <table style="background:#f9f9f9; border-radius:8px; padding:15px; width:100%; max-width:600px;">
#                 <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
#                 <tr><td><strong>Status:</strong></td><td><strong>{status_name}</strong></td></tr>
#                 <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else '-'}</td></tr>
#                 <tr><td><strong>Location:</strong></td><td>{ticket.location.field_name if ticket.location else '-'}</td></tr>
#                 <tr><td><strong>Requested By:</strong></td>
#                 <td>{ticket.requested.firstname if ticket.requested and ticket.requested.firstname else ticket.requested.email if ticket.requested else 'Unknown'}</td></tr>
#                 {message_section}
#             </table>

#             <p style="margin:20px 0;">{action_text}</p>

#             <p style="margin:30px 0;">
#                 <a href="{ticket_url}" style="background:#0066cc; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold;">
#                     View Ticket Details
#                 </a>
#             </p>

#             <hr style="border:none; border-top:1px solid #eee; margin:30px 0;">
#             <small>This is an automated notification from Stemz Helpdesk System.</small>
#         </body>
#         </html>
#         """

#         # --- Step 4: Send email ---
#         send_email_task.delay(
#             to_emails=list(recipients),
#             subject=subject,
#             html_body=html_body
#         )

#         logger.info(
#             f"Status update ({notify_type}) email queued for ticket {ticket.ticket_no} → "
#             f"{len(recipients)} recipients: {sorted(recipients)}"
#         )

#     except CreateTicket.DoesNotExist:
#         logger.error(f"Ticket ID {ticket_id} not found for status notification.")
#     except Exception as e:
#         logger.error(f"Error in send_status_change_notification({ticket_id}, {notify_type}): {e}", exc_info=True)


# @shared_task
# def send_status_change_notification(ticket_id, notify_type):
#     """
#     Send status-specific notifications.
#     notify_type options:
#         - 'clarification_required': only requester
#         - 'clarification_supplied': only assignees (users + groups)
#         - 'closed': both requester and assignees
#     """
#     try:
#         ticket = CreateTicket.objects.select_related(
#             'requested', 'priority', 'department', 'status','location'
#         ).get(id=ticket_id)

#         message_section = ""

#         # clarification_text = None
#         # if notify_type in ["clarification_required", "clarification_supplied"]:
#         #     clarification_text = get_latest_clarification_message(ticket.ticket_no)


#         recipients = set()

#         status_name = ticket.status.field_name if ticket.status else "Unknown"
#         requested_by = (
#                 ticket.requested.firstname.strip()
#                 if ticket.requested and ticket.requested.firstname
#                 else ticket.requested.email
#                 if ticket.requested
#                 else "Unknown"
#             )


#         # Determine who to notify based on notify_type
#         if notify_type in ["clarification_supplied", "closed"]:
#             # Add assigned users
#             for email in (ticket.assigned_users or []):
#                 if email:
#                     try:
#                         user = User.objects.get(email=email, is_active=True)
#                         recipients.add(user.email)
#                     except User.DoesNotExist:
#                         logger.warning(f"Assigned user not found/inactive: {email}")

#             # Add group members
#             for group_id in (ticket.assigned_groups or []):
#                 try:
#                     group = UsersGroup.objects.get(id=group_id)
#                     for member in group.get_users():
#                         if member.is_active and member.email:
#                             recipients.add(member.email)
#                 except UsersGroup.DoesNotExist:
#                     logger.warning(f"Assigned group not found: {group_id}")

#         if notify_type in ["clarification_required", "closed"]:
#             # Add requester
#             if ticket.requested and ticket.requested.is_active and ticket.requested.email:
#                 recipients.add(ticket.requested.email)
#             else:
#                 logger.warning(f"Requester has no valid email for ticket {ticket.ticket_no}")

#         if not recipients:
#             logger.info(f"No recipients for {notify_type} notification on ticket {ticket.ticket_no}")
#             return

#         ticket_url = f"https://your-helpdesk-domain.com/tickets/{ticket.ticket_no}"  # Update with real domain

#         # Customize subject and body based on notify_type
#         if notify_type == "clarification_required":
#             subject = f"Clarification Needed: Ticket #{ticket.ticket_no} - {ticket.title[:50]}..."
#             greeting = "Please provide clarification"
#             action_text = "The technician has requested additional information."
#         elif notify_type == "clarification_supplied":
#             subject = f"Clarification Provided: Ticket #{ticket.ticket_no}"
#             greeting = "The requester has provided clarification"
#             action_text = "Please review the updated information and proceed."
#         else:  # closed
#             subject = f"Ticket Closed: #{ticket.ticket_no} - {ticket.title[:50]}..."
#             greeting = "This ticket has been resolved"
#             # action_text = f"Status: <strong>{status_name}</strong>"

          

#         if notify_type in ["clarification_required", "clarification_supplied"]:
#             clarification_text = get_latest_clarification_message(
#                 ticket.ticket_no,
#                 notify_type
#             )

#             if clarification_text:
#                 message_section = f"""
#                 <tr>
#                     <td colspan="2" style="padding-top:15px;">
#                         <strong>Message:</strong>
#                         <div style="
#                             margin-top:8px;
#                             padding:12px;
#                             background:#fffbea;
#                             border-left:4px solid #f59e0b;
#                             white-space:pre-line;
#                             font-size:14px;
#                         ">
#                             {clarification_text}
#                         </div>
#                     </td>
#                 </tr>
#                 """

#         html_body = f"""
#         <html>
#         <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
#             <h2>Ticket Update: #{ticket.ticket_no}</h2>
#             <p>{greeting}:</p>

#             <table style="background:#f9f9f9; border-radius:8px; padding:15px; width:100%; max-width:600px;">
#                 <tr><td><strong>Title:</strong></td><td>{ticket.title}</td></tr>
#                 <tr><td><strong>Status:</strong></td><td><strong>{status_name}</strong></td></tr>
#                 <tr><td><strong>Priority:</strong></td><td>{ticket.priority.field_name if ticket.priority else '-'}</td></tr>
#                 <tr><td><strong>Location:</strong></td><td>{ticket.location.field_name if ticket.location else '-'}</td></tr>
#                  <tr><td><strong>Requested By:</strong></td>
#     <td>{ticket.requested.firstname if ticket.requested and ticket.requested.firstname else ticket.requested.email if ticket.requested else 'Unknown'}</td></tr>
#              {message_section}
#             </table>

#             <p style="margin:20px 0;">{action_text}</p>

#             <p style="margin:30px 0;">
#                 <a href="{ticket_url}" style="background:#0066cc; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold;">
#                     View Ticket Details
#                 </a>
#             </p>

#             <hr style="border:none; border-top:1px solid #eee; margin:30px 0;">
#             <small>This is an automated notification from Stemz Helpdesk System.</small>
#         </body>
#         </html>
#         """

#         send_email_task.delay(
#             to_emails=list(recipients),
#             subject=subject,
#             html_body=html_body
#         )

#         logger.info(
#             f"Status update ({notify_type}) email queued for ticket {ticket.ticket_no} → "
#             f"{len(recipients)} recipients: {sorted(recipients)}"
#         )

#     except CreateTicket.DoesNotExist:
#         logger.error(f"Ticket ID {ticket_id} not found for status notification.")
#     except Exception as e:
#         logger.error(f"Error in send_status_change_notification({ticket_id}, {notify_type}): {e}", exc_info=True)
