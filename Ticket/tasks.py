# Ticket/tasks.py
import smtplib
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template import Template, Context
from django.contrib.auth import get_user_model
from Ticket.models import CreateTicket, TicketSLA, TicketApprovalLog, TicketEmailTemplate,TicketsMasterConfiguration
from Ticket.models import Holiday

User = get_user_model()


# ============================================================
# EMAIL SENDER TASK
# ============================================================
@shared_task(bind=True, max_retries=3)
def send_email_task(self, to_emails, subject, html_body, cc=None, bcc=None):
    """Send HTML email asynchronously using SMTP."""
    try:
        cc = cc or []
        bcc = bcc or []
        all_recipients = list(set(to_emails + cc + bcc))

        if not all_recipients:
            print("⚠️ No recipients found for email.")
            return

        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = ", ".join(to_emails)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if getattr(settings, "EMAIL_USE_TLS", False):
                server.starttls()
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, all_recipients, msg.as_string())

        print(f"✅ Email sent successfully to {to_emails}")

    except Exception as exc:
        print(f"❌ Email send error: {exc}")
        raise self.retry(exc=exc, countdown=30)


# ============================================================
# SLA PARSER (convert text to hours)
# ============================================================
def parse_sla_time_to_hours(sla_text: str) -> float:
    """
    Converts SLA text (e.g., '1 day 5 hr 10 min', '1.5 day', '2 working days', '3.5 hrs')
    into total hours using 24-hour working days.
    """

    if not sla_text:
        return 24.0  # Default 1 day (24 hours)

    # Normalize text
    text = (
        sla_text.lower()
        .replace(",", " ")
        .replace("and", " ")
        .replace("working", "")
        .replace("days", "day")
        .replace("hrs", "hr")
        .replace("hours", "hr")
        .replace("minutes", "min")
        .replace("mins", "min")
        .strip()
    )

    # Split into parts (e.g. ['1', 'day', '5', 'hr', '10', 'min'])
    parts = text.split()
    days = hours = minutes = 0.0
    i = 0

    while i < len(parts):
        try:
            val = float(parts[i])
            unit = parts[i + 1] if i + 1 < len(parts) else ""
            if "day" in unit:
                days += val
            elif "hr" in unit:
                hours += val
            elif "min" in unit:
                minutes += val
            i += 2
        except (ValueError, IndexError):
            i += 1

    total_hours = (days * 24) + hours + (minutes / 60)
    return round(total_hours, 2)

# def parse_sla_time_to_hours(sla_text: str) -> float:
#     """Converts SLA string ('1 day 2 hrs', '1.5 day', '30 mins') into hours (24h/day)."""
#     if not sla_text:
#         return 24.0

#     text = sla_text.lower().replace("working", "").replace("days", "day").replace("hrs", "hr").strip()
#     days = hours = minutes = 0.0
#     parts = text.split()

#     i = 0
#     while i < len(parts):
#         try:
#             val = float(parts[i])
#             unit = parts[i + 1] if i + 1 < len(parts) else ""
#             if "day" in unit:
#                 days += val
#             elif "hr" in unit:
#                 hours += val
#             elif "min" in unit:
#                 minutes += val
#             i += 2
#         except (ValueError, IndexError):
#             i += 1

#     total_hours = (days * 24) + hours + (minutes / 60)
#     return total_hours


# ============================================================
# ADD SLA TIME SKIPPING HOLIDAYS & SUNDAYS
# ============================================================
def add_sla_time_skipping_holidays(start_time, sla_hours):
    """Adds SLA time (in hours), skipping Sundays and holidays."""

    """
    Adds SLA time while skipping Sundays & Holidays.
    Keeps original time of day → Sunday 5:00 PM + 1 hr → Monday 6:00 PM
    This is your exact requirement.
    """
    end_time = start_time
    remaining_minutes = int(sla_hours * 60)

    while remaining_minutes > 0:
        end_time += timedelta(minutes=1)
        current_date = end_time.date()

        # Skip full day if Sunday or Holiday — keep same time
        if (current_date.weekday() == 6 or 
            Holiday.objects.filter(date=current_date, status=1).exists()):
            end_time += timedelta(days=1)
            continue

        remaining_minutes -= 1

    return end_time
    # end_time = start_time
    # remaining_minutes = int(sla_hours * 60)

    # while remaining_minutes > 0:
    #     end_time += timedelta(minutes=1)
    #     current_date = end_time.date()

    #     # Skip Sundays & holidays
    #     if current_date.weekday() == 6 or Holiday.objects.filter(date=current_date, status=1).exists():
    #         next_day = current_date + timedelta(days=1)
    #         end_time = timezone.make_aware(datetime.combine(next_day, datetime.min.time()))
    #         continue

    #     remaining_minutes -= 1

    # return end_time

