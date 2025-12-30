# # views.py (Using APIView for Custom Control)
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.renderers import JSONRenderer
# from .models import TicketPanel
# from .serializers import TicketPanelSerializer

# class TicketPanelCreateView(APIView):
#     parser_classes = [MultiPartParser, FormParser]
#     renderer_classes = [JSONRenderer]

#     def post(self, request, *args, **kwargs):
#         serializer = TicketPanelSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             response_data = {
#                 'panel_id': serializer.instance.id,
#                 'screenshot_url': request.build_absolute_uri(serializer.instance.imageupload.url) if serializer.instance.imageupload else None,
#                 'stored_payload_preview': {k: v for k, v in serializer.instance.raw_payload.items() if k != 'imageupload'}
#             }
#             return Response(response_data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class TicketPanelListView(APIView):
#     renderer_classes = [JSONRenderer]

#     def get(self, request, *args, **kwargs):
#         queryset = TicketPanel.objects.all().order_by('-created_date')
#         serializer = TicketPanelSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)

# class TicketPanelRetrieveView(APIView):
#     renderer_classes = [JSONRenderer]

#     def get(self, request, pk, *args, **kwargs):
#         try:
#             instance = TicketPanel.objects.get(pk=pk)
#         except TicketPanel.DoesNotExist:
#             return Response({'error': 'Panel not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = TicketPanelSerializer(instance, context={'request': request})
#         return Response(serializer.data)

# views.py (Using APIView for Custom Control - No Serializer)
# 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from .models import TicketPanel
from django.http import Http404
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
# Additional imports for ticket creation
from Ticket.models import CreateTicket, TicketsMasterConfiguration, TicketSLA, TicketApprovalLog, TicketEmailTemplate
from Ticket.serializers import CreateTicketSerializer  # Assuming in same app; adjust if needed
from django.contrib.auth.models import User
from django.db import transaction
import logging
logger = logging.getLogger(__name__)
from django.utils import timezone
from django.template import Template, Context
from Ticket.tasks import send_email_task # Adjust import path as needed
from django.conf import settings
from datetime import timedelta  # For dummy utils

# Dummy implementations for missing utils (replace with actual if available)
def parse_sla_time_to_hours(sla_text):
    # Example: "8 hours" -> 8; adjust parsing as needed
    if sla_text:
        try:
            return float(sla_text.split()[0])
        except:
            return 0
    return 0

def add_sla_time_skipping_holidays(start_time, hours):
    # Simple addition without holiday skipping for now
    return start_time + timedelta(hours=hours)

class TicketPanelCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        # Extract file
        image_file = request.FILES.get('imageupload')

        # Manual validation for required fields
        required_fields = ['name', 'message', 'paneltype']
        errors = {}
        for field in required_fields:
            if field not in request.data or not str(request.data[field]).strip():
                errors[field] = f'{field} is required and cannot be empty.'

        # Handle image validation
        image_errors = {}
        if image_file:
            if not image_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_errors['imageupload'] = 'Only PNG/JPG screenshots allowed.'

        # Prepare raw_payload always (include errors for inspect/error handling)
        raw_payload = {}
        for k, v in request.data.items():
            if not isinstance(v, (UploadedFile, InMemoryUploadedFile)):
                raw_payload[k] = str(v)  # Ensure serializable as string
            else:
                # For files, store metadata (include error if any)
                raw_payload[k] = {
                    'filename': v.name,
                    'size': v.size,
                    'content_type': v.content_type
                }
                if image_errors:
                    raw_payload[k]['error'] = list(image_errors.values())[0]

        # Add errors to raw_payload for inspect/error display
        if errors or image_errors:
            raw_payload['validation_errors'] = {**errors, **image_errors}
            raw_payload['inspect_mode'] = 'error'  # Flag for error-based screenshot

        # Check if full validation passes
        full_valid = not (errors or image_errors)

        api_errors = None
        ticket_id = None
        ticket_no = None

        if full_valid:
            # Normal full creation
            try:
                instance = TicketPanel.objects.create(
                    name=request.data['name'],
                    department=request.data.get('department', ''),
                    location=request.data.get('location', ''),
                    role=request.data.get('role', ''),
                    imageupload=image_file,
                    message=request.data['message'],
                    paneltype=request.data['paneltype'],
                    raw_payload=raw_payload
                )
                status_code = status.HTTP_201_CREATED

                # Automatically create corresponding CreateTicket using serializer and post logic
                try:
                    with transaction.atomic():
                        department_value = request.data.get('department', '').strip()
                        location_value = request.data.get('location', '').strip()
                        panel_type_value = request.data['paneltype'].strip()

                        # Helper function to get or create FK object: prefer ID if numeric, else lookup/create by field_type/field_values or field_name
                        def get_or_create_fk_obj(value, fk_type):
                            if not value:
                                return None
                            field_type_map = {
                                'department': 'Department',
                                'location': 'Location',
                                'type': 'TicketType',
                            }
                            try:
                                if value.isdigit():
                                    obj = TicketsMasterConfiguration.objects.get(id=int(value))
                                    # Validate type
                                    expected_ft = field_type_map.get(fk_type)
                                    if expected_ft and obj.field_type != expected_ft:
                                        obj = None
                                    return obj
                                else:
                                    ft = field_type_map.get(fk_type)
                                    if ft:
                                        obj = TicketsMasterConfiguration.objects.filter(field_type=ft, field_values=value).first()
                                        if not obj:
                                            obj = TicketsMasterConfiguration.objects.filter(field_type=ft, field_name=value).first()
                                        if not obj:
                                            # Create if not found (ensure required fields; add more if model requires)
                                            obj = TicketsMasterConfiguration.objects.create(
                                                field_type=ft,
                                                field_values=value,
                                                field_name=value,  # Duplicate for compatibility
                                                is_active='Y'
                                            )
                                            logger.info(f"Created {ft} entry for '{value}' (ID: {obj.id})")
                                        return obj
                                    return None
                            except (ValueError, TicketsMasterConfiguration.DoesNotExist) as e:
                                logger.error(f"Error getting/creating {fk_type} for '{value}': {e}")
                                return None

                        type_obj = get_or_create_fk_obj(panel_type_value, 'type')
                        department_obj = get_or_create_fk_obj(department_value, 'department')
                        location_obj = get_or_create_fk_obj(location_value, 'location')

                        # Ensure type_obj is not None (required); fallback to first if create failed
                        if not type_obj:
                            type_obj = TicketsMasterConfiguration.objects.filter(field_type='TicketType').first()
                            if not type_obj:
                                type_obj = TicketsMasterConfiguration.objects.create(
                                    field_type='TicketType',
                                    field_values='Default',
                                    field_name='Default',
                                    is_active='Y'
                                )
                                logger.info(f"Created default TicketType (ID: {type_obj.id})")

                        # Default priority (get or create)
                        priority_ft = 'Priority'
                        priority_obj = (TicketsMasterConfiguration.objects
                                        .filter(field_type=priority_ft, field_values='Medium').first() or
                                        TicketsMasterConfiguration.objects
                                        .filter(field_type=priority_ft, field_name='Medium').first())
                        if not priority_obj:
                            priority_obj = TicketsMasterConfiguration.objects.create(
                                field_type=priority_ft,
                                field_values='Medium',
                                field_name='Medium',
                                is_active='Y'
                            )
                            logger.info(f"Created default Priority 'Medium' (ID: {priority_obj.id})")

                        # Default status (get or create Pending)
                        status_ft = 'Status'
                        pending_status = (TicketsMasterConfiguration.objects
                                          .filter(field_type__iexact=status_ft, field_values__iexact='Pending').first() or
                                          TicketsMasterConfiguration.objects
                                          .filter(field_type__iexact=status_ft, field_name__iexact='Pending').first())
                        if not pending_status:
                            pending_status = TicketsMasterConfiguration.objects.create(
                                field_type=status_ft,
                                field_values='Pending',
                                field_name='Pending',
                                is_active='Y'
                            )
                            logger.info(f"Created default Status 'Pending' (ID: {pending_status.id})")

                        # Map category_id (customize as needed)
                        category_mapping = {'Stemz': 1, 'ND': 1, 'approval': 2}  # Add more based on paneltype
                        category_id = category_mapping.get(panel_type_value, 1)
                        subcategory_id = None

                        # Prepare data for serializer: PKs (ints) for FK fields expecting them, str for status
                        ticket_data = {
                            'type': type_obj.id,  # int PK
                            'department': department_obj.id if department_obj else None,
                            'location': location_obj.id if location_obj else None,
                            'priority': priority_obj.id,  # int PK
                            'category_id': category_id,
                            'subcategory_id': subcategory_id,
                            'title': request.data['name'],
                            'description': request.data['message'],
                            'assignee': str(request.data.get('role', '')),
                            'status': 'Pending',  # str for CharField in serializer
                            'watchers': [],  # Empty
                        }

                        # Use serializer for creation (handles sla, etc.)
                        ticket_serializer = CreateTicketSerializer(data=ticket_data, context={'request': request})
                        ticket_serializer.is_valid(raise_exception=True)

                        # FIXED: Override validated_data with instances for PK-based FK fields to avoid assignment error
                        modified_vd = ticket_serializer._validated_data.copy()
                        modified_vd['type'] = type_obj
                        modified_vd['department'] = department_obj
                        modified_vd['location'] = location_obj
                        modified_vd['priority'] = priority_obj
                        # FIXED: Handle status string -> instance conversion
                        status_str = modified_vd.get('status')
                        if isinstance(status_str, str):
                            modified_vd['status'] = pending_status
                        # 'status' now instance; serializer's create() will use it
                        ticket_serializer._validated_data = modified_vd

                        ticket = ticket_serializer.save(requested=request.user if request.user and request.user.is_authenticated else None)
                        logger.info(f"🎫 Ticket #{ticket.ticket_no} created by panel (user: {getattr(request.user, 'username', 'anonymous')})")

                        # Additional post-creation logic (mimic CreateTicketView.post)
                        sla = ticket.sla
                        if not sla:
                            sla = TicketSLA.objects.filter(
                                category_id=category_id,
                                subcategory_id=subcategory_id,
                                is_active="Y",
                            ).first()
                            if sla:
                                ticket.sla = sla
                                ticket.save()

                        if sla:
                            approver_ids = [
                                getattr(sla, "Approver_level1_user_id"),
                                getattr(sla, "Approver_level2_user_id"),
                                getattr(sla, "Approver_level3_user_id"),
                                getattr(sla, "Approver_level4_user_id"),
                                getattr(sla, "Approver_level5_user_id"),
                            ]
                            approvers = list(User.objects.filter(id__in=[a for a in approver_ids if a]))
                            if approvers:
                                ticket.total_approval_levels = len(approvers)
                                ticket.save()

                                # Create Approval Logs
                                for i, approver in enumerate(approvers):
                                    TicketApprovalLog.objects.create(
                                        ticket=ticket,
                                        sla=sla,
                                        current_level=i + 1,
                                        is_current_level=(i == 0),
                                        status="Pending" if i == 0 else "Waiting",
                                        approval_status="Pending",
                                        created_by=approver,
                                        created_on=timezone.now(),
                                    )

                                # Emails and scheduling if authenticated
                                if request.user and request.user.is_authenticated:
                                    requester_email = request.user.email
                                    requester_name = f"{(getattr(request.user, 'firstname', '') or '')} {(getattr(request.user, 'realname', '') or '')}".strip() or "Requester"
                                else:
                                    requester_email = None
                                    requester_name = "System"

                                # Requester Email
                                if requester_email:
                                    ticket_created_template = TicketEmailTemplate.objects.filter(email_event="Ticket_Created", is_active="Y").first()
                                    if ticket_created_template:
                                        template = Template(ticket_created_template.email_template)
                                        ticket_context = {
                                            "firstname": requester_name,
                                            "realname": "",
                                            "ticket_no": ticket.ticket_no,
                                            "name": ticket.title or ticket.description,
                                            "date_creation": timezone.localtime(ticket.created_date),
                                            "ticket_url": request.build_absolute_uri(f"/tickets/{ticket.id}/"),
                                            "mail_signature": "IT Support Team",
                                        }
                                        html_content = template.render(Context({"ticket": ticket_context}))
                                        send_email_task.delay(
                                            [requester_email],
                                            f"Ticket #{ticket.ticket_no} Created Successfully",
                                            html_content,
                                            cc=[]
                                        )
                                        logger.info(f"📧 Ticket Created email sent to {requester_email}")

                                # First Approver Email
                                if approvers:
                                    first_approver = approvers[0]
                                    first_approver_email = getattr(first_approver, "email", None)
                                    if first_approver_email:
                                        approval_template = TicketEmailTemplate.objects.filter(email_event="Approval", is_active="Y").first()
                                        if approval_template:
                                            template = Template(approval_template.email_template)
                                            approver_context = {
                                                "firstname": requester_name.split(" ")[0] or requester_name,
                                                "realname": " ",
                                                "date_creation": timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
                                                "name": ticket.description or ticket.title or "No description provided",
                                                "ticket_url": request.build_absolute_uri(f"/tickets/{ticket.id}/"),
                                                "mail_signature": "IT Support Team",
                                                "year": timezone.now().year,
                                            }
                                            html_content = template.render(Context(approver_context))
                                            send_email_task.delay(
                                                [first_approver_email],
                                                f"Approval Request - Ticket #{ticket.ticket_no}",
                                                html_content,
                                                cc=[]
                                            )
                                            logger.info(f"📧 Approval email sent to {first_approver_email}")

                                # Schedule SLA Escalation for Level 1
                                first_sla_text = getattr(sla, "Approver_level1_time", None)
                                first_approver_user = getattr(sla, "Approver_level1_user", None)
                                if first_sla_text and first_approver_user:
                                    try:
                                        hours = parse_sla_time_to_hours(first_sla_text)
                                        start_time = ticket.created_date
                                        adjusted_end = add_sla_time_skipping_holidays(start_time, hours)
                                        delay_seconds = max(0, (adjusted_end - timezone.now()).total_seconds())
                                        handle_sla_escalation.apply_async(
                                            args=[ticket.id, 1],
                                            countdown=int(delay_seconds)
                                        )
                                        logger.info(f"⏱ SLA escalation scheduled for Ticket #{ticket.ticket_no} (Level 1) after {hours} hours")
                                    except Exception as esc_e:
                                        logger.warning(f"⚠️ SLA scheduling failed for Ticket #{ticket.ticket_no}: {esc_e}")
                                else:
                                    logger.warning(f"⚠️ No SLA time or approver for Level 1 of Ticket #{ticket.ticket_no}")
                        else:
                            logger.warning(f"⚠️ No SLA found for Ticket #{ticket.ticket_no}")

                    ticket_id = ticket.id
                    ticket_no = ticket.ticket_no

                    # Store ticket reference in raw_payload
                    raw_payload['created_ticket_id'] = ticket_id
                    raw_payload['created_ticket_no'] = ticket_no
                    instance.raw_payload = raw_payload
                    instance.save(update_fields=['raw_payload'])
                    logger.info(f"Updated TicketPanel {instance.id} with ticket {ticket_id}/{ticket_no}")

                except Exception as ticket_e:
                    ticket_error_msg = f'Ticket creation failed: {str(ticket_e)}'
                    raw_payload['ticket_creation_error'] = ticket_error_msg
                    instance.raw_payload = raw_payload
                    instance.save(update_fields=['raw_payload'])
                    api_errors = {'ticket_creation': ticket_error_msg}
                    logger.error(ticket_error_msg)

            except Exception as e:
                return Response({'error': f'Database error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Partial save on error: save what we can, store errors in raw_payload and message
            partial_message = request.data.get('message', '') or 'Partial save due to validation errors'
            partial_message += f'\nErrors: {str({**errors, **image_errors})}'
            try:
                instance = TicketPanel.objects.create(
                    name=request.data.get('name', 'Unnamed (Error Capture)'),
                    department=request.data.get('department', ''),
                    location=request.data.get('location', ''),
                    role=request.data.get('role', ''),
                    imageupload=image_file if not image_errors else None,  # Skip invalid image
                    message=partial_message,
                    paneltype=request.data.get('paneltype', 'error'),
                    raw_payload=raw_payload
                )
                status_code = status.HTTP_400_BAD_REQUEST  # Still error status, but data saved
                api_errors = {**errors, **image_errors}
                # No ticket creation on partial validation failure
            except Exception as e:
                # Fallback: minimal creation if even partial fails
                fallback_payload = {**raw_payload, 'fallback_error': str(e)}
                instance = TicketPanel.objects.create(
                    name='Fallback Error Capture',
                    message=f'Validation and DB errors: {str(e)}',
                    paneltype='fallback_error',
                    raw_payload=fallback_payload
                )
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                api_errors = {'general': 'Fallback save performed due to multiple issues.'}

        # Build response data (common for all cases)
        screenshot_url = request.build_absolute_uri(instance.imageupload.url) if instance.imageupload else None
        stored_preview = {k: v for k, v in instance.raw_payload.items() if k != 'imageupload'}

        response_data = {
            'panel_id': instance.id,
            'screenshot_url': screenshot_url,
            'stored_payload_preview': stored_preview,
            'saved_successfully': full_valid,
            'errors': api_errors,
            'inspect_data': raw_payload.get('validation_errors', None),  # Expose errors for frontend inspect display
            'ticket_id': ticket_id,
            'ticket_no': ticket_no,
        }
        return Response(response_data, status=status_code)

class TicketPanelListView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        queryset = TicketPanel.objects.all().order_by('-created_date')
        data = []
        for obj in queryset:
            screenshot_url = request.build_absolute_uri(obj.imageupload.url) if obj.imageupload else None
            # Add inspect/error flag if present in raw_payload
            inspect_flag = obj.raw_payload.get('inspect_mode') if obj.raw_payload else None
            item = {
                'id': obj.id,
                'name': obj.name,
                'department': obj.department,
                'location': obj.location,
                'role': obj.role,
                'imageupload': obj.imageupload.name if obj.imageupload else None,
                'screenshot_url': screenshot_url,
                'message': obj.message,
                'paneltype': obj.paneltype,
                'raw_payload': obj.raw_payload,
                'inspect_mode': inspect_flag,  # For error-based display
                'created_date': obj.created_date.isoformat() if obj.created_date else None,
                'updated_date': obj.updated_date.isoformat() if obj.updated_date else None
            }
            data.append(item)
        return Response(data)

class TicketPanelRetrieveView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, pk, *args, **kwargs):
        try:
            instance = TicketPanel.objects.get(pk=pk)
        except TicketPanel.DoesNotExist:
            return Response({'error': 'Panel not found'}, status=status.HTTP_404_NOT_FOUND)

        screenshot_url = request.build_absolute_uri(instance.imageupload.url) if instance.imageupload else None
        # Add inspect/error flag if present in raw_payload
        inspect_flag = instance.raw_payload.get('inspect_mode') if instance.raw_payload else None
        data = {
            'id': instance.id,
            'name': instance.name,
            'department': instance.department,
            'location': instance.location,
            'role': instance.role,
            'imageupload': instance.imageupload.name if instance.imageupload else None,
            'screenshot_url': screenshot_url,
            'message': instance.message,
            'paneltype': instance.paneltype,
            'raw_payload': instance.raw_payload,
            'inspect_mode': inspect_flag,  # For error-based display
            'created_date': instance.created_date.isoformat() if instance.created_date else None,
            'updated_date': instance.updated_date.isoformat() if instance.updated_date else None
        }
        return Response(data)