# ============================================================
# SLA ESCALATION HANDLER (Updated)  working
# # ============================================================
# @shared_task
# def handle_sla_escalation(ticket_id, approver_level):
#     """
#     Handles SLA auto-escalation for multi-level approvals.
#     If the current approver does not act within SLA → escalate to the next approver.
#     """
#     try:
#         ticket = CreateTicket.objects.get(id=ticket_id)  # Fetch ticket by ID
#         sla = ticket.sla  # Get SLA details for the ticket

#         # Get the current approval log for the specified approver level
#         current_log = TicketApprovalLog.objects.filter(
#             ticket=ticket, current_level=approver_level, status="Pending"
#         ).first()

#         if not current_log:
#             print(f"✅ No pending approval for Ticket #{ticket.ticket_no}, Level {approver_level}")
#             return

#         # If the ticket is on hold, do not escalate
#         if current_log.onhold_start:
#             print(f"✅ Ticket #{ticket.ticket_no} is on hold, skipping escalation.")
#             return

#         # Mark current approver as timed out (if SLA expires)
#         current_log.status = "Timeout"
#         current_log.sla_breach = True
#         current_log.is_current_level = False
#         current_log.save()

#         print(f"⚠️ SLA Timeout - Ticket #{ticket.ticket_no} (Level {approver_level})")

#         # Check for next approver (e.g., Approver Level 2)
#         next_level = approver_level + 1
#         next_log = TicketApprovalLog.objects.filter(ticket=ticket, current_level=next_level).first()

#         if not next_log:
#             # No further approvers → Close the ticket
#             ticket.status = "Closed - Final Level Breached"
#             ticket.save()
#             print(f"🚨 Ticket #{ticket.ticket_no} reached final escalation level. Auto-closed.")
#             return

#         # Activate next approver and create a new log
#         next_log.is_current_level = True
#         next_log.status = "Pending"
#         next_log.created_on = timezone.now()
#         next_log.save()

#         # Get next approver's email
#         next_approver_user_id = getattr(sla, f"Approver_level{next_level}_user_id", None)
#         next_approver_email = None

#         if next_approver_user_id:
#             try:
#                 user = User.objects.get(id=next_approver_user_id)
#                 next_approver_email = user.email
#             except User.DoesNotExist:
#                 print(f"⚠️ Approver not found for Level {next_level}")
#         else:
#             print(f"⚠️ No approver ID found for Level {next_level}")

#         if not next_approver_email:
#             print(f"❌ No valid email for next approver. Skipping email send.")
#             return

#         # Create and send escalation email
#         description = ticket.description or "N/A"
#         subject = f"⚠️ Ticket #{ticket.ticket_no} Escalated - Level {next_level}"
#         body = f"""
#             <p>Dear Approver,</p>
#             <p>Ticket <b>#{ticket.ticket_no}</b> has been escalated to you.</p>
#             <p><b>Requester:</b> {ticket.requested.full_name}<br>
#                <b>Request Date:</b> {ticket.created_date.strftime('%Y-%m-%d %H:%M:%S')}<br>
#                <b>Description:</b> {description}</p>
#             <p>Please review and take action promptly.</p>
#             <p>-- Ticketing System</p>
#         """

#         send_email_task.delay([next_approver_email], subject, body)

#         print(f"📧 Escalation email sent to {next_approver_email}")

#         # Calculate SLA for next approver
#         next_sla_text = getattr(sla, f"Approver_level{next_level}_time", None)

#         if next_sla_text:
#             hours = parse_sla_time_to_hours(next_sla_text)
#             adjusted_end = add_sla_time_skipping_holidays(timezone.now(), hours)
#             delay_seconds = (adjusted_end - timezone.now()).total_seconds()

#             # Schedule next escalation task
#             handle_sla_escalation.apply_async(
#                 args=[ticket.id, next_level],
#                 countdown=int(delay_seconds)
#             )

#             print(f"⏱ SLA escalation scheduled after {hours} hours (~{delay_seconds / 3600:.2f} hrs).")

#         else:
#             print(f"✅ No next SLA time or approver for Ticket #{ticket.ticket_no}")

#     except Exception as e:
#         print(f"❌ Error in handle_sla_escalation: {e}")
# -------------------------
# handle_sla_escalation (full updated task)
# -------------------------
# -------------------------
# @shared_task(bind=True)
# def handle_sla_escalation(self, ticket_id, approver_level):
#     print("\n" + "="*80)
#     print(f"🚀 START SLA TASK | Ticket ID: {ticket_id}, Approver Level: {approver_level}")
#     print("="*80)

#     try:
#         # 1️⃣ Fetch ticket and SLA
#         print("🔍 Fetching Ticket & SLA...")
#         ticket = CreateTicket.objects.select_related('sla').get(id=ticket_id)
#         sla = ticket.sla

#         if not sla:
#             print(f"⚠️ No SLA found for Ticket ID: {ticket_id}")
#             return

#         print(f"🎫 Ticket: {ticket.ticket_no}")
#         print(f"📄 SLA Object Loaded")

#         # 2️⃣ Fetch approval log (includes Pending and On-Hold)
#         print(f"🔍 Fetching Approval Log for Level {approver_level}...")
#         current_log = TicketApprovalLog.objects.filter(
#             ticket=ticket,
#             current_level=approver_level,
#             is_current_level=True,
#             approval_status__in=["Pending", "On-Hold"]
#         ).first()

#         if not current_log:
#             print(f"⚠️ No approval log found at Level {approver_level} → STOP")
#             return

#         print(f"📝 Approval Log Found → id={current_log.id}, created_on={current_log.created_on}")
#         print(f"   SLA End Time: {current_log.sla_end_time}")
#         print(f"   On-Hold Start: {current_log.onhold_start}")
#         print(f"   Approval Status: {current_log.approval_status}")

#         # 3️⃣ If approved early
#         if current_log.approval_status == 'Approved':
#             print("\n" + "-"*60)
#             print(f"✅ APPROVED EARLY at Level {approver_level}")
#             print("-"*60)

#             current_log.sla_end_time = timezone.now()
#             current_log.save()
#             print(f"⏳ Updated SLA End Time → {current_log.sla_end_time}")

#             # Move to next approver (same as normal approve flow)
#             next_level = approver_level + 1
#             next_user = getattr(sla, f"Approver_level{next_level}_user", None)

#             if not next_user:
#                 print("🏁 No further approver. Closing ticket.")
#                 ticket.status = self._get_master_status("Approved") if hasattr(self, "_get_master_status") else ticket.status
#                 ticket.save()
#                 return

#             print(f"➡️ Moving to Next Approver → Level {next_level} (user_id={next_user.id})")

#             level_sla_text = getattr(sla, f"Approver_level{next_level}_time")
#             sla_hours = parse_sla_time_to_hours(level_sla_text)

#             with transaction.atomic():
#                 print("🔄 Making previous levels non-current...")
#                 TicketApprovalLog.objects.filter(ticket=ticket).update(is_current_level=False)

#                 print("➕ Creating/Updating next level log...")
#                 next_log, created = TicketApprovalLog.objects.update_or_create(
#                     ticket=ticket,
#                     current_level=next_level,
#                     defaults={
#                         'sla': sla,
#                         'created_by_id': next_user.id,
#                         'status': "Pending",
#                         'approval_status': "Pending",
#                         'is_current_level': True,
#                         'comments': f"Assigned to Level {next_level} approver: {next_user.email}",
#                         'created_on': timezone.now(),
#                         'sla_end_time': add_sla_time_skipping_holidays(
#                             timezone.now(),
#                             sla_hours
#                         )
#                     }
#                 )

#             print(f"⏳ Next Approver SLA End Time: {next_log.sla_end_time}")

#             # Email
#             print("📧 Sending Approval Email...")
#             template_obj = TicketEmailTemplate.objects.filter(
#                 email_event__iexact="Approval",
#                 is_active="Y"
#             ).first()

#             if template_obj:
#                 print("📨 Email Template Loaded")
#                 ctx = Context({
#                     'firstname': ticket.requested.firstname or ticket.requested.email,
#                     'realname': getattr(ticket.requested, "realname", ""),
#                     'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#                     'name': ticket.title or ticket.description or "N/A",
#                     'ticket_url': f"http://yourdomain.com/tickets/{ticket.id}",
#                     'mail_signature': 'IT Support Team',
#                     'year': timezone.now().year
#                 })
#                 html_content = Template(template_obj.email_template).render(ctx)
#                 send_email_task.delay([next_user.email], f"Approval Request - Ticket #{ticket.ticket_no}", html_content)
#             else:
#                 print("⚠️ No Email Template Found (Approval)")

#             # Schedule next SLA task
#             delay_seconds = (next_log.sla_end_time - timezone.now()).total_seconds()
#             delay_seconds = max(1, int(delay_seconds))
#             print(f"🕑 Scheduling Next SLA Check in {delay_seconds} seconds")
#             result = handle_sla_escalation.apply_async(args=[ticket.id, next_level], countdown=delay_seconds)
#             try:
#                 next_log.scheduled_task_id = result.id
#                 next_log.save()
#                 print(f"🔖 Stored scheduled_task_id = {result.id} on TicketApprovalLog id={next_log.id}")
#             except Exception:
#                 print("⚠️ scheduled_task_id field not present — skipping store.")
#             return

#         # 4️⃣ Ticket On-Hold (pause & store remaining seconds)
#         if current_log.onhold_start:
#             print("\n" + "-"*60)
#             print("⏸️ TICKET IS CURRENTLY ON HOLD")
#             print("-"*60)
#             hold_duration = timezone.now() - current_log.onhold_start
#             print(f"⏱ Hold Duration: {hold_duration}")

#             # compute remaining seconds (best effort)
#             if current_log.sla_end_time:
#                 remaining_seconds = int(max(0, (current_log.sla_end_time - timezone.now()).total_seconds()))
#                 print(f"🟡 Remaining seconds at on-hold moment: {remaining_seconds}")
#                 try:
#                     current_log.remaining_sla_seconds = remaining_seconds
#                 except Exception:
#                     pass
#             else:
#                 sla_text = getattr(sla, f"Approver_level{approver_level}_time")
#                 hours = parse_sla_time_to_hours(sla_text)
#                 print(f"🛠 Extending SLA END TIME by Hold Duration (fallback calc)")
#                 current_log.sla_end_time = add_sla_time_skipping_holidays(
#                     current_log.created_on or timezone.now(),
#                     hours + (hold_duration.total_seconds() / 3600)
#                 )
#                 current_log.save()

#             # revoke scheduled task if present (best-effort)
#             try:
#                 task_id = getattr(current_log, "scheduled_task_id", None)
#                 if task_id:
#                     print(f"🛑 Attempting to revoke scheduled task id={task_id}")
#                     celery_app.control.revoke(task_id, terminate=False)
#                     print("✅ Revoke requested")
#             except Exception as e:
#                 print(f"⚠️ Error while revoking scheduled task: {e}")

#             print(f"⏳ Updated SLA End Time after Hold: {current_log.sla_end_time}")
#             return

#         # 5️⃣ SLA End time assignment (if not set)
#         if not current_log.sla_end_time:
#             print("⚙️ SLA END TIME not set. Setting now.")
#             sla_text = getattr(sla, f"Approver_level{approver_level}_time")
#             hours = parse_sla_time_to_hours(sla_text)

#             current_log.sla_end_time = add_sla_time_skipping_holidays(
#                 current_log.created_on or timezone.now(),
#                 hours
#             )
#             current_log.save()
#             print(f"⏳ SLA End Time Set → {current_log.sla_end_time}")

#             # schedule this SLA check and store task id (best-effort)
#             delay_seconds = max(1, int((current_log.sla_end_time - timezone.now()).total_seconds()))
#             print(f"🕑 Scheduling SLA check for this level in {delay_seconds} seconds")
#             result = handle_sla_escalation.apply_async(args=[ticket.id, approver_level], countdown=delay_seconds)
#             try:
#                 current_log.scheduled_task_id = result.id
#                 current_log.save()
#                 print(f"🔖 Stored scheduled_task_id = {result.id} on TicketApprovalLog id={current_log.id}")
#             except Exception:
#                 print("⚠️ scheduled_task_id field not present — skipping store.")
#             return

#         # 6️⃣ Check SLA breach
#         now = timezone.now()
#         print("\n" + "-"*60)
#         print("⏰ SLA TIMER CHECK")
#         print("-"*60)
#         print(f"Current Time: {now}")
#         print(f"SLA End Time: {current_log.sla_end_time}")

#         if now >= current_log.sla_end_time:
#             print(f"❌ SLA BREACHED for Level {approver_level} (log id={current_log.id})")
#             # mark current as timeout
#             current_log.status = "Timeout"
#             current_log.sla_breach = True
#             current_log.approval_status = "Timeout"
#             current_log.is_current_level = False
#             current_log.save()

#             # get next approver
#             next_level = approver_level + 1
#             next_user = getattr(sla, f"Approver_level{next_level}_user", None)

#             if not next_user:
#                 print("🏁 Final approver breached. Closing ticket.")
#                 ticket.status = "Closed - Final Level Breached"
#                 ticket.save()
#                 return

#             print(f"➡️ Moving to Next Approver after Breach → Level {next_level} (user_id={next_user.id})")

#             # 7️⃣ Create/assign next approval log
#             level_sla_text = getattr(sla, f"Approver_level{next_level}_time")
#             next_sla_hours = parse_sla_time_to_hours(level_sla_text)

#             with transaction.atomic():
#                 print("🔄 Making previous levels non-current...")
#                 TicketApprovalLog.objects.filter(ticket=ticket).update(is_current_level=False)

#                 print("➕ Creating/Updating next level log...")
#                 next_log, created = TicketApprovalLog.objects.update_or_create(
#                     ticket=ticket,
#                     current_level=next_level,
#                     defaults={
#                         'sla': sla,
#                         'created_by_id': next_user.id,
#                         'status': "Pending",
#                         'approval_status': "Pending",
#                         'is_current_level': True,
#                         'comments': f"Assigned to Level {next_level} approver: {next_user.email}",
#                         'created_on': timezone.now(),
#                         'sla_end_time': add_sla_time_skipping_holidays(timezone.now(), next_sla_hours)
#                     }
#                 )

#             print(f"⏳ Next Approver SLA End Time: {next_log.sla_end_time}")

#             # 8️⃣ Send email to next approver
#             print("📧 Sending escalation/approval email to next approver...")
#             template_obj = TicketEmailTemplate.objects.filter(email_event__iexact="Approval", is_active="Y").first()
#             if template_obj:
#                 ctx = Context({
#                     'firstname': ticket.requested.firstname or ticket.requested.email,
#                     'realname': getattr(ticket.requested, "realname", ""),
#                     'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#                     'name': ticket.title or ticket.description or "N/A",
#                     'ticket_url': f"http://yourdomain.com/tickets/{ticket.id}",
#                     'mail_signature': 'IT Support Team',
#                     'year': timezone.now().year
#                 })
#                 html_content = Template(template_obj.email_template).render(ctx)
#                 send_email_task.delay([next_user.email], f"Approval Request - Ticket #{ticket.ticket_no}", html_content)
#                 print("✅ Email queued to next approver")
#             else:
#                 print("⚠️ No approval email template found; skipping email send.")

#             # 9️⃣ Schedule SLA for next level
#             delay_seconds = max(1, int((next_log.sla_end_time - timezone.now()).total_seconds()))
#             print(f"🕑 Scheduling SLA escalation for next level in {delay_seconds} seconds.")
#             result = handle_sla_escalation.apply_async(args=[ticket.id, next_level], countdown=delay_seconds)
#             try:
#                 next_log.scheduled_task_id = result.id
#                 next_log.save()
#                 print(f"🔖 Stored scheduled_task_id = {result.id} on TicketApprovalLog id={next_log.id}")
#             except Exception:
#                 print("⚠️ scheduled_task_id field not present — skipping store.")

#             return

#         print("🏁 SLA Task Execution Completed.")

#     except Exception as e:
#         print(f"💥 ERROR in SLA Escalation Task: {e}")
#         raise self.retry(exc=e, countdown=30)


# def escalate_to_next_approver(ticket, current_level, reason="approval"):
#     print(f"\n{'='*80}")
#     print(f"ESCALATING | Ticket #{ticket.ticket_no} | From Level {current_level} | Reason: {reason}")
#     print(f"{'='*80}")

#     sla = ticket.sla
#     next_level = current_level + 1
#     next_user = getattr(sla, f"Approver_level{next_level}_user", None)

#     if not next_user:
#         print("FINAL LEVEL → TICKET APPROVED")
#         approved_status = TicketsMasterConfiguration.objects.filter(
#             field_type__iexact='Status', field_values__iexact='Approved', is_active='Y'
#         ).first()
#         if approved_status:
#             ticket.status = approved_status
#             ticket.save()
#         return

#     hours = parse_sla_time_to_hours(getattr(sla, f"Approver_level{next_level}_time") or "1 hour")
#     end_time = add_sla_time_skipping_holidays(timezone.now(), hours)

#     with transaction.atomic():
#         TicketApprovalLog.objects.filter(ticket=ticket).update(is_current_level=False)
#         next_log, _ = TicketApprovalLog.objects.update_or_create(
#             ticket=ticket,
#             current_level=next_level,
#             defaults={
#                 'sla': sla,
#                 'created_by_id': next_user.id,
#                 'status': "Pending",
#                 'approval_status': "Pending",
#                 'is_current_level': True,
#                 'comments': f"Level {next_level} - {reason}",
#                 'created_on': timezone.now(),
#                 'sla_end_time': end_time,
#             }
#         )
#         print(f"LEVEL {next_level} READY → {next_user.email} | Deadline: {end_time}")

#     # Email
#     template = TicketEmailTemplate.objects.filter(email_event__iexact="Approval", is_active="Y").first()
#     if template and next_user.email:
#         ctx = Context({
#             'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
#             'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#             'name': ticket.title or "Ticket",
#             'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
#             'mail_signature': 'IT Support Team',
#             'year': timezone.now().year,
#         })
#         html = Template(template.email_template).render(ctx)
#         send_email_task.delay([next_user.email], f"Approval Request - Ticket #{ticket.ticket_no}", html)
#         print(f"EMAIL SENT → {next_user.email}")

#     # Schedule next check
#     delay = max(1, int((next_log.sla_end_time - timezone.now()).total_seconds()))
#     handle_sla_escalation.apply_async(args=[ticket.id, next_level], countdown=delay)
#     print(f"SLA TASK SCHEDULED FOR LEVEL {next_level} IN {delay}s")


# # ============================================================
# # MAIN SLA ESCALATION TASK
# # ============================================================
# @shared_task(bind=True)
# def handle_sla_escalation(self, ticket_id, approver_level):
#     print(f"\n{'*'*100}")
#     print(f"SLA CHECK | Ticket: {ticket_id} | Level: {approver_level} | Time: {timezone.now()}")
#     print(f"{'*'*100}")

#     try:
#         ticket = CreateTicket.objects.select_related('sla').get(id=ticket_id)
#         if not ticket.sla:
#             return

#         log = TicketApprovalLog.objects.filter(
#             ticket=ticket,
#             current_level=approver_level,
#             is_current_level=True,
#             approval_status__in=["Pending", "On-Hold"]
#         ).first()

#         if not log:
#             print(f"NO ACTIVE LOG → OLD TASK IGNORED")
#             return

#         # CRITICAL GUARD — prevents duplicates
#         if log.approval_status not in ["Pending", "On-Hold"]:
#             print(f"ALREADY {log.approval_status} → OLD TASK IGNORED")
#             return

#         # On-Hold?
#         if log.onhold_start:
#             print(f"ON HOLD SINCE {log.onhold_start} → NO ACTION")
#             return

#         now = timezone.now()

#         # First visit?
#         if not log.sla_end_time:
#             hours = parse_sla_time_to_hours(getattr(ticket.sla, f"Approver_level{approver_level}_time"))
#             end_time = add_sla_time_skipping_holidays(now, hours)
#             log.sla_end_time = end_time
#             log.save()
#             delay = max(1, int((end_time - now).total_seconds()))
#             handle_sla_escalation.apply_async(args=[ticket.id, approver_level], countdown=delay)
#             print(f"SLA SET → {end_time} | Next check in {delay}s")
#             return

#         # BREACH!
#         if now >= log.sla_end_time:
#             print(f"SLA BREACHED AT LEVEL {approver_level}!!")
#             log.status = "Timeout"
#             log.approval_status = "Timeout"
#             log.sla_breach = True
#             log.is_current_level = False
#             log.save()
#             escalate_to_next_approver(ticket, approver_level, reason="SLA_BREACH")
#             return

#         print(f"Still waiting... Deadline: {log.sla_end_time}")

#     except Exception as e:
#         print(f"SLA TASK ERROR: {e}")
#         raise self.retry(exc=e, countdown=60)

def escalate_to_next_approver(ticket, current_level, reason="approval", bonus_seconds=0):
    sla = ticket.sla
    next_level = current_level + 1
    next_user = getattr(sla, f"Approver_level{next_level}_user", None)

    if not next_user:
        # FINAL APPROVAL → ASSIGN TO TECHNICIAN
        tech_status = TicketsMasterConfiguration.objects.filter(
            field_type__iexact='Status', field_values__iexact='Assigned to Technician', is_active='Y'
        ).first() or TicketsMasterConfiguration.objects.filter(
            field_type__iexact='Status', field_values__iexact='Approved', is_active='Y'
        ).first()
        if tech_status:
            ticket.status = tech_status
            ticket.save()
        print(f"TICKET #{ticket.ticket_no} → ASSIGNED TO TECHNICIAN")
        return

    base_hours = parse_sla_time_to_hours(getattr(sla, f"Approver_level{next_level}_time") or "1 hour")
    bonus_hours = bonus_seconds / 3600.0
    total_hours = base_hours + bonus_hours
    end_time = add_sla_time_skipping_holidays(timezone.now(), total_hours)

    with transaction.atomic():
        TicketApprovalLog.objects.filter(ticket=ticket).update(is_current_level=False)
        next_log, _ = TicketApprovalLog.objects.update_or_create(
            ticket=ticket,
            current_level=next_level,
            defaults={
                'sla': sla,
                'created_by_id': next_user.id,
                'status': "Pending",
                'approval_status': "Pending",
                'is_current_level': True,
                'comments': f"Level {next_level} (+{bonus_seconds}s bonus) - {reason}",
                'created_on': timezone.now(),
                'sla_end_time': end_time,
            }
        )

    # Approval email to next
    template = TicketEmailTemplate.objects.filter(email_event="Approval", is_active="Y").first()
    if template and next_user.email:
        ctx = Context({
            'firstname': ticket.requested.firstname or "User",
            'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y"),
            'name': ticket.title or "Ticket",
            'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
            'mail_signature': 'IT Support Team',
        })
        html = Template(template.email_template).render(ctx)
        send_email_task.delay([next_user.email], f"Approval Request - Ticket #{ticket.ticket_no}", html)
        handle_sla_escalation.apply_async(
                args=[ticket.id, next_level],
                eta=end_time
            )
    # Schedule next SLA
    # delay = max(1, int((end_time - timezone.now()).total_seconds()))
    # handle_sla_escalation.apply_async(args=[ticket.id, next_level], countdown=delay)
   

@shared_task(bind=True)
def handle_sla_escalation(self, ticket_id, approver_level):
    try:
        ticket = CreateTicket.objects.select_related('sla').get(id=ticket_id)
        log = TicketApprovalLog.objects.filter(
            ticket=ticket,
            current_level=approver_level,
            is_current_level=True,
            approval_status__in=["Pending", "On-Hold"]
        ).first()

        if not log or log.approval_status not in ["Pending", "On-Hold"]:
            return

        if log.onhold_start:
            return

        # now = timezone.now()

        # # FIRST TIME → set deadline and keep checking
        # if not log.sla_end_time:
        #     hours = parse_sla_time_to_hours(getattr(ticket.sla, f"Approver_level{approver_level}_time"))
        #     log.sla_end_time = add_sla_time_skipping_holidays(now, hours)
        #     log.save()

        # # ALWAYS RE-SCHEDULE FOR NEXT CHECK (every 60 seconds)
        # delay = 60
        # handle_sla_escalation.apply_async(args=[ticket.id, approver_level], countdown=delay)

        # # BREACH CHECK
        # if now >= log.sla_end_time:
        #     print(f"SLA BREACHED AT LEVEL {approver_level}!!")
        now = timezone.now()

        # FIRST TIME → set deadline
        if not log.sla_end_time:
            hours = parse_sla_time_to_hours(getattr(ticket.sla, f"Approver_level{approver_level}_time"))
            log.sla_end_time = add_sla_time_skipping_holidays(now, hours)
            log.save()

        # SCHEDULE TASK TO RUN EXACTLY AT THE DEADLINE (CRITICAL FIX)
        if log.sla_end_time:
            delay = max(1, int((log.sla_end_time - timezone.now()).total_seconds()))
            handle_sla_escalation.apply_async(args=[ticket.id, approver_level], countdown=delay)

        # BREACH CHECK — will now trigger EXACTLY on time
        if now >= log.sla_end_time:
            print(f"SLA BREACHED AT LEVEL {approver_level}!!")
            # ... rest of your breach logic (unchanged) ...

            # Breach mail
            breach_template = TicketEmailTemplate.objects.filter(email_event="SLA Breached", is_active="Y").first()
            if breach_template and log.created_by and log.created_by.email:
                ctx = Context({
                    'ticket_id': ticket.ticket_no,
                    'ticket': {
                        'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
                        'realname': getattr(ticket.requested, 'realname', '') or '',
                        'date_creation': timezone.localtime(ticket.created_date),
                        'name': ticket.title or ticket.description or "No Title",
                        'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                        'mail_signature': 'IT Support Team',
                    },
                    'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                })
                html = Template(breach_template.email_template).render(ctx)
                send_email_task.delay([log.created_by.email], f"SLA Breached - Ticket #{ticket.ticket_no}", html)

            log.status = "Timeout"
            log.approval_status = "Timeout"
            log.sla_breach = True
            # log.is_current_level = False
            log.save()

            next_user = getattr(ticket.sla, f"Approver_level{approver_level + 1}_user", None)
            if not next_user:
                # FINAL SLA BREACH → AUTO-CLOSE TICKET
                closed_status = TicketsMasterConfiguration.objects.filter(
                    field_type__iexact='Status',
                    field_values__iexact='Closed',
                    is_active='Y'
                ).first()

                if closed_status:
                    ticket.status = closed_status
                    ticket.closed_on = timezone.now()
                    ticket.save()

                    # ONLY REQUESTER GETS "Ticket Closed" EMAIL
                    closed_template = TicketEmailTemplate.objects.filter(email_event="Ticket Closed", is_active="Y").first()
                    if closed_template and ticket.requested.email:
                        ctx = Context({
                            'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
                            'realname': getattr(ticket.requested, 'realname', '') or '',
                            'ticket_no': ticket.ticket_no,
                            'name': ticket.title or ticket.description or "Ticket",
                            'date_creation': ticket.created_date,   
                            'closed_date': ticket.closed_on,
                            'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                            'mail_signature': 'IT Support Team',
                            'reason': 'This ticket was automatically closed due to SLA timeout at the final approval level.',
                            'year': timezone.now().year,
                            
                        })
                        html = Template(closed_template.email_template).render(ctx)
                        send_email_task.delay(
                            [ticket.requested.email],
                            f"Ticket #{ticket.ticket_no} Closed - SLA Timeout",
                            html
                        )

                        # Optional: Notify watchers
                        watcher_emails = [w.email for w in ticket.watchers.all() if w.email]
                        if watcher_emails:
                            send_email_task.delay(watcher_emails, f"Ticket #{ticket.ticket_no} Closed", html)

                print(f"FINAL SLA BREACH → TICKET #{ticket.ticket_no} AUTO-CLOSED & Requester Notified")
                return

            # ESCALATE WITH 0 BONUS
            escalate_to_next_approver(ticket, approver_level, reason="SLA_BREACH", bonus_seconds=0)
            # handle_sla_escalation.apply_async(
            #     args=[ticket_id, approver_level],
            #     eta=log.sla_end_time
            # )
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
