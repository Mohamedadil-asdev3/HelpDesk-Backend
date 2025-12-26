
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.template import Template, Context
from .models import TicketsMasterConfiguration , TicketCategory, TicketSubcategory,CreateTicket,Entity,TicketApprovalLog,TicketSLA,TicketEmailTemplate,TicketDocument,Holiday
from Authenticate.models import User,UsersGroup
from .serializers import TicketsMasterConfigurationSerializer, TicketDocumentSerializer,TicketCategorySerializer,TicketSubcategorySerializer,TicketSLASerializer,CreateTicketSerializer,EntitySerializer,DepartmentSerializer,UserSerializer,TicketApprovalLogSerializer,TicketEmailTemplateSerializer,HolidaySerializer,RoleSerializer
from .models import TicketsMasterConfiguration , TicketCategory, TicketSubcategory,CreateTicket,Entity,TicketApprovalLog,TicketSLA,TicketEmailTemplate,TicketDocument,Role,UserRoleMapping,Message
# from Authenticate.models import User,UsersGroup,Holiday
from .serializers import TicketsMasterConfigurationSerializer, TicketDocumentSerializer,TicketCategorySerializer,TicketSubcategorySerializer,TicketSLASerializer,CreateTicketSerializer,EntitySerializer,DepartmentSerializer,UserSerializer,TicketApprovalLogSerializer,TicketEmailTemplateSerializer,HolidaySerializer,RoleSerializer,UserRoleMappingSerializer,MessageSerializer,PlatformSerializer
from Authenticate.serializers import UsersGroupSerializer,WatcherUserSerializer
from django.utils import timezone
import logging
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F,Q
from .tasks import send_email_task, send_email_task
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model() 
logger = logging.getLogger(__name__)

from django.db import models
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils import timezone
from .models import TicketsMasterConfiguration  # Assuming the model is imported correctly
# from  Approval.analyse import GlpiUsers

# class LocationByCountryAPIView(APIView):
#     """
#     Handles GET, POST, PUT, and DELETE requests for locations of a given entity
#     """
#     permission_classes = [AllowAny]

#     def get(self, request):
#         """
#         GET: Return all locations, optionally filtered by entity_id
#         """
#         entity_id = request.query_params.get('entity_id') or request.data.get('entity_id')

#         if entity_id:
#             locations = TicketsMasterConfiguration.objects.filter(
#                 field_type="Location",
#                 entity_id=entity_id,
#             ).annotate(entity_name=F('entity__name')).values(
#                 "id",
#                 "entity_id",
#                 "entity_name",
#                 "referrence_to",
#                 "field_name",
#                 "field_values",
#                 "is_mandatory",
#                 "is_active"
#             )
#         else:
#             locations = TicketsMasterConfiguration.objects.filter(
#                 field_type="Location",
#             ).annotate(entity_name=F('entity__name')).values(
#                 "id",
#                 "entity_id",
#                 "entity_name",
#                 "referrence_to",
#                 "field_name",
#                 "field_values",
#                 "is_mandatory",
#                 "is_active"
#             )

#         return Response(list(locations))

#     def post(self, request):
#         """
#         POST: Create a new location
#         """
#         data = request.data
#         created_by = request.user.firstname if request.user.is_authenticated else "system"

#         required_fields = ["entity_id", "field_name"]
#         for field in required_fields:
#             if not data.get(field):
#                 return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

#         location = TicketsMasterConfiguration.objects.create(
#             entity_id=data["entity_id"],
#             field_type="Location",
#             referrence_to=data.get("referrence_to", ""),
#             field_name=data["field_name"],
#             field_values=data.get("field_values", ""),
#             is_mandatory=data.get("is_mandatory", ""),
#             is_active=data.get("is_active", "Y"),
#             created_date=timezone.now(),
#             created_by=created_by
#         )

#         # Return full object for React table
#         location_data = TicketsMasterConfiguration.objects.filter(pk=location.id).annotate(
#             entity_name=F('entity__name')
#         ).values(
#             "id",
#             "entity_id",
#             "entity_name",
#             "referrence_to",
#             "field_name",
#             "field_values",
#             "is_mandatory",
#             "is_active"
#         ).first()

#         return Response(location_data, status=status.HTTP_201_CREATED)

#     def put(self, request, pk=None):
#         """
#         PUT: Update an existing location
#         """
#         if not pk:
#             return Response({"error": "Location ID (pk) required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             location = TicketsMasterConfiguration.objects.get(pk=pk, field_type="Location")
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data
#         updated_by = request.user.firstname if request.user.is_authenticated else "system"

#         # Update fields if provided
#         for field in ["field_name", "referrence_to", "field_values", "is_mandatory", "is_active"]:
#             if data.get(field) is not None:
#                 setattr(location, field, data[field])

#         location.updated_date = timezone.now()
#         location.updated_by = updated_by
#         location.save()

#         # Return full object for React table
#         location_data = TicketsMasterConfiguration.objects.filter(pk=location.id).annotate(
#             entity_name=F('entity__name')
#         ).values(
#             "id",
#             "entity_id",
#             "entity_name",
#             "referrence_to",
#             "field_name",
#             "field_values",
#             "is_mandatory",
#             "is_active"
#         ).first()

#         return Response(location_data, status=status.HTTP_200_OK)

#     def delete(self, request, pk=None):
#         """
#         DELETE: Soft delete a location by marking is_active = 'N'
#         """
#         if not pk:
#             return Response({"error": "Location ID (pk) required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             location = TicketsMasterConfiguration.objects.get(pk=pk, field_type="Location")
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

#         location.is_active = 'N'
#         location.updated_date = timezone.now()
#         location.updated_by = request.user.firstname if request.user.is_authenticated else "system"
#         location.save()

#         return Response({"message": f"Location {location.id} has been deactivated."}, status=status.HTTP_200_OK)
class LocationByCountryAPIView(APIView):
    """
    Handles GET, POST, PUT, and DELETE requests for locations of given entities
    """
    permission_classes = [AllowAny]

    def get_entity_names(self, entity_ids):
        """
        Helper to fetch entity names from entity_ids list
        """
        if not entity_ids:
            return ["No Entity"]
        entities = Entity.objects.filter(id__in=entity_ids)
        return [entity.name for entity in entities if entity.name]

    def get(self, request):
        """
        GET: Return all locations, optionally filtered by entity_id (checks if in entity_ids)
        """
        entity_id = request.query_params.get('entity_id')
        if entity_id:
            try:
                entity_id = int(entity_id)
                locations = TicketsMasterConfiguration.objects.filter(
                    field_type="Location",
                    entity_ids__contains=[entity_id],
                ).values(
                    "id",
                    "entity_ids",
                    "referrence_to",
                    "field_name",
                    "field_values",
                    "is_mandatory",
                    "is_active"
                )
            except ValueError:
                return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            locations = TicketsMasterConfiguration.objects.filter(
                field_type="Location",
            ).values(
                "id",
                "entity_ids",
                "referrence_to",
                "field_name",
                "field_values",
                "is_mandatory",
                "is_active"
            )

        # Post-process to add entity_names
        locations_list = list(locations)
        for loc in locations_list:
            loc["entity_names"] = self.get_entity_names(loc["entity_ids"])

        return Response(locations_list)

    def post(self, request):
        """
        POST: Create a new location
        """
        data = request.data
        created_by = request.user.firstname if request.user.is_authenticated else "system"

        required_fields = ["entity_ids", "field_name"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure entity_ids is a list
        entity_ids = data.get("entity_ids", [])
        if not isinstance(entity_ids, list):
            return Response({"error": "entity_ids must be a list of integers"}, status=status.HTTP_400_BAD_REQUEST)

        location = TicketsMasterConfiguration.objects.create(
            entity_ids=entity_ids,
            field_type="Location",
            referrence_to=data.get("referrence_to", ""),
            field_name=data["field_name"],
            field_values=data.get("field_values", ""),
            is_mandatory=data.get("is_mandatory", ""),
            is_active=data.get("is_active", "Y"),
            created_by=created_by,
            created_date=timezone.now(),
            updated_date=timezone.now(),
            updated_by=created_by
        )

        # Return full object for React table
        location_data = TicketsMasterConfiguration.objects.filter(pk=location.id).values(
            "id",
            "entity_ids",
            "referrence_to",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active"
        ).first()
        if location_data:
            location_data["entity_names"] = self.get_entity_names(location_data["entity_ids"])

        return Response(location_data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        """
        PUT: Update an existing location
        """
        if not pk:
            return Response({"error": "Location ID (pk) required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = TicketsMasterConfiguration.objects.get(pk=pk, field_type="Location")
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        updated_by = request.user.firstname if request.user.is_authenticated else "system"

        # Update fields if provided
        if "entity_ids" in data:
            entity_ids = data["entity_ids"]
            if not isinstance(entity_ids, list):
                return Response({"error": "entity_ids must be a list of integers"}, status=status.HTTP_400_BAD_REQUEST)
            location.entity_ids = entity_ids

        for field in ["field_name", "referrence_to", "field_values", "is_mandatory", "is_active"]:
            if data.get(field) is not None:
                setattr(location, field, data[field])

        location.updated_date = timezone.now()
        location.updated_by = updated_by
        location.save()

        # Return full object for React table
        location_data = TicketsMasterConfiguration.objects.filter(pk=location.id).values(
            "id",
            "entity_ids",
            "referrence_to",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active"
        ).first()
        if location_data:
            location_data["entity_names"] = self.get_entity_names(location_data["entity_ids"])

        return Response(location_data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """
        DELETE: Soft delete a location by marking is_active = 'N'
        """
        if not pk:
            return Response({"error": "Location ID (pk) required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = TicketsMasterConfiguration.objects.get(pk=pk, field_type="Location")
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

        location.is_active = 'N'
        location.updated_date = timezone.now()
        location.updated_by = request.user.firstname if request.user.is_authenticated else "system"
        location.save()

        return Response({"message": f"Location {location.id} has been deactivated."}, status=status.HTTP_200_OK)

class ConfigurationByTypeAPIView(APIView):
    """
    Handles POST for creating configurations (e.g., new country)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        created_by = request.user.firstname if request.user.is_authenticated else "system"

        # Validate field_type
        if not data.get("field_type"):
            return Response({"error": "field_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        required_fields = ["field_type", "field_name"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

        configuration = TicketsMasterConfiguration.objects.create(
            entity_id=data.get("entity_id"),
            field_type=data["field_type"],
            referrence_to=data.get("referrence_to", ""),
            field_name=data["field_name"],
            field_values=data.get("field_values", data["field_name"]),
            is_mandatory=data.get("is_mandatory", "N"),
            is_active=data.get("is_active", "Y"),
            created_date=timezone.now(),
            created_by=created_by
        )

        # Return full object
        configuration_data = TicketsMasterConfiguration.objects.filter(pk=configuration.id).annotate(
            entity_name=F('entity__name')
        ).values(
            "id",
            "entity_id",
            "entity_name",
            "referrence_to",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active",
            "created_date",
            "updated_date"
        ).first()

        return Response(configuration_data, status=status.HTTP_201_CREATED)


# class DepartmentAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         entity_id = request.query_params.get('entity_id')
#         qs = TicketsMasterConfiguration.objects.filter(field_type='Department')
#         if entity_id:
#             qs = qs.filter(entity_id=entity_id)
#         data = DepartmentSerializer(qs, many=True).data  # use DepartmentSerializer
#         return Response(data)

#     def post(self, request):
#         data = request.data.copy()
#         data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_by"] = data["created_by"]
#         data["created_date"] = timezone.now()
#         data["updated_date"] = timezone.now()

#         serializer = DepartmentSerializer(data=data)  # use DepartmentSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             dept = TicketsMasterConfiguration.objects.get(pk=pk)
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data.copy()
#         data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_date"] = timezone.now()

#         serializer = DepartmentSerializer(dept, data=data, partial=True)  # use DepartmentSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   
# class RoleAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         entity_id = request.query_params.get('entity_id')
#         qs = TicketsMasterConfiguration.objects.filter(field_type='Role')
#         if entity_id:
#             qs = qs.filter(entity_id=entity_id)
#         data = RoleSerializer(qs, many=True).data  # use RoleSerializer
#         return Response(data)

#     def post(self, request):
#         data = request.data.copy()
#         data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_by"] = data["created_by"]
#         data["created_date"] = timezone.now()
#         data["updated_date"] = timezone.now()

#         serializer = RoleSerializer(data=data)  # use RoleSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             dept = TicketsMasterConfiguration.objects.get(pk=pk)
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data.copy()
#         data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_date"] = timezone.now()

#         serializer = RoleSerializer(dept, data=data, partial=True)  # use RoleSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserManagementAPIView(APIView):
#     """
#     Handles user creation, listing, update, and soft delete.
#     Supports multiple roles and entities via JSON arrays.
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         if pk:
#             user = get_object_or_404(User, pk=pk, is_deleted=False)
#             serializer = UserSerializer(user)
#             return Response(serializer.data)
#         else:
#             users = User.objects.filter(is_deleted=False)\
#                 .select_related('locations', 'department_id')\
#                 .order_by('id')
#             serializer = UserSerializer(users, many=True)
#             return Response(serializer.data)

#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         user = get_object_or_404(User, pk=pk, is_deleted=False)
#         serializer = UserSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         user = get_object_or_404(User, pk=pk, is_deleted=False)
#         user.is_deleted = True
#         user.is_active = False
#         user.save()
#         return Response({"message": "User soft deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
class UserManagementAPIView(APIView):
    """
    Handles user creation, listing, update, and soft delete.
    Supports multiple roles and entities via JSON arrays, stored in UserRoleMapping table.
    Also stores entities_ids and roles_ids in User table for quick access.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk:
            user = get_object_or_404(User, pk=pk, is_deleted=False)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            users = User.objects.filter(is_deleted=False)\
                .select_related('locations', 'department_id')\
                .order_by('id')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        # Extract roles and entities for mapping (pop to avoid setting in User JSON fields via serializer)
        entity_ids = data.pop('entities_ids', [])
        role_ids = data.pop('roles_ids', [])

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            # Sync mappings (deletes old not in input, updates/creates based on input)
            self._sync_mappings(user.id, role_ids, entity_ids)
            # Store in User JSON fields
            user.entities_ids = entity_ids
            user.roles_ids = role_ids
            user.save(update_fields=['entities_ids', 'roles_ids'])
            # Re-serialize with the fields included
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_deleted=False)
        data = request.data.copy()
        # Extract roles and entities for mapping (pop to avoid setting in User JSON fields via serializer)
        entity_ids = data.pop('entities_ids', [])
        role_ids = data.pop('roles_ids', [])

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Sync mappings (deletes old not in input, updates/creates based on input)
            self._sync_mappings(user.id, role_ids, entity_ids)
            # Store in User JSON fields
            user.entities_ids = entity_ids
            user.roles_ids = role_ids
            user.save(update_fields=['entities_ids', 'roles_ids'])
            # Re-serialize with the fields included
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_deleted=False)
        # Also delete associated mappings on soft delete
        UserRoleMapping.objects.filter(user=user).delete()
        user.is_deleted = True
        user.is_active = False
        user.save()
        return Response({"message": "User soft deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def _sync_mappings(self, user_id, role_ids, entity_ids):
        """
        Sync UserRoleMapping: 
        - Delete mappings for combos not in input (already existing but omitted).
        - For input combos: update if exists (triggers updated_date), create if not.
        Assumes role_ids and entity_ids are lists of integers.
        """
        if not role_ids and not entity_ids:
            # If both empty, clear all existing
            UserRoleMapping.objects.filter(user_id=user_id).delete()
            return

        desired_combos = {(r, e) for r in role_ids for e in entity_ids}

        with transaction.atomic():
            # Get existing combos for user
            existing_mappings = UserRoleMapping.objects.filter(user_id=user_id).select_related('role', 'entity')
            existing_combos = {(m.role_id, m.entity_id) for m in existing_mappings}

            # Delete mappings for combos not in desired
            to_delete_combos = existing_combos - desired_combos
            for role_id, entity_id in to_delete_combos:
                UserRoleMapping.objects.filter(
                    user_id=user_id, role_id=role_id, entity_id=entity_id
                ).delete()

            # Handle desired: update existing or create new
            for role_id, entity_id in desired_combos:
                mapping_data = {
                    'user': user_id,
                    'role': role_id,
                    'entity': entity_id,
                }
                existing = UserRoleMapping.objects.filter(
                    user_id=user_id, role_id=role_id, entity_id=entity_id
                ).first()
                if existing:
                    # Update (partial, triggers updated_date)
                    serializer = UserRoleMappingSerializer(existing, data=mapping_data, partial=True)
                else:
                    # Create
                    serializer = UserRoleMappingSerializer(data=mapping_data)
                
                if serializer.is_valid():
                    serializer.save()
                else:
                    logger.warning(f"Validation error syncing mapping for user {user_id}, role {role_id}, entity {entity_id}: {serializer.errors}")
# class UserManagementAPIView(APIView):
#     """
#     Handles user creation, listing, update, and soft delete.
#     Supports multiple roles and entities via JSON arrays, stored in UserRoleMapping table.
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         if pk:
#             user = get_object_or_404(User, pk=pk, is_deleted=False)
#             serializer = UserSerializer(user)
#             # Optionally remove entities_ids and roles_ids from response if needed
#             data = serializer.data
#             data.pop('entities_ids', None)
#             data.pop('roles_ids', None)
#             return Response(data)
#         else:
#             users = User.objects.filter(is_deleted=False)\
#                 .select_related('locations', 'department_id')\
#                 .order_by('id')
#             serializer = UserSerializer(users, many=True)
#             # Optionally remove from list response
#             data = serializer.data
#             for item in data:
#                 item.pop('entities_ids', None)
#                 item.pop('roles_ids', None)
#             return Response(data)

#     def post(self, request):
#         data = request.data.copy()
#         # Extract roles and entities for mapping (pop to avoid setting in User JSON fields)
#         entity_ids = data.pop('entities_ids', [])
#         role_ids = data.pop('roles_ids', [])

#         serializer = UserSerializer(data=data)
#         if serializer.is_valid():
#             user = serializer.save()
#             # Sync mappings (deletes old not in input, updates/creates based on input)
#             self._sync_mappings(user.id, role_ids, entity_ids)
#             # Ensure User JSON fields are empty (not used)
#             user.entities_ids = []
#             user.roles_ids = []
#             user.save(update_fields=['entities_ids', 'roles_ids'])
#             # Re-serialize without the fields
#             response_serializer = UserSerializer(user)
#             response_data = response_serializer.data
#             response_data.pop('entities_ids', None)
#             response_data.pop('roles_ids', None)
#             return Response(response_data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         user = get_object_or_404(User, pk=pk, is_deleted=False)
#         data = request.data.copy()
#         # Extract roles and entities for mapping (pop to avoid setting in User JSON fields)
#         entity_ids = data.pop('entities_ids', [])
#         role_ids = data.pop('roles_ids', [])

#         serializer = UserSerializer(user, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             # Sync mappings (deletes old not in input, updates/creates based on input)
#             self._sync_mappings(user.id, role_ids, entity_ids)
#             # Ensure User JSON fields are empty (not used)
#             user.entities_ids = []
#             user.roles_ids = []
#             user.save(update_fields=['entities_ids', 'roles_ids'])
#             # Re-serialize without the fields
#             response_serializer = UserSerializer(user)
#             response_data = response_serializer.data
#             response_data.pop('entities_ids', None)
#             response_data.pop('roles_ids', None)
#             return Response(response_data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         user = get_object_or_404(User, pk=pk, is_deleted=False)
#         # Also delete associated mappings on soft delete
#         UserRoleMapping.objects.filter(user=user).delete()
#         user.is_deleted = True
#         user.is_active = False
#         user.save()
#         return Response({"message": "User soft deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#     def _sync_mappings(self, user_id, role_ids, entity_ids):
#         """
#         Sync UserRoleMapping: 
#         - Delete mappings for combos not in input (already existing but omitted).
#         - For input combos: update if exists (triggers updated_date), create if not.
#         Assumes role_ids and entity_ids are lists of integers.
#         """
#         if not role_ids and not entity_ids:
#             # If both empty, clear all existing
#             UserRoleMapping.objects.filter(user_id=user_id).delete()
#             return

#         desired_combos = {(r, e) for r in role_ids for e in entity_ids}

#         with transaction.atomic():
#             # Get existing combos for user
#             existing_mappings = UserRoleMapping.objects.filter(user_id=user_id).select_related('role', 'entity')
#             existing_combos = {(m.role_id, m.entity_id) for m in existing_mappings}

#             # Delete mappings for combos not in desired
#             to_delete_combos = existing_combos - desired_combos
#             for role_id, entity_id in to_delete_combos:
#                 UserRoleMapping.objects.filter(
#                     user_id=user_id, role_id=role_id, entity_id=entity_id
#                 ).delete()

#             # Handle desired: update existing or create new
#             for role_id, entity_id in desired_combos:
#                 mapping_data = {
#                     'user': user_id,
#                     'role': role_id,
#                     'entity': entity_id,
#                 }
#                 existing = UserRoleMapping.objects.filter(
#                     user_id=user_id, role_id=role_id, entity_id=entity_id
#                 ).first()
#                 if existing:
#                     # Update (partial, triggers updated_date)
#                     serializer = UserRoleMappingSerializer(existing, data=mapping_data, partial=True)
#                 else:
#                     # Create
#                     serializer = UserRoleMappingSerializer(data=mapping_data)
                
#                 if serializer.is_valid():
#                     serializer.save()
#                 else:
#                     logger.warning(f"Validation error syncing mapping for user {user_id}, role {role_id}, entity {entity_id}: {serializer.errors}")
class DepartmentAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        entity_id = request.query_params.get('entity_id')
        qs = TicketsMasterConfiguration.objects.filter(field_type='Department')
        if entity_id:
            try:
                entity_id = int(entity_id)
                qs = qs.filter(entity_ids__contains=[entity_id])
            except ValueError:
                return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
        data = DepartmentSerializer(qs, many=True).data  # use DepartmentSerializer
        return Response(data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
        data["updated_by"] = data["created_by"]
        # Remove manual date setting if model uses auto_now_add/auto_now
        # data["created_date"] = timezone.now()
        # data["updated_date"] = timezone.now()

        serializer = DepartmentSerializer(data=data)  # use DepartmentSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            dept = TicketsMasterConfiguration.objects.get(pk=pk, field_type='Department')  # Added field_type filter for safety
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"
        # Remove manual date setting if model uses auto_now
        # data["updated_date"] = timezone.now()

        serializer = DepartmentSerializer(dept, data=data, partial=True)  # use DepartmentSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
# class RoleAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         entity_id = request.query_params.get('entity_id')
#         qs = TicketsMasterConfiguration.objects.filter(field_type='Role')
#         if entity_id:
#             qs = qs.filter(entity_id=entity_id)
#         data = RoleSerializer(qs, many=True).data  # use RoleSerializer
#         return Response(data)

#     def post(self, request):
#         data = request.data.copy()
#         data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_by"] = data["created_by"]
#         data["created_date"] = timezone.now()
#         data["updated_date"] = timezone.now()

#         serializer = RoleSerializer(data=data)  # use RoleSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             role_obj = TicketsMasterConfiguration.objects.get(pk=pk)  # Renamed from 'dept' for clarity
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data.copy()
#         data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"
#         data["updated_date"] = timezone.now()

#         serializer = RoleSerializer(role_obj, data=data, partial=True)  # use RoleSerializer
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
class RoleAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        entity_id = request.query_params.get('entity_id')
        qs = TicketsMasterConfiguration.objects.filter(field_type='Role')
        if entity_id:
            try:
                entity_id = int(entity_id)
                qs = qs.filter(entity_ids__contains=[entity_id])
            except ValueError:
                return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
        data = RoleSerializer(qs, many=True).data  # use RoleSerializer
        return Response(data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
        data["updated_by"] = data["created_by"]
        # Remove manual date setting if model uses auto_now_add/auto_now
        # data["created_date"] = timezone.now()
        # data["updated_date"] = timezone.now()

        serializer = RoleSerializer(data=data)  # use RoleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            role_obj = TicketsMasterConfiguration.objects.get(pk=pk, field_type='Role')  # Added field_type filter for safety
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"
        # Remove manual date setting if model uses auto_now
        # data["updated_date"] = timezone.now()

        serializer = RoleSerializer(role_obj, data=data, partial=True)  # use RoleSerializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class RoleAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request):
#         qs = Role.objects.filter(is_active='Y')
#         data = RoleSerializer(qs, many=True).data
#         return Response(data)

#     def post(self, request):
#         data = request.data.copy()
#         creator_name = "system"
#         if request.user.is_authenticated:
#             creator_name = getattr(request.user, 'firstname', '') or request.user.username or 'Anonymous'
#         data["updated_by"] = creator_name  # Initial update same as create

#         # Do NOT set created_by/updated_by in data here (read_only will exclude from validated_data)
#         # Set is_active only if provided or default
#         if 'is_active' not in data:
#             data['is_active'] = 'Y'

#         serializer = RoleSerializer(data=data)
#         if serializer.is_valid():
#             # Force-set audit fields after validation
#             instance = serializer.save(
#                 created_by=creator_name,
#                 updated_by=creator_name
#             )
#             # Re-serialize to include audit fields in response
#             response_serializer = RoleSerializer(instance)
#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
#         # Debug: Print errors to console
#         print("POST Serializer Errors:", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             role = Role.objects.get(pk=pk, is_active='Y')
#         except Role.DoesNotExist:
#             return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data.copy()
#         updater_name = "system"
#         if request.user.is_authenticated:
#             updater_name = getattr(request.user, 'firstname', '') or request.user.username or 'Anonymous'

#         # Do NOT set updated_by in data (read_only)
#         serializer = RoleSerializer(role, data=data, partial=True)
#         if serializer.is_valid():
#             # Force-set updated_by after validation
#             instance = serializer.save(updated_by=updater_name)
#             # Re-serialize
#             response_serializer = RoleSerializer(instance)
#             return Response(response_serializer.data)
        
#         # Debug
#         print("PUT Serializer Errors:", serializer.errors)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class TicketsMasterConfigurationView(APIView):
    
#     permission_classes = [AllowAny]
#     def get(self, request):
#         configurations = TicketsMasterConfiguration.objects.all()
#         serializer = TicketsMasterConfigurationSerializer(configurations, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = TicketsMasterConfigurationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         try:
#             configuration = TicketsMasterConfiguration.objects.get(pk=pk)
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         serializer = TicketsMasterConfigurationSerializer(configuration, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class TicketsMasterConfigurationView(APIView):
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        configurations = TicketsMasterConfiguration.objects.all()
        serializer = TicketsMasterConfigurationSerializer(configurations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TicketsMasterConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # Re-serialize to include computed fields like entity_names
            serializer = TicketsMasterConfigurationSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            configuration = TicketsMasterConfiguration.objects.get(pk=pk)
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({'error': 'Configuration not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TicketsMasterConfigurationSerializer(configuration, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            # Re-serialize to include computed fields like entity_names
            serializer = TicketsMasterConfigurationSerializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """
        DELETE: Soft delete a configuration by marking is_active = 'N'
        """
        if not pk:
            return Response({"error": "Configuration ID (pk) required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            configuration = TicketsMasterConfiguration.objects.get(pk=pk)
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Configuration not found"}, status=status.HTTP_404_NOT_FOUND)

        configuration.is_active = 'N'
        configuration.updated_date = timezone.now()
        configuration.updated_by = request.user.firstname if request.user.is_authenticated else "system"
        configuration.save()

        return Response({"message": f"Configuration {configuration.id} has been deactivated."}, status=status.HTTP_200_OK)


class TicketEmailTemplateListCreateView(APIView):
    # ✅ GET all templates
    def get(self, request):
        templates = TicketEmailTemplate.objects.all().order_by('id')
        serializer = TicketEmailTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    # ✅ POST: create a new template
    def post(self, request):
        serializer = TicketEmailTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TicketEmailTemplateDetailView(APIView):
    # ✅ PUT (update)
    def put(self, request, pk):
        try:
            template = TicketEmailTemplate.objects.get(pk=pk)
        except TicketEmailTemplate.DoesNotExist:
            return Response({"detail": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketEmailTemplateSerializer(template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ DELETE (soft delete → deactivate)
    def delete(self, request, pk):
        try:
            template = TicketEmailTemplate.objects.get(pk=pk)
        except TicketEmailTemplate.DoesNotExist:
            return Response({"detail": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        template.is_active = "N"
        template.save()
        return Response({"detail": "Template deactivated"}, status=status.HTTP_204_NO_CONTENT)

import json
# class TicketCategoryListCreateView(APIView):
#     permission_classes = []
#     def get(self, request, *args, **kwargs):
#         queryset = TicketCategory.objects.all()
#         serializer = TicketCategorySerializer(queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         from Ticket.models import TicketsMasterConfiguration, TicketCategory, TicketSubcategory, TicketSLA
#         data = request.data
#         created_by = request.user.firstname if request.user.is_authenticated else "system"
#         updated_by = request.user.firstname if request.user.is_authenticated else "system"


#         # Validate Entity
#         try:
#             entity = Entity.objects.filter(id=int(data.get("entity_id"))).first()
#         except (Entity.DoesNotExist, TypeError, ValueError):
#             return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
#         print("entity :",entity)
#         try:
#             department = TicketsMasterConfiguration.objects.filter(id=int(data.get("department_id")), is_active="Y").first()
#         except Exception as e:
#             print("e :",e)
#             return Response({"error": "Invalid department_id"}, status=status.HTTP_400_BAD_REQUEST)
#         if entity.id not in department.entity_ids:
#             # ID not allowed
#             return Response({"error": "Entity not allowed in department"}, status=403)
#         # Handle Category
#         category_id = data.get("category_id")
#         category_name = data.get("category_name")

#         if category_id:
#             try:
#                 category = TicketCategory.objects.get(id=int(category_id))
#             except TicketCategory.DoesNotExist:
#                 return Response({"error": "Invalid category_id"}, status=status.HTTP_400_BAD_REQUEST)
#         elif category_name:
#             category, created = TicketCategory.objects.get_or_create(
#                 category_name=category_name,
#                 entity=entity,
#                 department=department,
#                 defaults={
#                     "category_description": category_name,
#                     "is_active": "Y",
#                     "created_date": timezone.now(),
#                     "updated_date": timezone.now(),
#                 }
#             )
#         else:
#             return Response({"error": "category_id or category_name required"}, status=status.HTTP_400_BAD_REQUEST)
#         # Handle Subcategory
#         subcategory_id = data.get("subcategory_id")
#         subcategory_name = data.get("subcategory_name")
#         subcategory = None

#         if subcategory_id:
#             try:
#                 subcategory = TicketSubcategory.objects.get(id=int(subcategory_id))
#             except TicketSubcategory.DoesNotExist:
#                 return Response({"error": "Invalid subcategory_id"}, status=status.HTTP_400_BAD_REQUEST)
#         elif subcategory_name:
#             subcategory, created = TicketSubcategory.objects.get_or_create(
#                 subcategory_name=subcategory_name,
#                 category=category,
#                 entity_id=entity.id,
#                 defaults={
#                     "subcategory_description": subcategory_name,
#                     "is_active": "Y",
#                     "created_date": timezone.now(),
#                     "updated_date": timezone.now(),
#                 }
#             )

  
#         sla_data = {
#             "Approver_level1_user_id": data.get("level1"),
#             "Approver_level1_time": data.get("sla1"),
#             "Approver_level2_user_id": data.get("level2"),
#             "Approver_level2_time": data.get("sla2"),
#             "Approver_level3_user_id": data.get("level3"),
#             "Approver_level3_time": data.get("sla3"),
#             "Approver_level4_user_id": data.get("level4"),
#             "Approver_level4_time": data.get("sla4"),
#             "Approver_level5_user_id": data.get("level5"),
#             "Approver_level5_time": data.get("sla5"),
#             "Assign_to": data.get("assign_technician"),
#             # "Assign_to_id": data.get("assignTechnician"),
#             "is_active": "Y",
#             "updated_date": timezone.now(),
#             "updated_by":updated_by,
#         }

#         ticket_sla, created = TicketSLA.objects.update_or_create(
#             entity=entity,
#             category=category,
#             subcategory=subcategory,
#             defaults=sla_data
#         )

#         if created:
#             ticket_sla.created_date = timezone.now()
#             created
#             ticket_sla.save()



#         return Response({
#             "success": True,
#             "message": "Category, Subcategory, and SLA created successfully",
#             "category_id": category.id,
#             "subcategory_id": subcategory.id if subcategory else None,
#             "department_id": department.id
#         }, status=status.HTTP_201_CREATED)
    

# class TicketCategoryRetrieveUpdateView(APIView):
#     # permission_classes = [IsAuthenticated]  # Requires authentication for all operations
#     permission_classes = [AllowAny]
#     def get_object(self, pk):
#         try:
#             return TicketCategory.objects.get(pk=pk)
#         except TicketCategory.DoesNotExist:
#             return None

#     def get(self, request, pk, *args, **kwargs):
#         # GET single ticket category
#         instance = self.get_object(pk)
#         if not instance:
#             return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
#         serializer = TicketCategorySerializer(instance)
#         return Response(serializer.data)
    
#     def put(self, request, pk, *args, **kwargs):
#         data = request.data
#         updated_by = "system"

#         # Get category
#         try:
#             category = TicketCategory.objects.get(pk=pk)
#         except TicketCategory.DoesNotExist:
#             return Response({"error": "Category not found"}, status=404)

#         # Entity
#         try:
#             entity_id = int(data.get("entity_id") or category.entity_id)
#             entity = Entity.objects.get(id=entity_id)
#         except (Entity.DoesNotExist, ValueError):
#             return Response({"error": "Invalid entity_id"}, status=400)

#         # Department only
#         try:
#             dept_id = int(data.get("department_id") or category.department_id)
#             department = TicketsMasterConfiguration.objects.get(
#                 id=dept_id,
#                 is_active="Y",
#                 entity_ids__contains=[entity_id]
#             )
#         except TicketsMasterConfiguration.DoesNotExist:
#             return Response({"error": "Invalid department"}, status=400)

#         # UPDATE CATEGORY — NO LOCATION AT ALL
#         category.entity = entity
#         category.department = department
#         category.is_active = data.get("is_active", "Y")
#         category.updated_date = timezone.now()
#         category.updated_by = updated_by
#         category.save()

#         # Subcategory
#         subcategory = None
#         if data.get("subcategory_id"):
#             try:
#                 subcategory = TicketSubcategory.objects.get(id=int(data["subcategory_id"]))
#             except TicketSubcategory.DoesNotExist:
#                 return Response({"error": "Invalid subcategory_id"}, status=400)

#         # UPDATE SLA
#         TicketSLA.objects.update_or_create(
#             entity=entity,
#             category=category,
#             subcategory=subcategory,
#             defaults={
#                 "Approver_level1_user_id": data.get("level1"),
#                 "Approver_level1_time": data.get("sla1"),
#                 "Approver_level2_user_id": data.get("level2"),
#                 "Approver_level2_time": data.get("sla2"),
#                 "Approver_level3_user_id": data.get("level3"),
#                 "Approver_level3_time": data.get("sla3"),
#                 "Approver_level4_user_id": data.get("level4"),
#                 "Approver_level4_time": data.get("sla4"),
#                 "Approver_level5_user_id": data.get("level5"),
#                 "Approver_level5_time": data.get("sla5"),
#                 # "Assign_to_id": data.get("assignTechnician"),
#                 "Assign_to": str(data.get("assignTechnician", "")) or None,
#                 "updated_date": timezone.now(),
#                 "updated_by": updated_by,
#             }
#         )

#         return Response({
#             "success": True,
#             "message": "Updated successfully"
#         }, status=200)
    
#     # def put(self, request, pk, *args, **kwargs):
#     #     data = request.data
#     #     user = request.user if request.user.is_authenticated else None
#     #     updated_by = user.firstname if user else "system"

#     #     # 1. Get the existing TicketCategory
#     #     category = self.get_object(pk)
#     #     if not category:
#     #         return Response({"error": "Category not found"}, status=404)

#     #     # 2. Validate Entity (must match)
#     #     try:
#     #         entity_id = int(data.get("entity_id") or category.entity_id)
#     #         entity = Entity.objects.get(id=entity_id)
#     #     except (Entity.DoesNotExist, ValueError):
#     #         return Response({"error": "Invalid entity_id"}, status=400)

#     #     # 3. Validate Department
#     #     try:
#     #         dept_id = int(data.get("department_id") or category.department_id)
#     #         department = TicketsMasterConfiguration.objects.get(
#     #             id=dept_id,
#     #             is_active="Y",
#     #             entity_ids__contains=[entity_id]
#     #         )
#     #     except TicketsMasterConfiguration.DoesNotExist:
#     #         return Response({"error": "Invalid or unauthorized department"}, status=400)

#     #     # 4. Validate Location
#     #     location = category.location  # default = old location
#     #     if "location_id" in data and data["location_id"]:
#     #         try:
#     #             loc_id = int(data["location_id"])
#     #             location = TicketsMasterConfiguration.objects.get(id=loc_id, is_active="Y")
#     #         except (TicketsMasterConfiguration.DoesNotExist, ValueError):
#     #             return Response({"error": "Invalid location_id"}, status=400)

#     #     # 5. Update the category (if needed)
#     #     category.department = department
#     #     category.location = location
#     #     category.is_active = data.get("is_active", category.is_active)
#     #     category.save()

#     #     # 6. Handle Subcategory
#     #     subcategory = None
#     #     if data.get("subcategory_id"):
#     #         try:
#     #             subcategory = TicketSubcategory.objects.get(id=int(data["subcategory_id"]))
#     #         except TicketSubcategory.DoesNotExist:
#     #             return Response({"error": "Invalid subcategory_id"}, status=400)
#     #     elif data.get("subcategory_name"):
#     #         subcategory, _ = TicketSubcategory.objects.get_or_create(
#     #             entity=entity,
#     #             category=category,
#     #             subcategory_name=data["subcategory_name"],
#     #             defaults={"is_active": "Y"}
#     #         )

#     #     # 7. UPDATE SLA — THIS IS THE FIX!
#     #     sla_data = {
#     #         "Approver_level1_user_id": data.get("level1"),
#     #         "Approver_level1_time": data.get("sla1"),
#     #         "Approver_level2_user_id": data.get("level2"),
#     #         "Approver_level2_time": data.get("sla2"),
#     #         "Approver_level3_user_id": data.get("level3"),
#     #         "Approver_level3_time": data.get("sla3"),
#     #         "Approver_level4_user_id": data.get("level4"),
#     #         "Approver_level4_time": data.get("sla4"),
#     #         "Approver_level5_user_id": data.get("level5"),
#     #         "Approver_level5_time": data.get("sla5"),
#     #         "Assign_to_id": data.get("assignTechnician"),
#     #         "updated_date": timezone.now(),
#     #         "updated_by": updated_by,
#     #     }

#     #     TicketSLA.objects.update_or_create(
#     #         entity=entity,
#     #         category=category,
#     #         subcategory=subcategory,
#     #         defaults=sla_data
#     #     )

#     #     return Response({
#     #         "success": True,
#     #         "message": "Category and SLA updated successfully",
#     #         "category_id": category.id
#     #     }, status=200)
#     # def put(self, request, pk, *args, **kwargs):
#     #     # PUT update ticket category
#     #     instance = self.get_object(pk)
#     #     if not instance:
#     #         return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
#     #     serializer = TicketCategorySerializer(instance, data=request.data, partial=False)
#     #     if serializer.is_valid():
#     #         serializer.save(
#     #             updated_date=timezone.now(),
#     #             updated_by=request.user.firstname if request.user.is_authenticated else None
#     #         )
#     #         return Response(serializer.data)
#     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketCategoryListCreateView(APIView):
    permission_classes = [AllowAny]
 
    def get(self, request, *args, **kwargs):
        queryset = TicketCategory.objects.all()
        serializer = TicketCategorySerializer(queryset, many=True)
        return Response(serializer.data)
 
    def post(self, request, *args, **kwargs):
        data = request.data
        created_by = request.user.firstname if request.user.is_authenticated else "system"
        updated_by = request.user.firstname if request.user.is_authenticated else "system"
 
        # Validate entity_ids
        entity_ids_raw = data.get("entity_ids", [])
        if not entity_ids_raw:
            return Response({"error": "entity_ids (list) required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            entity_ids = sorted([int(eid) for eid in entity_ids_raw])
        except (TypeError, ValueError):
            return Response({"error": "entity_ids must be a list of integers"}, status=status.HTTP_400_BAD_REQUEST)
 
        entities = Entity.objects.filter(id__in=entity_ids)
        if len(entities) != len(entity_ids):
            return Response({"error": "Invalid entity_ids"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Validate Department
        dept_id = data.get("department_id")
        if not dept_id:
            return Response({"error": "department_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            dept_id = int(dept_id)
        except ValueError:
            return Response({"error": "Invalid department_id"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Check if all entity_ids are allowed in department
        department = TicketsMasterConfiguration.objects.filter(
            id=dept_id,
            is_active="Y"
        ).first()

        if not department:
            return Response({"error": "Department not found or inactive"}, status=400)

        department_entity_ids = department.entity_ids or []

        missing_entities = [eid for eid in entity_ids if eid not in department_entity_ids]
        # department = TicketsMasterConfiguration.objects.filter(
        #     id=dept_id,
        #     is_active="Y"
        # ).filter(*[Q(entity_ids__contains=[eid]) for eid in entity_ids]).first()
        # if not department:
        #     return Response({"error": "Invalid department_id or entities not allowed in department"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Handle Category
        category_id = data.get("category_id")
        category_name = data.get("category_name")
 
        if category_id:
            try:
                category = TicketCategory.objects.get(id=int(category_id))
                # Override entity_ids if mismatch (flexible reuse)
                if sorted(category.entity_ids) != entity_ids:
                    category.entity_ids = entity_ids
                    category.is_active = data.get("is_active", category.is_active)
                    category.updated_date = timezone.now()
                    category.updated_by = updated_by
                    category.save()
            except TicketCategory.DoesNotExist:
                return Response({"error": "Invalid category_id"}, status=status.HTTP_400_BAD_REQUEST)
        elif category_name:
            # Check if category already exists with same params
            existing_categories = TicketCategory.objects.filter(
                category_name=category_name,
                department=department,
                entity_ids=entity_ids
            )
            if existing_categories.exists():
                category = existing_categories.first()
            else:
                category = TicketCategory.objects.create(
                    entity_ids=entity_ids,
                    department=department,
                    category_name=category_name,
                    category_description=data.get("category_description", category_name),
                    is_active=data.get("is_active", "Y"),
                    created_date=timezone.now(),
                    created_by=created_by,
                    updated_date=timezone.now(),
                    updated_by=updated_by
                )
        else:
            return Response({"error": "category_id or category_name required"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Handle Subcategory IDs (support multiple)
        subcategory_ids_raw = data.get("subcategory_ids", [])
        if isinstance(subcategory_ids_raw, list):
            try:
                subcategory_ids = [int(sid) for sid in subcategory_ids_raw]
                # Validate they belong to the category
                valid_subcats = TicketSubcategory.objects.filter(id__in=subcategory_ids, category=category)
                if len(valid_subcats) != len(subcategory_ids):
                    return Response({"error": "Invalid subcategory_ids (must belong to the category)"}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError):
                return Response({"error": "subcategory_ids must be a list of integers"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            subcategory_ids = []
 
        # SLA Data
        sla_data = {
            "Approver_level1_user_id": data.get("level1"),
            "Approver_level1_time": data.get("sla1"),
            "Approver_level2_user_id": data.get("level2"),
            "Approver_level2_time": data.get("sla2"),
            "Approver_level3_user_id": data.get("level3"),
            "Approver_level3_time": data.get("sla3"),
            "Approver_level4_user_id": data.get("level4"),
            "Approver_level4_time": data.get("sla4"),
            "Approver_level5_user_id": data.get("level5"),
            "Approver_level5_time": data.get("sla5"),
            "assigned_user_id": data.get("assigned_user_id"),
            "assigned_group_id": data.get("assigned_group_id"),
            # "confidential": data.get("confidential", "N"),
            "Execution_by": data.get("assign_technician"),  # Use correct field name (from prior fix)
            "is_active": "Y",
            "updated_date": timezone.now(),
            "updated_by": updated_by,
        }
 
        # Handle SLA
        existing_sla = TicketSLA.objects.filter(
            entity_ids=entity_ids,
            category=category,
            subcategory_ids=subcategory_ids  # Use list for exact match
        ).first()
 
        created = False
        if existing_sla:
            for key, value in sla_data.items():
                setattr(existing_sla, key, value)
            existing_sla.updated_date = timezone.now()
            existing_sla.updated_by = updated_by
            existing_sla.save()
        else:
            TicketSLA.objects.create(
                entity_ids=entity_ids,
                category=category,
                subcategory_ids=subcategory_ids,  # Pass the list here
                **sla_data,
                created_date=timezone.now(),
                created_by=created_by
            )
            created = True
 
        return Response({
            "success": True,
            "message": "Category, Subcategory, and SLA created/updated successfully",
            "category_id": category.id,
            "subcategory_id": None,  # Since multiple, set to null
            "department_id": department.id
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
 
 
class TicketCategoryRetrieveUpdateView(APIView):
    permission_classes = [AllowAny]
 
    def get_object(self, pk):
        try:
            return TicketCategory.objects.get(pk=pk)
        except TicketCategory.DoesNotExist:
            return None
 
    def get(self, request, pk, *args, **kwargs):
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketCategorySerializer(instance)
        return Response(serializer.data)
 
    def put(self, request, pk, *args, **kwargs):
        data = request.data
        updated_by = request.user.firstname if request.user.is_authenticated else "system"
 
        # Get category
        try:
            category = TicketCategory.objects.get(pk=pk)
        except TicketCategory.DoesNotExist:
            return Response({"error": "Category not found"}, status=404)
 
        # Entity_ids
        entity_ids_raw = data.get("entity_ids", category.entity_ids or [])
        try:
            entity_ids = sorted([int(eid) for eid in entity_ids_raw])
        except (TypeError, ValueError):
            return Response({"error": "entity_ids must be a list of integers"}, status=400)
 
        if not entity_ids:
            return Response({"error": "entity_ids required"}, status=400)
 
        entities = Entity.objects.filter(id__in=entity_ids)
        if len(entities) != len(entity_ids):
            return Response({"error": "Invalid entity_ids"}, status=400)
 
        # Department
        dept_id = data.get("department_id", category.department_id)
        try:
            dept_id = int(dept_id)
        except ValueError:
            return Response({"error": "Invalid department_id"}, status=400)
 
        # department = TicketsMasterConfiguration.objects.filter(
        #     id=dept_id,
        #     is_active="Y"
        # ).filter(*[Q(entity_ids__contains=[eid]) for eid in entity_ids]).first()
        # if not department:
        #     return Response({"error": "Invalid department"}, status=400)
        department = TicketsMasterConfiguration.objects.filter(
                id=dept_id,
                is_active="Y"
            ).first()

        if not department:
            return Response({"error": "Department not found or inactive"}, status=400)

        department_entity_ids = department.entity_ids or []

        missing_entities = [eid for eid in entity_ids if eid not in department_entity_ids]
        # Update Category
        category.entity_ids = entity_ids
        category.department = department
        category.is_active = data.get("is_active", category.is_active)
        category.category_name = data.get("category_name", category.category_name)
        category.category_description = data.get("category_description", category.category_description)
        category.updated_date = timezone.now()
        category.updated_by = updated_by
        category.save()
 
        # Handle Subcategory IDs (multiple)
        subcategory_ids_raw = data.get("subcategory_ids", [])
        if isinstance(subcategory_ids_raw, list):
            try:
                subcategory_ids = [int(sid) for sid in subcategory_ids_raw]
                # Validate they belong to the category
                valid_subcats = TicketSubcategory.objects.filter(id__in=subcategory_ids, category=category)
                if len(valid_subcats) != len(subcategory_ids):
                    return Response({"error": "Invalid subcategory_ids (must belong to the category)"}, status=400)
            except (TypeError, ValueError):
                return Response({"error": "subcategory_ids must be a list of integers"}, status=400)
        else:
            subcategory_ids = []
 
        # Update SLA
        existing_sla = TicketSLA.objects.filter(
            entity_ids=entity_ids,
            category=category,
            subcategory_ids=subcategory_ids  # Fixed: Use list for exact match
        ).first()
        if existing_sla:
            sla_data = {
                "Approver_level1_user_id": data.get("level1"),
                "Approver_level1_time": data.get("sla1"),
                "Approver_level2_user_id": data.get("level2"),
                "Approver_level2_time": data.get("sla2"),
                "Approver_level3_user_id": data.get("level3"),
                "Approver_level3_time": data.get("sla3"),
                "Approver_level4_user_id": data.get("level4"),
                "Approver_level4_time": data.get("sla4"),
                "Approver_level5_user_id": data.get("level5"),
                "Approver_level5_time": data.get("sla5"),
                "assigned_user_id": data.get("assigned_user_id"),
                "assigned_group_id": data.get("assigned_group_id"),
                "confidential": data.get("confidential", existing_sla.confidential),
                "Execution_by": data.get("assign_technician"),
                "is_active": data.get("is_active", existing_sla.is_active),
                "updated_date": timezone.now(),
                "updated_by": updated_by,
            }
            for key, value in sla_data.items():
                setattr(existing_sla, key, value)
            existing_sla.save()
        else:
            # Create if not exists
            TicketSLA.objects.create(
                entity_ids=entity_ids,
                category=category,
                subcategory_ids=subcategory_ids,
                Approver_level1_user_id=data.get("level1"),
                Approver_level1_time=data.get("sla1"),
                Approver_level2_user_id=data.get("level2"),
                Approver_level2_time=data.get("sla2"),
                Approver_level3_user_id=data.get("level3"),
                Approver_level3_time=data.get("sla3"),
                Approver_level4_user_id=data.get("level4"),
                Approver_level4_time=data.get("sla4"),
                Approver_level5_user_id=data.get("level5"),
                Approver_level5_time=data.get("sla5"),
                assigned_user_id=data.get("assigned_user_id"),
                assigned_group_id=data.get("assigned_group_id"),
                confidential=data.get("confidential", "N"),
                Execution_by=data.get("assign_technician"),
                is_active="Y",
                created_date=timezone.now(),
                created_by=updated_by,
                updated_date=timezone.now(),
                updated_by=updated_by
            )
 
        return Response({
            "success": True,
            "message": "Updated successfully"
        }, status=200)
 
 
class TicketSubcategoryListCreateView(APIView):
    permission_classes = [AllowAny]
 
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category_id')
        queryset = TicketSubcategory.objects.all()
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        serializer = TicketSubcategorySerializer(queryset, many=True)
        return Response(serializer.data)
 
    def post(self, request, *args, **kwargs):
        serializer = TicketSubcategorySerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(
                created_date=timezone.now(),
                updated_date=timezone.now(),
                created_by=request.user.firstname if request.user.is_authenticated else "system",
                updated_by=request.user.firstname if request.user.is_authenticated else "system"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




class HodUserAPIView(APIView):
    # def get(self, request):
    #     """Retrieve all HOD users"""
    #     hods = User.objects.filter(is_hod=True)
    #     serializer = UserSerializer(hods, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    # def get(self, request):
    #     """Retrieve all HOD users with ticket approval counts (approved, rejected, pending, on_hold, overdue, sla_breached) 
    #     including breakdowns by priority and department from TicketsMasterConfiguration,
    #     and average approver response time in hours."""
    #     hods = User.objects.filter(is_hod=True)
        
    #     # Fetch all priority configurations for reference
    #     priority_configs = TicketsMasterConfiguration.objects.filter(field_type__iexact='priority').values_list('id', 'field_name')
    #     priority_map = {config[0]: config[1] for config in priority_configs}  # {priority_id: priority_name}
        
    #     # Fetch all department configurations for reference
    #     department_configs = TicketsMasterConfiguration.objects.filter(field_type__iexact='department').values_list('id', 'field_name')
    #     department_map = {config[0]: config[1] for config in department_configs}  # {department_id: department_name}
        
    #     # Helper for counts per HOD
    #     def get_hod_counts(hod):
    #         approver_logs_qs = TicketApprovalLog.objects.filter(created_by=hod).select_related('ticket')
            
    #         # Total tickets handled by this HOD (unique tickets from logs)
    #         total_tickets = CreateTicket.objects.filter(
    #             id__in=approver_logs_qs.values_list('ticket', flat=True).distinct()
    #         ).count()
            
    #         # Overall counts (not priority-specific)
    #         approved_count = approver_logs_qs.filter(approved_by=hod).count()
    #         rejected_count = approver_logs_qs.filter(status__iexact='Rejected').count()
    #         on_hold_count = approver_logs_qs.filter(status__iexact='OnHold').count()
    #         pending_count = approver_logs_qs.filter(status__iexact='Pending').count()
    #         overdue_count = approver_logs_qs.filter(status__iexact='Pending', sla_breach=True).count()  # Added overdue count
    #         sla_breached_count = approver_logs_qs.filter(sla_breach=True).count()
            
    #         # Calculate average response time for resolved approvals (Approved or Rejected)
    #         resolved_logs = approver_logs_qs.filter(status__in=['Approved', 'Rejected'])
    #         average_response_time = 0
    #         if resolved_logs.exists():
    #             response_times = []
    #             for log in resolved_logs:
    #                 if log.updated_date and log.created_date:
    #                     delta = log.updated_date - log.created_date
    #                     response_times.append(delta.total_seconds() / 3600.0)  # in hours
    #             average_response_time = sum(response_times) / len(response_times) if response_times else 0
            
    #         # Priority-based full counts: group by ticket's priority_id from CreateTicket
    #         # Assuming CreateTicket has 'priority_id' field referencing TicketsMasterConfiguration
    #         priority_logs = approver_logs_qs.values(
    #             'ticket__priority_id', 'status', 'sla_breach', 'approved_by'
    #         )
            
    #         # Use a dict to group counts by priority_id
    #         priority_counts = {}
    #         for log in priority_logs:
    #             priority_id = log['ticket__priority_id']
    #             if priority_id not in priority_counts:
    #                 priority_counts[priority_id] = {
    #                     'name': priority_map.get(priority_id, f'Priority {priority_id}'),  # Use name from config
    #                     'approved': 0,
    #                     'rejected': 0,
    #                     'pending': 0,
    #                     'on_hold': 0,
    #                     'overdue': 0,  # Added overdue
    #                     'sla_breached': 0,
    #                     'total': 0,  # Total logs for this priority
    #                 }
                
    #             # Increment total for each log
    #             priority_counts[priority_id]['total'] += 1
                
    #             if log['approved_by'] == hod.id:  # Compare IDs for safety
    #                 priority_counts[priority_id]['approved'] += 1
    #             status_lower = (log['status'] or '').lower()
    #             if 'rejected' in status_lower:
    #                 priority_counts[priority_id]['rejected'] += 1
    #             if 'pending' in status_lower:
    #                 priority_counts[priority_id]['pending'] += 1
    #             if 'onhold' in status_lower:
    #                 priority_counts[priority_id]['on_hold'] += 1
    #             if status_lower == 'pending' and log['sla_breach']:  # Overdue logic
    #                 priority_counts[priority_id]['overdue'] += 1
    #             if log['sla_breach']:
    #                 priority_counts[priority_id]['sla_breached'] += 1
            
    #         # Transform to name-based dict: {name: {approved: ..., rejected: ..., total: ..., etc.}}
    #         name_based_priority_breakdown = {}
    #         for pc in priority_counts.values():
    #             name = pc['name']
    #             name_based_priority_breakdown[name] = {k: v for k, v in pc.items() if k != 'name'}
            
    #         # Department-based full counts: group by ticket's department_id from CreateTicket
    #         # Assuming CreateTicket has 'department_id' field referencing TicketsMasterConfiguration
    #         department_logs = approver_logs_qs.values(
    #             'ticket__department_id', 'status', 'sla_breach', 'approved_by'
    #         )
            
    #         # Use a dict to group counts by department_id
    #         department_counts = {}
    #         for log in department_logs:
    #             department_id = log['ticket__department_id']
    #             if department_id not in department_counts:
    #                 department_counts[department_id] = {
    #                     'name': department_map.get(department_id, f'Department {department_id}'),  # Use name from config
    #                     'approved': 0,
    #                     'rejected': 0,
    #                     'pending': 0,
    #                     'on_hold': 0,
    #                     'overdue': 0,  # Added overdue
    #                     'sla_breached': 0,
    #                     'total': 0,  # Total logs for this department
    #                 }
                
    #             # Increment total for each log
    #             department_counts[department_id]['total'] += 1
                
    #             if log['approved_by'] == hod.id:  # Compare IDs for safety
    #                 department_counts[department_id]['approved'] += 1
    #             status_lower = (log['status'] or '').lower()
    #             if 'rejected' in status_lower:
    #                 department_counts[department_id]['rejected'] += 1
    #             if 'pending' in status_lower:
    #                 department_counts[department_id]['pending'] += 1
    #             if 'onhold' in status_lower:
    #                 department_counts[department_id]['on_hold'] += 1
    #             if status_lower == 'pending' and log['sla_breach']:  # Overdue logic
    #                 department_counts[department_id]['overdue'] += 1
    #             if log['sla_breach']:
    #                 department_counts[department_id]['sla_breached'] += 1
            
    #         # Transform to name-based dict: {name: {approved: ..., rejected: ..., total: ..., etc.}}
    #         name_based_department_breakdown = {}
    #         for dc in department_counts.values():
    #             name = dc['name']
    #             name_based_department_breakdown[name] = {k: v for k, v in dc.items() if k != 'name'}
            
    #         return {
    #             'total_tickets': total_tickets,
    #             'approved_count': approved_count,
    #             'rejected_count': rejected_count,
    #             'pending_count': pending_count,
    #             'overdue_count': overdue_count,  # Added
    #             'on_hold_count': on_hold_count,
    #             'sla_breached_count': sla_breached_count,
    #             'average_response_time': round(average_response_time, 2),  # Average approver response time in hours
    #             'priority_breakdown': name_based_priority_breakdown,  # Dict keyed by priority name, including total and overdue
    #             'department_breakdown': name_based_department_breakdown,  # Dict keyed by department name, including total and overdue
    #         }

    #     hod_data = []
    #     for hod in hods:
    #         base_data = UserSerializer(hod).data
    #         counts = get_hod_counts(hod)
    #         hod_dict = {**base_data, **counts}
    #         hod_data.append(hod_dict)

    #     return Response(hod_data, status=status.HTTP_200_OK)
    def get_approver_stats(self, approver):
        """Helper function to get approval stats for any approver (HOD or user)."""
        approver_logs_qs = TicketApprovalLog.objects.filter(created_by=approver).select_related('ticket')
        
        # Total tickets handled by this approver (unique tickets from logs)
        total_tickets = CreateTicket.objects.filter(
            id__in=approver_logs_qs.values_list('ticket', flat=True).distinct()
        ).count()
        
        # Overall counts (not priority-specific)
        approved_count = approver_logs_qs.filter(approved_by=approver).count()
        rejected_count = approver_logs_qs.filter(status__iexact='Rejected').count()
        on_hold_count = approver_logs_qs.filter(status__iexact='OnHold').count()
        pending_count = approver_logs_qs.filter(status__iexact='Pending').count()
        overdue_count = approver_logs_qs.filter(status__iexact='Pending', sla_breach=True).count()  # Added overdue count
        sla_breached_count = approver_logs_qs.filter(sla_breach=True).count()
        
        # Calculate average response time for resolved approvals (Approved or Rejected)
        resolved_logs = approver_logs_qs.filter(status__in=['Approved', 'Rejected'])
        average_response_time = 0
        if resolved_logs.exists():
            response_times = []
            for log in resolved_logs:
                if log.approved_on and log.created_on:
                    delta = log.approved_on - log.created_on
                    response_times.append(delta.total_seconds() / 3600.0)  # in hours
            average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Priority-based full counts: group by ticket's priority_id from CreateTicket
        # Assuming CreateTicket has 'priority_id' field referencing TicketsMasterConfiguration
        priority_logs = approver_logs_qs.values(
            'ticket__priority_id', 'status', 'sla_breach', 'approved_by'
        )
        
        # Fetch all priority configurations for reference (moved outside if possible, but keeping here for generality)
        priority_configs = TicketsMasterConfiguration.objects.filter(field_type__iexact='priority').values_list('id', 'field_name')
        priority_map = {config[0]: config[1] for config in priority_configs}  # {priority_id: priority_name}
        
        # Use a dict to group counts by priority_id
        priority_counts = {}
        for log in priority_logs:
            priority_id = log['ticket__priority_id']
            if priority_id not in priority_counts:
                priority_counts[priority_id] = {
                    'name': priority_map.get(priority_id, f'Priority {priority_id}'),  # Use name from config
                    'approved': 0,
                    'rejected': 0,
                    'pending': 0,
                    'on_hold': 0,
                    'overdue': 0,  # Added overdue
                    'sla_breached': 0,
                    'total': 0,  # Total logs for this priority
                }
            
            # Increment total for each log
            priority_counts[priority_id]['total'] += 1
            
            if log['approved_by'] == approver.id:  # Compare IDs for safety
                priority_counts[priority_id]['approved'] += 1
            status_lower = (log['status'] or '').lower()
            if 'rejected' in status_lower:
                priority_counts[priority_id]['rejected'] += 1
            if 'pending' in status_lower:
                priority_counts[priority_id]['pending'] += 1
            if 'onhold' in status_lower:
                priority_counts[priority_id]['on_hold'] += 1
            if status_lower == 'pending' and log['sla_breach']:  # Overdue logic
                priority_counts[priority_id]['overdue'] += 1
            if log['sla_breach']:
                priority_counts[priority_id]['sla_breached'] += 1
        
        # Transform to name-based dict: {name: {approved: ..., rejected: ..., total: ..., etc.}}
        name_based_priority_breakdown = {}
        for pc in priority_counts.values():
            name = pc['name']
            name_based_priority_breakdown[name] = {k: v for k, v in pc.items() if k != 'name'}
        
        # Department-based full counts: group by ticket's department_id from CreateTicket
        # Assuming CreateTicket has 'department_id' field referencing TicketsMasterConfiguration
        department_logs = approver_logs_qs.values(
            'ticket__department_id', 'status', 'sla_breach', 'approved_by'
        )
        
        # Fetch all department configurations for reference (moved outside if possible, but keeping here for generality)
        department_configs = TicketsMasterConfiguration.objects.filter(field_type__iexact='department').values_list('id', 'field_name')
        department_map = {config[0]: config[1] for config in department_configs}  # {department_id: department_name}
        
        # Use a dict to group counts by department_id
        department_counts = {}
        for log in department_logs:
            department_id = log['ticket__department_id']
            if department_id not in department_counts:
                department_counts[department_id] = {
                    'name': department_map.get(department_id, f'Department {department_id}'),  # Use name from config
                    'approved': 0,
                    'rejected': 0,
                    'pending': 0,
                    'on_hold': 0,
                    'overdue': 0,  # Added overdue
                    'sla_breached': 0,
                    'total': 0,  # Total logs for this department
                }
            
            # Increment total for each log
            department_counts[department_id]['total'] += 1
            
            if log['approved_by'] == approver.id:  # Compare IDs for safety
                department_counts[department_id]['approved'] += 1
            status_lower = (log['status'] or '').lower()
            if 'rejected' in status_lower:
                department_counts[department_id]['rejected'] += 1
            if 'pending' in status_lower:
                department_counts[department_id]['pending'] += 1
            if 'onhold' in status_lower:
                department_counts[department_id]['on_hold'] += 1
            if status_lower == 'pending' and log['sla_breach']:  # Overdue logic
                department_counts[department_id]['overdue'] += 1
            if log['sla_breach']:
                department_counts[department_id]['sla_breached'] += 1
        
        # Transform to name-based dict: {name: {approved: ..., rejected: ..., total: ..., etc.}}
        name_based_department_breakdown = {}
        for dc in department_counts.values():
            name = dc['name']
            name_based_department_breakdown[name] = {k: v for k, v in dc.items() if k != 'name'}
        
        return {
            'total_tickets': total_tickets,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
            'overdue_count': overdue_count,  # Added
            'on_hold_count': on_hold_count,
            'sla_breached_count': sla_breached_count,
            'average_response_time': round(average_response_time, 2),  # Average approver response time in hours
            'priority_breakdown': name_based_priority_breakdown,  # Dict keyed by priority name, including total and overdue
            'department_breakdown': name_based_department_breakdown,  # Dict keyed by department name, including total and overdue
        }

    def get(self, request):
        """Retrieve all HOD users with ticket approval counts (approved, rejected, pending, on_hold, overdue, sla_breached) 
        including breakdowns by priority and department from TicketsMasterConfiguration,
        and average approver response time in hours.
        For each HOD, include a list of non-HOD users in their department with their respective ticket approval details."""
        hods = User.objects.filter(is_hod=True)
        
        hod_data = []
        for hod in hods:
            base_data = UserSerializer(hod).data
            counts = self.get_approver_stats(hod)
            
            # Get non-HOD users in the same department (assuming User has 'department_id' field)
            department_users = User.objects.filter(department_id=hod.department_id, is_hod=False)
            
            user_data = []
            for user in department_users:
                user_base = UserSerializer(user).data
                user_counts = self.get_approver_stats(user)
                user_dict = {**user_base, **user_counts}
                user_data.append(user_dict)
            
            hod_dict = {**base_data, **counts, 'department_users': user_data}
            hod_data.append(hod_dict)

        return Response(hod_data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Create a new HOD user"""
        data = request.data.copy()  # Make a mutable copy
        data["is_hod"] = True  # Force the new user to be a HOD
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "HOD user created successfully", "user": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntityAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        pk = request.query_params.get('id', None)
        if pk:
            entity = get_object_or_404(Entity, pk=pk)
            serializer = EntitySerializer(entity)
            return Response(serializer.data)
        entities = Entity.objects.all()
        serializer = EntitySerializer(entities, many=True)
        return Response(serializer.data)

    def post(self, request):
        pk = request.data.get('id', None)
        user = str(request.user) if request.user.is_authenticated else 'Anonymous'

        if pk:
            # Update existing entity
            entity = get_object_or_404(Entity, pk=pk)
            serializer = EntitySerializer(entity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=user, updated_date=timezone.now())
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create new entity
        serializer = EntitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                created_by=user,
                updated_by=user,
                created_date=timezone.now(),
                updated_date=timezone.now()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
            return Response({'error': 'ID required for update'}, status=status.HTTP_400_BAD_REQUEST)

        entity = get_object_or_404(Entity, pk=pk)
        serializer = EntitySerializer(entity, data=request.data, partial=True)
        if serializer.is_valid():
            user = str(request.user) if request.user.is_authenticated else 'Anonymous'
            serializer.save(updated_by=user, updated_date=timezone.now())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({'error': 'ID required for delete'}, status=status.HTTP_400_BAD_REQUEST)
        entity = get_object_or_404(Entity, pk=pk)
        entity.is_active = False
        entity.save()
        return Response({'success': 'Entity marked inactive'})

    
class TicketSubcategoryListCreateView(APIView):
    # permission_classes = [IsAuthenticated]  # Requires authentication for all operations
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        # GET all ticket subcategories, with optional category_id filter
        category_id = request.query_params.get('category_id')
        queryset = TicketSubcategory.objects.all()
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        serializer = TicketSubcategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # POST new ticket subcategory
        serializer = TicketSubcategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                created_date=timezone.now(),
                updated_date=timezone.now(),
                created_by=request.user.username if request.user.is_authenticated else None,
                updated_by=request.user.username if request.user.is_authenticated else None
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TicketSubcategoryRetrieveUpdateView(APIView):
    # permission_classes = [IsAuthenticated]  # Requires authentication for all operations
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return TicketSubcategory.objects.get(pk=pk)
        except TicketSubcategory.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        # GET single ticket subcategory
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSubcategorySerializer(instance)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        # PUT update ticket subcategory
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSubcategorySerializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save(
                updated_date=timezone.now(),
                updated_by=request.user.username if request.user.is_authenticated else None
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



def is_privileged(user):
    return getattr(user, "is_superuser", False) or getattr(user, "is_staff", False) or getattr(user, "is_hod", False)

# class CreateTicketView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def get(self, request, ticket_no=None):
#         if ticket_no is not None:
#             try:
#                 ticket = get_object_or_404(
#                     CreateTicket.objects.select_related("type", "department", "location", "priority", "status"),
#                     ticket_no=ticket_no,
#                 )
#             except Exception as e:
#                 print("erro :",e)

#             # Only owner or privileged can view
#             if not is_privileged(request.user) and ticket.requested_id != request.user.id:
#                 return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#             data = CreateTicketSerializer(ticket, context={"request": request}).data
            
#             return Response(data, status=status.HTTP_200_OK)

#         # List: show only my tickets unless privileged
#         qs = CreateTicket.objects.select_related("type", "department", "location", "priority", "status")
#         if not is_privileged(request.user):
#             qs = qs.filter(requested=request.user)

#         data = CreateTicketSerializer(qs, many=True, context={"request": request}).data
#         return Response(data, status=status.HTTP_200_OK)
    


#     def post(self, request, ticket_no=None):
#         print("🔍 Incoming data:", request.data)
#         print("🔍 Incoming FILES:", request.FILES)

#         try:
#             serializer = CreateTicketSerializer(data=request.data, context={"request": request})
#             serializer.is_valid(raise_exception=True)

#             # ✅ Save ticket with logged-in user as requester
#             ticket = serializer.save(requested=request.user)

#             # ✅ Handle uploaded documents
#             for f in request.FILES.getlist("documents"):
#                 TicketDocument.objects.create(ticket=ticket, file=f)

#             current_site = request.build_absolute_uri(f'api/tickets/tickets/{ticket.id}/')
#             creator_user = request.user
#             creator_email = getattr(creator_user, 'email', None)

#             # ✅ Send confirmation email to requester
#             email_template_obj = TicketEmailTemplate.objects.filter(
#                 email_event='Approval',
#                 is_active='Y'
#             ).first()

#             if email_template_obj and creator_email:
#                 template = Template(email_template_obj.email_template)
#                 context = Context({
#                     'firstname': getattr(creator_user, 'firstname', '-') or '',
#                     'realname': getattr(creator_user, 'realname', '-') or '',
#                     'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#                     'name': ticket.title or ticket.description,
#                     'ticket_url': current_site,
#                     'mail_signature': 'IT Support Team',
#                     'year': timezone.now().year,
#                 })
#                 html_content = template.render(context)
#                 send_email_task.delay(
#                     [creator_email],
#                     f"Ticket #{ticket.ticket_no} Created Successfully",
#                     html_content
#                 )

#             # ✅ Handle SLA & approvers
#             sla = TicketSLA.objects.filter(
#                 category_id=ticket.category_id,
#                 subcategory_id=getattr(ticket, 'subcategory_id', None),
#                 is_active='Y'
#             ).first()

#             if sla:
#                 approvers = [
#                     sla.Approver_level1_user,
#                     sla.Approver_level2_user,
#                     sla.Approver_level3_user,
#                     sla.Approver_level4_user,
#                     sla.Approver_level5_user,
#                 ]
#                 approvers = [a for a in approvers if a]  # remove blanks
#                 ticket.total_approval_levels = len(approvers)
#                 ticket.save()

#                 if approvers:
#                     # ✅ Assign to first approver
#                     first_approver = approvers[0]
#                     ticket.current_approver = first_approver
#                     ticket.save()

#                     # ✅ Notify first approver
#                     if email_template_obj:
#                         template = Template(email_template_obj.email_template)
#                         context = Context({
#                             'requester': f"{getattr(creator_user, 'firstname', '-') or ''} {getattr(creator_user, 'realname', '-') or ''}",
#                             'ticket_no': ticket.ticket_no,
#                             'title': ticket.title,
#                             'description': ticket.description,
#                             'ticket_url': f"http://yourdomain.com/tickets/{ticket.id}",
#                             'created_date': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#                             'year': timezone.now().year,
#                         })
#                         html_content = template.render(context)
#                         send_email_task.delay(
#                             [first_approver.email],
#                             f"Ticket #{ticket.ticket_no} Requires Your Approval",
#                             html_content
#                         )

#                     # ✅ Schedule SLA timeout check
#                     sla_time_text = getattr(sla, "sla_time", "1 working day")
#                     sla_hours = parse_sla_time_to_hours(sla_time_text)  # convert text to hours (e.g., 1.5 → 36 hrs)
#                     print(f"⏱ Scheduling SLA check in {sla_hours} hours for ticket {ticket.ticket_no}")

#                     check_approver_timeout.apply_async(
#                         args=[ticket.id, 1],  # ticket id + level 1
#                         countdown=sla_hours * 3600
#                     )

#             data = CreateTicketSerializer(ticket, context={"request": request}).data
#             return Response(data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             print("❌ Ticket creation failed:", e)
#             return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
# def resolve_user_email(approver_name):
#     """Finds the email of a user from the name or email text."""
#     if not approver_name:
#         return None



# class TicketView(APIView):
#     def get(self, request):
#         """Return only ticket statistics (counts)"""
#         qs = CreateTicket.objects.all()

#         # Restrict tickets for non-privileged users
#         if not is_privileged(request.user):
#             qs = qs.filter(requested=request.user)

#         # Current time references
#         now = timezone.now()
#         start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

#         # Use the correct date field from your model
#         total_tickets = qs.count()
#         tickets_this_month = qs.filter(created_date__gte=start_of_month).count()
#         tickets_today = qs.filter(created_date__gte=start_of_day).count()

#         data = {
#             "total_tickets": total_tickets,
#             "tickets_this_month": tickets_this_month,
#             "tickets_today": tickets_today,
#         }

#         return Response(data, status=status.HTTP_200_OK)

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CreateTicket

def is_privileged(user):
    """Helper function to check if user is privileged (e.g., superuser or staff)"""
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# 10/11/2025
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from django.utils import timezone
# from datetime import timedelta
# from calendar import monthrange
# from .models import CreateTicket, TicketApprovalLog  # Make sure imports are correct


# class TicketView(APIView):
#     def get(self, request):
#         """Return ticket statistics including user, watcher, and overall stats with month-wise breakdown"""

#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()

#         now = timezone.now()
#         base_qs = CreateTicket.objects.all()
#         user_requested_qs = base_qs.filter(requested=request.user)
#         user_assigned_qs = base_qs.filter(assignee=str(request.user.id))  # Assignee is CharField

#         # --- Date filter ---
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)

#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 user_assigned_qs = user_assigned_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 base_qs = base_qs.filter(created_date__gte=start_date, created_date__lte=end_date)
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         # --- Search filter ---
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)
#             user_assigned_qs = user_assigned_qs.filter(search_filter)
#             base_qs = base_qs.filter(search_filter)

#         user_combined_qs = (user_requested_qs | user_assigned_qs).distinct()

#         # --- SLA breached helper ---
#         def count_sla_breached(tickets_qs):
#             return TicketApprovalLog.objects.filter(
#                 sla_breach=True,
#                 ticket__in=tickets_qs
#             ).values('ticket').distinct().count()

#         # --- User stats ---
#         data = {
#             "user_stats": {
#                 "total_tickets": user_combined_qs.count(),
#                 "new_assigned": user_assigned_qs.filter(status__field_values__iexact='New').count(),
#                 "solved": user_combined_qs.filter(status__field_values__iexact='Solved').count(),
#                 "closed": user_combined_qs.filter(status__field_values__iexact='Closed').count(),
#                 "pending": user_requested_qs.filter(status__field_values__iexact='Pending').count(),
#                 "approved": user_requested_qs.filter(status__field_values__iexact='Approved').count(),
#                 "rejected": user_requested_qs.filter(status__field_values__iexact='Rejected').count(),
#                 "on_hold": user_requested_qs.filter(status__field_values__iexact='On Hold').count(),
#                 "sla_breached": count_sla_breached(user_requested_qs),
#             }
#         }

#         # --- Watcher stats ---
#         watcher_ticket_qs = CreateTicket.objects.filter(watchers=request.user).distinct()
#         watcher_ticket_qs = watcher_ticket_qs.filter(
#             created_date__gte=start_date if start_date else timezone.make_aware(timezone.datetime(2000,1,1)),
#             created_date__lte=end_date if end_date else now
#         )
#         if search:
#             watcher_ticket_qs = watcher_ticket_qs.filter(search_filter)

#         data["watcher_stats"] = {
#             "pending": watcher_ticket_qs.filter(status__field_values__iexact='Pending').count(),
#             "approved": watcher_ticket_qs.filter(status__field_values__iexact='Approved').count(),
#             "rejected": watcher_ticket_qs.filter(status__field_values__iexact='Rejected').count(),
#             "on_hold": watcher_ticket_qs.filter(status__field_values__iexact='On Hold').count(),
#             "sla_breached": count_sla_breached(watcher_ticket_qs),
#         }

#         # --- Overall stats (all users, month-wise breakdown) ---
#         today_start = timezone.make_aware(timezone.datetime(now.year, now.month, now.day))
#         today_end = today_start + timedelta(days=1) - timedelta(seconds=1)

#         month_start = timezone.make_aware(timezone.datetime(now.year, now.month, 1))
#         last_day = monthrange(now.year, now.month)[1]
#         month_end = timezone.make_aware(timezone.datetime(now.year, now.month, last_day, 23, 59, 59))

#         # Month-wise stats
#         month_stats = []
#         for month in range(1, 13):
#             first_day = timezone.make_aware(timezone.datetime(now.year, month, 1))
#             last_day = monthrange(now.year, month)[1]
#             last_day_date = timezone.make_aware(timezone.datetime(now.year, month, last_day, 23, 59, 59))
#             month_qs = base_qs.filter(created_date__gte=first_day, created_date__lte=last_day_date)
#             month_stats.append({
#                 "month": first_day.strftime("%B"),
#                 "total_tickets": month_qs.count(),
#                 "pending": month_qs.filter(status__field_values__iexact='Pending').count(),
#                 "approved": month_qs.filter(status__field_values__iexact='Approved').count(),
#                 "rejected": month_qs.filter(status__field_values__iexact='Rejected').count(),
#                 "on_hold": month_qs.filter(status__field_values__iexact='On Hold').count(),
#                 "sla_breached": count_sla_breached(month_qs),
#             })

#         data["overall_stats"] = {
#             "total_tickets": base_qs.count(),
#             "today_tickets": base_qs.filter(created_date__gte=today_start, created_date__lte=today_end).count(),
#             "month_tickets": base_qs.filter(created_date__gte=month_start, created_date__lte=month_end).count(),
#             "pending": base_qs.filter(status__field_values__iexact='Pending').count(),
#             "approved": base_qs.filter(status__field_values__iexact='Approved').count(),
#             "rejected": base_qs.filter(status__field_values__iexact='Rejected').count(),
#             "on_hold": base_qs.filter(status__field_values__iexact='On Hold').count(),
#             "sla_breached": count_sla_breached(base_qs),
#             "month_wise": month_stats
#         }

#         return Response(data, status=status.HTTP_200_OK)
# ----------------------------------- 
from datetime import timedelta
from calendar import monthrange
from django.utils import timezone
# Assuming other necessary imports are already present, like:
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from .models import CreateTicket, TicketApprovalLog  # Adjust as per your models
 
# class TicketView(APIView):
#     def get(self, request):
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
 
#         now = timezone.now()
#         base_qs = CreateTicket.objects.all()
#         user_requested_qs = base_qs.filter(requested=request.user)
#         user_assigned_qs = base_qs.filter(assignee=str(request.user.id))

#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 base_qs = base_qs.filter(entity_id=entity_id)
#                 user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
#                 user_assigned_qs = user_assigned_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
 
#         # --- Date filter ---
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 user_assigned_qs = user_assigned_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 base_qs = base_qs.filter(created_date__gte=start_date, created_date__lte=end_date)
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # --- Search filter ---
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)
#             user_assigned_qs = user_assigned_qs.filter(search_filter)
#             base_qs = base_qs.filter(search_filter)
 
#         user_combined_qs = (user_requested_qs | user_assigned_qs).distinct()
 
#         # --- Helper: serialize ticket ---
#         def serialize_ticket(ticket):
#             return {
#                 "id": ticket.id,
#                 "ticket_no": ticket.ticket_no,
#                 "title": ticket.title,
#                 "description": ticket.description,
#                 "status_detail": {
#                     "field_values": ticket.status.field_values if ticket.status else None
#                 } if ticket.status else None,
#                 "category_detail": {
#                     "id": ticket.category.id if ticket.category else None,
#                     "category_name": ticket.category.category_name if ticket.category else None,
#                     "entity_name": ticket.category.entity.name if ticket.category and ticket.category.entity else None,
#                     "department_name": ticket.category.department.field_name if ticket.category and ticket.category.department else None
#                 } if ticket.category else None,
#                 "subcategory_detail": {
#                     "id": ticket.subcategory.id if ticket.subcategory else None,
#                     "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                 } if ticket.subcategory else None,
#                 "priority_detail": {
#                     "field_values": ticket.priority.field_values if ticket.priority else None
#                 } if ticket.priority else None,
#                 "department_detail": {
#                     "field_name": ticket.department.field_name if ticket.department else None
#                 } if ticket.department else None,
#                 "location_detail": {
#                     "field_name": ticket.location.field_name if ticket.location else None
#                 } if ticket.location else None,
#                 "requested_detail": {
#                         "name": (
#                             f"{getattr(ticket.requested, 'firstname', '')} {getattr(ticket.requested, 'realname', '')}".strip()
#                             or getattr(ticket.requested, 'email', '')
#                             or "Unknown User"
#                         ) if ticket.requested else None,
#                         "email": ticket.requested.email if ticket.requested else None
#                     },
#                 "created_date": ticket.created_date,
#                 # "updated_date": ticket.updated_date,
#                 "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#             }
 
#         # --- SLA & Status Helpers ---
#         def get_sla_breached_data(tickets_qs):
#             breached_ids = TicketApprovalLog.objects.filter(
#                 sla_breach=True, ticket__in=tickets_qs
#             ).values_list('ticket', flat=True).distinct()
#             breached_tickets = tickets_qs.filter(id__in=breached_ids).order_by("-ticket_no")
#             return {
#                 "count": breached_tickets.count(),
#                 "tickets": [serialize_ticket(t) for t in breached_tickets]
#             }
 
#         def get_status_data(tickets_qs, status_value):
#             status_tickets = tickets_qs.filter(status__field_values__iexact=status_value).order_by("-ticket_no")
#             return {
#                 "count": status_tickets.count(),
#                 "tickets": [serialize_ticket(t) for t in status_tickets]
#             }
 
#         def get_approver_status_data(logs_qs, filter_q):
#             filtered_logs = logs_qs.filter(filter_q)
#             ticket_ids = list(filtered_logs.values_list('ticket', flat=True).distinct())
#             if not ticket_ids:
#                 return {"count": 0, "tickets": []}
#             tickets_qs = CreateTicket.objects.filter(id__in=ticket_ids).order_by("-ticket_no")
#             return {
#                 "count": tickets_qs.count(),
#                 "tickets": [serialize_ticket(t) for t in tickets_qs]
#             }
 
#         def get_total_approver_tickets(logs_qs):
#             ticket_ids = list(logs_qs.values_list('ticket', flat=True).distinct())
#             if not ticket_ids:
#                 return 0
#             return CreateTicket.objects.filter(id__in=ticket_ids).count()
 
#         # --- User, Watcher, Approver Stats (unchanged) ---
#         user_sla = get_sla_breached_data(user_requested_qs)
#         user_pending = get_status_data(user_requested_qs, 'Pending')
#         user_approved = get_status_data(user_requested_qs, 'Approved')
#         user_rejected = get_status_data(user_requested_qs, 'Rejected')
#         user_on_hold = get_status_data(user_requested_qs, 'On Hold')
#         user_solved = get_status_data(user_combined_qs, 'Solved')
#         user_closed = get_status_data(user_combined_qs, 'Closed')
#         user_new_assigned = get_status_data(user_assigned_qs, 'New')
 
#         data = {
#             "user_stats": {
#                 "total_tickets": user_combined_qs.count(),
#                 "new_assigned": user_new_assigned["count"],
#                 "new_assigned_tickets": user_new_assigned["tickets"],
#                 "solved": user_solved["count"],
#                 "solved_tickets": user_solved["tickets"],
#                 "closed": user_closed["count"],
#                 "closed_tickets": user_closed["tickets"],
#                 "pending": user_pending["count"],
#                 "pending_tickets": user_pending["tickets"],
#                 "approved": user_approved["count"],
#                 "approved_tickets": user_approved["tickets"],
#                 "rejected": user_rejected["count"],
#                 "rejected_tickets": user_rejected["tickets"],
#                 "on_hold": user_on_hold["count"],
#                 "on_hold_tickets": user_on_hold["tickets"],
#                 "sla_breached_count": user_sla["count"],
#                 "sla_breached_tickets": user_sla["tickets"],
#             }
#         }
 
#         # --- Watcher & Approver stats (keep your original code here) ---
#         # --- WATCHER STATS ---
#         watcher_tickets_qs = CreateTicket.objects.filter(watchers=request.user)
#         if entity_id is not None:
#             watcher_tickets_qs = watcher_tickets_qs.filter(entity_id=entity_id)
#             approver_logs_qs = approver_logs_qs.filter(ticket__entity_id=entity_id)
#         if start_date and end_date:
#             watcher_tickets_qs = watcher_tickets_qs.filter(
#                 created_date__gte=start_date, created_date__lte=end_date
#             )
#         if search:
#             watcher_tickets_qs = watcher_tickets_qs.filter(search_filter)

#         watcher_pending = get_status_data(watcher_tickets_qs, 'Pending')
#         watcher_approved = get_status_data(watcher_tickets_qs, 'Approved')
#         watcher_rejected = get_status_data(watcher_tickets_qs, 'Rejected')
#         watcher_on_hold = get_status_data(watcher_tickets_qs, 'On Hold')
#         watcher_sla = get_sla_breached_data(watcher_tickets_qs)

#         data["watcher_stats"] = {
#             "total_tickets": watcher_tickets_qs.count(),
#             "pending": watcher_pending["count"],
#             "pending_tickets": watcher_pending["tickets"],
#             "approved": watcher_approved["count"],
#             "approved_tickets": watcher_approved["tickets"],
#             "rejected": watcher_rejected["count"],
#             "rejected_tickets": watcher_rejected["tickets"],
#             "on_hold": watcher_on_hold["count"],
#             "on_hold_tickets": watcher_on_hold["tickets"],
#             "sla_breached_count": watcher_sla["count"],
#             "sla_breached_tickets": watcher_sla["tickets"],
#         }

#         # --- APPROVER STATS ---
#         approver_logs_qs = TicketApprovalLog.objects.filter(created_by=request.user)
#         if entity_id is not None:
#             watcher_tickets_qs = watcher_tickets_qs.filter(entity_id=entity_id)
#             approver_logs_qs = approver_logs_qs.filter(ticket__entity_id=entity_id)
#         if start_date and end_date:
#             approver_logs_qs = approver_logs_qs.filter(
#                 created_on__gte=start_date, created_on__lte=end_date
#             )
#         if search:
#             approver_logs_qs = approver_logs_qs.filter(
#                 Q(ticket__title__icontains=search) | Q(ticket__description__icontains=search)
#             )

#         approver_pending = get_approver_status_data(approver_logs_qs, Q(status__iexact='Pending', is_current_level=True))
#         approver_approved = get_approver_status_data(approver_logs_qs, Q(approved_by=request.user))
#         approver_rejected = get_approver_status_data(approver_logs_qs, Q(status__iexact='Rejected'))
#         approver_reassigned = get_approver_status_data(approver_logs_qs, Q(status__iexact='Reassigned'))
#         approver_on_hold = get_approver_status_data(
#             approver_logs_qs, 
#             Q(approval_status__iexact='On-Hold', is_current_level=True) |
#             Q(status__iexact='On-Hold', is_current_level=True)
#         )
#         approver_sla = get_approver_status_data(approver_logs_qs, Q(sla_breach=True))

#         data["approver_stats"] = {
#             "total_tickets": get_total_approver_tickets(approver_logs_qs),
#             "pending": approver_pending["count"],
#             "pending_tickets": approver_pending["tickets"],
#             "approved": approver_approved["count"],
#             "approved_tickets": approver_approved["tickets"],
#             "rejected": approver_rejected["count"],
#             "rejected_tickets": approver_rejected["tickets"],
#             "reassigned": approver_reassigned["count"],
#             "reassigned_tickets": approver_reassigned["tickets"],
#             "on_hold": approver_on_hold["count"],
#             "on_hold_tickets": approver_on_hold["tickets"],
#             "sla_breached_count": approver_sla["count"],
#             "sla_breached_tickets": approver_sla["tickets"],
#         }
#         # ... (your existing watcher_stats and approver_stats code)
 
#         # --- OVERALL STATS + DASHBOARD METRICS ---
 
#         today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#         month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
 
#         overall_pending = get_status_data(base_qs, 'Pending')
#         overall_approved = get_status_data(base_qs, 'Approved')
#         overall_rejected = get_status_data(base_qs, 'Rejected')
#         overall_on_hold = get_status_data(base_qs, 'On Hold')
#         overall_sla = get_sla_breached_data(base_qs)
 
#         # Month-wise Line Chart
#         month_wise = []
#         current_year = now.year
#         for month in range(1, 13):
#             start = timezone.make_aware(timezone.datetime(current_year, month, 1))
#             if month == 12:
#                 end = start.replace(year=current_year + 1, month=1) - timedelta(seconds=1)
#             else:
#                 end = start.replace(month=month + 1, day=1) - timedelta(seconds=1)
#             count = base_qs.filter(created_date__gte=start, created_date__lte=end).count()
#             month_wise.append({
#                 "month": start.strftime("%B"),
#                 "total_tickets": count
#             })
 
#         # Last 7 Days
#         # last_7_days = []
#         # for i in range(6, -1, -1):
#         #     day = (now - timedelta(days=i)).date()
#         #     count = base_qs.filter(created_date__date=day).count()
#         #     last_7_days.append({
#         #         "label": day.strftime("%a"),
#         #         "count": count
#         #     })
#         # Last 7 Days - FINAL WORKING VERSION
#             all_tickets_qs = CreateTicket.objects.all()
#             last_7_days_counts = []
#             day_labels = []

#             today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

#             for i in range(6, -1, -1):
#                 day_start = today_midnight - timedelta(days=i)
#                 day_end = day_start + timedelta(days=1)
                
#                 count = all_tickets_qs.filter(
#                     created_date__gte=day_start,
#                     created_date__lt=day_end
#                 ).count()
                
#                 last_7_days_counts.append(count)
#                 day_labels.append(day_start.strftime("%a"))
#         # FIXED: Open Tickets Age (case-insensitive + valid lookup)
#         open_tickets = base_qs.exclude(
#             Q(status__field_values__iexact='Solved') |
#             Q(status__field_values__iexact='Closed') |
#             Q(status__field_values__iexact='Rejected')
#         )
 
#         open_tickets_age = {
#             "today": 0, "1_day": 0, "2_days": 0, "3_days": 0,
#             "4_days": 0, "5_days": 0, "6_days": 0, "7_plus_days": 0
#         }
#         for ticket in open_tickets:
#             age_days = (now - ticket.created_date).days
#             if age_days == 0:
#                 open_tickets_age["today"] += 1
#             elif age_days == 1:
#                 open_tickets_age["1_day"] += 1
#             elif age_days == 2:
#                 open_tickets_age["2_days"] += 1
#             elif age_days == 3:
#                 open_tickets_age["3_days"] += 1
#             elif age_days == 4:
#                 open_tickets_age["4_days"] += 1
#             elif age_days == 5:
#                 open_tickets_age["5_days"] += 1
#             elif age_days == 6:
#                 open_tickets_age["6_days"] += 1
#             else:
#                 open_tickets_age["7_plus_days"] += 1
 
#         # FIXED: Solving Period (case-insensitive)
#         resolved_tickets = base_qs.filter(
#             Q(status__field_values__iexact='Solved') |
#             Q(status__field_values__iexact='Closed')
#         )
 
#         solving_period = {
#             "less_than_1_day": 0,
#             "1_to_2_days": 0,
#             "3_to_5_days": 0,
#             "6_to_10_days": 0,
#             "more_than_10_days": 0,
#         }
#         for ticket in resolved_tickets:
#             if not ticket.updated_date:
#                 continue
#             days = (ticket.updated_date - ticket.created_date).days
#             if days < 1:
#                 solving_period["less_than_1_day"] += 1
#             elif days <= 2:
#                 solving_period["1_to_2_days"] += 1
#             elif days <= 5:
#                 solving_period["3_to_5_days"] += 1
#             elif days <= 10:
#                 solving_period["6_to_10_days"] += 1
#             else:
#                 solving_period["more_than_10_days"] += 1
 
#         # Final overall_stats
#         data["overall_stats"] = {
#             "total_tickets": base_qs.count(),
#             "today_tickets": base_qs.filter(created_date__gte=today_start).count(),
#             "month_tickets": base_qs.filter(created_date__gte=month_start).count(),
#             "pending": overall_pending["count"],
#             "approved": overall_approved["count"],
#             "rejected": overall_rejected["count"],
#             "on_hold": overall_on_hold["count"],
#             "sla_breached_count": overall_sla["count"],
#             "user_count": get_user_model().objects.filter(is_active=True).count(),
#             "month_wise": month_wise,
#             # "last_7_days": last_7_days,
#             "last_7_days_counts": last_7_days_counts,        # ← array of numbers
#             "last_7_days_labels": day_labels,
#             "open_tickets_age": open_tickets_age,
#             "solving_period": solving_period,
#         }
 
#         return Response(data, status=status.HTTP_200_OK) 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import CreateTicket
from Authenticate.models import UsersGroup
from django.contrib.auth import get_user_model
import json

User = get_user_model()

# class TicketView(APIView):
#     def get(self, request):
#         """Get user ticket stats with New, Solved, and Closed statuses"""
#         # Get query parameters
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
 
#         # Get user's email for assignee matching
#         user_email = request.user.email
        
#         # Base querysets for user - focus on requested tickets for "MY REQUEST"
#         user_requested_qs = CreateTicket.objects.filter(requested=request.user)
        
#         # Apply entity filter
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
 
#         # Apply date filter
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # Apply search filter
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)

#         # Helper function to get tickets by status
#         def get_tickets_by_status(queryset, status_name):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             # Simple serialization - no limit, returns all, dedup by id
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # assigned_users is already a list from JSONField
#                 assigned_users = ticket.assigned_users if ticket.assigned_users else []
                
#                 # assigned_groups is already a list from JSONField
#                 assigned_groups = ticket.assigned_groups if ticket.assigned_groups else []
                
#                 tickets_data.append({
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": {
#                         "id": ticket.requested.id if ticket.requested else None,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'first_name', None) or 
#                             ticket.requested.email
#                         ) if ticket.requested else None,
#                         "email": ticket.requested.email if ticket.requested else None
#                     } if ticket.requested else None,
#                     "assignees": assigned_users,
#                     "assignee": ticket.assignee,  # Legacy
#                     "assigned_groups": assigned_groups,
#                     "assigned_group": {
#                         "id": ticket.assigned_group.id if ticket.assigned_group else None,
#                         "name": ticket.assigned_group.name if ticket.assigned_group else None
#                     } if ticket.assigned_group else None,
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                 })
            
#             return {
#                 "count": len(tickets_data),  # Use len of list to ensure accurate count
#                 "tickets": tickets_data
#             }

#         # Get NEW requested tickets (user requested) - tickets requested by user with status "New"
#         new_tickets = get_tickets_by_status(user_requested_qs, 'New')
        
#         # Get SOLVED requested tickets (user requested)
#         solved_tickets = get_tickets_by_status(user_requested_qs, 'Solved')
        
#         # Get CLOSED requested tickets (user requested)
#         closed_tickets = get_tickets_by_status(user_requested_qs, 'Closed')
        
#         # Total user requested tickets
#         total_user_tickets = user_requested_qs.distinct().count()

#         # Prepare response - use requested keys for compatibility
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "user_stats": {
#                 "total_tickets": total_user_tickets,
#                 "new_assigned": new_tickets["count"],  # Rename to match component, but it's requested
#                 "new_assigned_tickets": new_tickets["tickets"],
#                 "solved": solved_tickets["count"],
#                 "solved_tickets": solved_tickets["tickets"],
#                 "closed": closed_tickets["count"],
#                 "closed_tickets": closed_tickets["tickets"],
#                 "ticket_sources": {
#                     "requested_by_me": user_requested_qs.distinct().count(),
#                 }
#             }
#         }
 
#         return Response(data, status=status.HTTP_200_OK)

# class TicketView(APIView):
#     def get(self, request):
#         """Get user ticket stats with New, Solved, and Closed statuses"""
#         # Get query parameters
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
 
#         # Get user's email for assignee matching
#         user_email = request.user.email
        
#         # Base querysets for user - focus on requested tickets for "MY REQUEST"
#         user_requested_qs = CreateTicket.objects.filter(requested=request.user)
        
#         # Apply entity filter
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
 
#         # Apply date filter
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # Apply search filter
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)

#         # Helper function to get tickets by status
#         def get_tickets_by_status(queryset, status_name):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             # Simple serialization - no limit, returns all, dedup by id
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # assigned_users is already a list from JSONField (assuming list of user IDs or emails)
#                 assigned_user_ids = ticket.assigned_users if ticket.assigned_users else []
                
#                 # assigned_groups is already a list from JSONField (list of group IDs)
#                 assigned_group_ids = ticket.assigned_groups if ticket.assigned_groups else []
                
#                 # Collect all assignees_detail: list of user objects from direct assignees and group members
#                 assignees_detail = []
#                 seen_assignee_ids = set()  # To deduplicate across direct and groups
                
#                 # Handle direct assignees
#                 if assigned_user_ids:
#                     # Assuming assigned_user_ids is list of integers (user IDs); adjust if emails
#                     try:
#                         # Filter users by IDs
#                         direct_users = User.objects.filter(id__in=assigned_user_ids).values(
#                             'id', 'first_name', 'realname', 'email', 'username'
#                         )
#                         for user_data in direct_users:
#                             user_id = user_data['id']
#                             if user_id not in seen_assignee_ids:
#                                 seen_assignee_ids.add(user_id)
#                                 assignees_detail.append({
#                                     "id": user_id,
#                                     "firstname": user_data['first_name'] or user_data['username'] or "Unknown",
#                                     "lastname": user_data['realname'] or "",
#                                     "email": user_data['email'],
#                                     "name": f"{user_data['first_name']} {user_data['realname']}".strip() or user_data['username'] or "Unknown"
#                                 })
#                     except Exception as e:
#                         # If IDs are invalid or emails, handle accordingly
#                         print(f"Error fetching direct assignees: {e}")
                
#                 # Handle group assignees: add group members if no direct or to supplement
#                 if assigned_group_ids:
#                     for group_id in assigned_group_ids:
#                         try:
#                             group = UsersGroup.objects.get(id=group_id)
#                             group_members = group.get_users()
#                             for member in group_members:
#                                 member_id = member.id
#                                 if member_id not in seen_assignee_ids:
#                                     seen_assignee_ids.add(member_id)
#                                     assignees_detail.append({
#                                         "id": member_id,
#                                         "firstname": getattr(member, 'first_name', None) or getattr(member, 'name', None) or getattr(member, 'username', "Unknown"),
#                                         "lastname": getattr(member, 'realname', "") or "",
#                                         "email": member.email,
#                                         "name": f"{getattr(member, 'first_name', '')} {getattr(member, 'realname', '')}".strip() or getattr(member, 'username', "Unknown") or getattr(member, 'name', "Unknown")
#                                     })
#                         except UsersGroup.DoesNotExist:
#                             pass
#                         except Exception as e:
#                             print(f"Error fetching group members: {e}")
                
#                 # Fallback: if still no assignees, use assigned_group details if present
#                 assigned_groups_detail = []
#                 if not assignees_detail and ticket.assigned_group:
#                     assigned_groups_detail = [{
#                         "id": ticket.assigned_group.id,
#                         "name": ticket.assigned_group.name,
#                         "members": [],  # Empty if not populated
#                         "members_count": 0
#                     }]
#                 elif assigned_group_ids:
#                     # Optionally populate full group details with members
#                     for group_id in assigned_group_ids:
#                         try:
#                             group = UsersGroup.objects.get(id=group_id)
#                             group_members = group.get_users()
#                             assigned_groups_detail.append({
#                                 "id": group.id,
#                                 "name": group.name,
#                                 "members": [  # List of member dicts
#                                     {
#                                         "id": m.id,
#                                         "firstname": getattr(m, 'first_name', None) or getattr(m, 'name', None) or getattr(m, 'username', "Unknown"),
#                                         "lastname": getattr(m, 'realname', "") or "",
#                                         "email": m.email,
#                                         "name": f"{getattr(m, 'first_name', '')} {getattr(m, 'realname', '')}".strip() or getattr(m, 'username', "Unknown") or getattr(m, 'name', "Unknown")
#                                     } for m in group_members
#                                 ],
#                                 "members_count": len(group_members)
#                             })
#                         except UsersGroup.DoesNotExist:
#                             pass
                
#                 tickets_data.append({
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": {
#                         "id": ticket.requested.id if ticket.requested else None,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'first_name', None) or 
#                             ticket.requested.email
#                         ) if ticket.requested else None,
#                         "email": ticket.requested.email if ticket.requested else None
#                     } if ticket.requested else None,
#                     "assignees_detail": assignees_detail,  # List of assignee objects (direct + group members)
#                     "assignee": ticket.assignee,  # Legacy single assignee
#                     "assigned_groups_detail": assigned_groups_detail,  # Full group details if needed
#                     "assigned_group": {
#                         "id": ticket.assigned_group.id if ticket.assigned_group else None,
#                         "name": ticket.assigned_group.name if ticket.assigned_group else None
#                     } if ticket.assigned_group else None,
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                 })
            
#             return {
#                 "count": len(tickets_data),  # Use len of list to ensure accurate count
#                 "tickets": tickets_data
#             }

#         # Get NEW requested tickets (user requested) - tickets requested by user with status "New"
#         new_tickets = get_tickets_by_status(user_requested_qs, 'New')
        
#         # Get SOLVED requested tickets (user requested)
#         solved_tickets = get_tickets_by_status(user_requested_qs, 'Solved')
        
#         # Get CLOSED requested tickets (user requested)
#         closed_tickets = get_tickets_by_status(user_requested_qs, 'Closed')
        
#         # Total user requested tickets
#         total_user_tickets = user_requested_qs.distinct().count()

#         # Prepare response - use requested keys for compatibility
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "user_stats": {
#                 "total_tickets": total_user_tickets,
#                 "new_assigned": new_tickets["count"],  # Rename to match component, but it's requested
#                 "new_assigned_tickets": new_tickets["tickets"],
#                 "solved": solved_tickets["count"],
#                 "solved_tickets": solved_tickets["tickets"],
#                 "closed": closed_tickets["count"],
#                 "closed_tickets": closed_tickets["tickets"],
#                 "ticket_sources": {
#                     "requested_by_me": user_requested_qs.distinct().count(),
#                 }
#             }
#         }
 
#         return Response(data, status=status.HTTP_200_OK)    

# class ApproverTicketView(APIView):
#     def get(self, request):
#         # Get query parameters
#         print("data :", request.GET)
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
#         assignee_user = request.query_params.get('assignee_user')
#         assignee_group = request.query_params.get('assignee_group')
 
#         user_email = request.user.email
        
#         # Filter tickets where current user is in assigned_users
#         assigned_tickets_qs = CreateTicket.objects.all()
        
#         # IMPORTANT: Filter tickets where current user is assigned
#         # Check if user ID or email is in assigned_users array
#         current_user_id = request.user.id
#         current_user_email = request.user.email
        
#         # Create a filter for assigned users containing current user
#         assigned_tickets_qs = assigned_tickets_qs.filter(
#             Q(assigned_users__contains=current_user_id) |
#             Q(assigned_users__contains=current_user_email) |
#             Q(assigned_users__contains=f'"{current_user_email}"') |
#             # Also check legacy assignee field
#             Q(assignee=current_user_id)
#         ).distinct()
        
#         print("assigned_tickets_qs count:", assigned_tickets_qs.count())
        
#         # Apply entity filter
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
        
#         # Apply assignee_user filter (if provided)
#         if assignee_user:
#             try:
#                 assignee_user_id = int(assignee_user)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_user_id) |
#                     Q(assigned_users__contains=str(assignee_user_id)) |
#                     Q(assignee=assignee_user_id)
#                 ).distinct()
#             except ValueError:
#                 # Treat as email
#                 assignee_email = assignee_user
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_email) |
#                     Q(assigned_users__contains=f'"{assignee_email}"')
#                 ).distinct()
        
#         # Apply assignee_group filter
#         if assignee_group:
#             try:
#                 assignee_group_id = int(assignee_group)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_groups__contains=assignee_group_id) |
#                     Q(assigned_groups__contains=str(assignee_group_id)) |
#                     Q(assigned_group=assignee_group_id)
#                 ).distinct()
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid assignee_group ID"}, status=400)
 
#         # Apply date filter
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # Apply search filter
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             assigned_tickets_qs = assigned_tickets_qs.filter(search_filter)

#         # Helper functions (keep the same as before)
#         def get_user_details(user_identifier):
#             """Get user details from ID or email"""
#             try:
#                 user_obj = None
                
#                 if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
#                     user_id = int(user_identifier)
#                     user_obj = User.objects.get(id=user_id)
#                 else:
#                     email = str(user_identifier).strip().strip('"\'')
#                     user_obj = User.objects.get(email=email)
                
#                 return {
#                     "id": user_obj.id,
#                     "name": getattr(user_obj, 'first_name', None) or getattr(user_obj, 'name', None) or user_obj.email.split('@')[0],
#                     "email": user_obj.email,
#                     "full_name": f"{user_obj.first_name or ''} {user_obj.realname or ''}".strip() or user_obj.email.split('@')[0]
#                 }
#             except User.DoesNotExist:
#                 identifier_str = str(user_identifier)
#                 return {
#                     "id": None,
#                     "name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
#                     "email": identifier_str if '@' in identifier_str else f"user{identifier_str}@unknown.com",
#                     "full_name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
#                     "is_unknown": True
#                 }
#             except Exception as e:
#                 print(f"Error getting user details for {user_identifier}: {e}")
#                 return {
#                     "id": None,
#                     "name": str(user_identifier),
#                     "email": str(user_identifier) if '@' in str(user_identifier) else f"{user_identifier}@unknown.com",
#                     "full_name": str(user_identifier),
#                     "is_unknown": True
#                 }

#         def get_group_details(group_id):
#             try:
#                 if isinstance(group_id, str) and group_id.isdigit():
#                     group_id = int(group_id)
                    
#                 group = UsersGroup.objects.get(id=group_id)
#                 return {
#                     "id": group.id,
#                     "name": group.name,
#                     "description": group.description if hasattr(group, 'description') else ""
#                 }
#             except UsersGroup.DoesNotExist:
#                 return {
#                     "id": group_id,
#                     "name": f"Group {group_id}",
#                     "description": "Group not found",
#                     "is_unknown": True
#                 }

#         def parse_assigned_users(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         user_detail = get_user_details(item)
#                         result.append(user_detail)
#                 return result
#             except json.JSONDecodeError as e:
#                 print(f"JSON decode error for assigned_users: {value}, error: {e}")
#                 result = []
#                 if isinstance(value, str):
#                     import re
#                     emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
#                     for email in emails:
#                         user_detail = get_user_details(email)
#                         result.append(user_detail)
                    
#                     ids = re.findall(r'\b\d+\b', value)
#                     for id_str in ids:
#                         if id_str not in emails:
#                             user_detail = get_user_details(int(id_str))
#                             result.append(user_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_users: {value}, error: {e}")
#                 return []

#         def parse_assigned_groups(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         group_detail = get_group_details(item)
#                         result.append(group_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_groups: {value}, error: {e}")
#                 return []

#         # Helper function to get tickets by status (same as before)
#         def get_tickets_by_status(queryset, status_name):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # Parse assigned data
#                 assigned_users = parse_assigned_users(ticket.assigned_users)
#                 assigned_groups = parse_assigned_groups(ticket.assigned_groups)
                
#                 # Check if current user is in assigned_users
#                 current_user_in_assigned = any(
#                     user.get('id') == current_user_id or user.get('email') == current_user_email 
#                     for user in assigned_users
#                 )
                
#                 # If current user is not in assigned_users but we got this ticket through assignee filter,
#                 # add current user to the assignees list for display
#                 if not current_user_in_assigned and ticket.assignee == current_user_id:
#                     current_user_detail = get_user_details(current_user_id)
#                     if current_user_detail:
#                         assigned_users.append(current_user_detail)
                
#                 # Get requested user details
#                 requested_user_detail = None
#                 if ticket.requested:
#                     requested_user_detail = {
#                         "id": ticket.requested.id,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'first_name', None) or 
#                             ticket.requested.email
#                         ),
#                         "email": ticket.requested.email
#                     }
                
#                 tickets_data.append({
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": requested_user_detail,
#                     "assignees": assigned_users,  # Detailed user info
#                     "assigned_users": assigned_users,  # Alias for assignees
#                     "assigned_users_count": len(assigned_users),
#                     "assigned_groups": assigned_groups,
#                     "assigned_groups_count": len(assigned_groups),
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                     "has_assignments": len(assigned_users) > 0 or len(assigned_groups) > 0,
#                 })
            
#             return {
#                 "count": len(tickets_data),
#                 "tickets": tickets_data
#             }

#         # Get NEW tickets assigned to current user
#         new_tickets = get_tickets_by_status(assigned_tickets_qs, 'New')
        
#         # Get SOLVED tickets assigned to current user
#         solved_tickets = get_tickets_by_status(assigned_tickets_qs, 'Solved')
        
#         # Get CLOSED tickets assigned to current user
#         closed_tickets = get_tickets_by_status(assigned_tickets_qs, 'Closed')
        
#         # Total tickets assigned to current user
#         total_assigned_tickets = assigned_tickets_qs.distinct().count()

#         # Calculate statistics
#         all_tickets = new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"]
#         total_assigned_users = sum(len(ticket.get("assigned_users", [])) for ticket in all_tickets)
#         total_assigned_groups = sum(len(ticket.get("assigned_groups", [])) for ticket in all_tickets)

#         # Prepare response
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "user_stats": {
#                 "total_tickets": total_assigned_tickets,
#                 "new_assigned": new_tickets["count"],
#                 "new_assigned_tickets": new_tickets["tickets"],
#                 "solved": solved_tickets["count"],
#                 "solved_tickets": solved_tickets["tickets"],
#                 "closed": closed_tickets["count"],
#                 "closed_tickets": closed_tickets["tickets"],
#                 "ticket_sources": {
#                     "assigned_to_me": total_assigned_tickets,
#                 },
#                 "assignment_stats": {
#                     "total_assigned_users": total_assigned_users,
#                     "total_assigned_groups": total_assigned_groups,
#                     "tickets_with_users": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0),
#                     "tickets_with_groups": sum(1 for ticket in all_tickets if ticket.get("assigned_groups_count", 0) > 0),
#                     "tickets_with_both": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0 and ticket.get("assigned_groups_count", 0) > 0),
#                 }
#             },
#             "filters": {
#                 "assignee_user": assignee_user,
#                 "assignee_group": assignee_group,
#                 "entity_id": entity_id,
#                 "search": search if search else None,
#                 "date_range": {
#                     "start_date": start_date_str,
#                     "end_date": end_date_str
#                 } if start_date_str and end_date_str else None
#             }
#         }
 
#         return Response(data, status=status.HTTP_200_OK)

# class TicketView(APIView):
#     def get(self, request):
#         """Get user ticket stats with New, Solved, Closed, and Cancelled statuses"""
#         # Get query parameters
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
 
#         # Get user's email for assignee matching
#         user_email = request.user.email
        
#         # Base querysets for user - focus on requested tickets for "MY REQUEST"
#         user_requested_qs = CreateTicket.objects.filter(requested=request.user)
        
#         # Apply entity filter
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
 
#         # Apply date filter
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # Apply search filter
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)

#         # Helper function to get tickets by status
#         def get_tickets_by_status(queryset, status_name):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             # Simple serialization - no limit, returns all, dedup by id
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # assigned_users is already a list from JSONField (assuming list of user IDs or emails)
#                 assigned_user_ids = ticket.assigned_users if ticket.assigned_users else []
                
#                 # assigned_groups is already a list from JSONField (list of group IDs)
#                 assigned_group_ids = ticket.assigned_groups if ticket.assigned_groups else []
                
#                 # Collect all assignees_detail: list of user objects from direct assignees and group members
#                 assignees_detail = []
#                 seen_assignee_ids = set()  # To deduplicate across direct and groups
                
#                 # Handle direct assignees
#                 if assigned_user_ids:
#                     # Assuming assigned_user_ids is list of integers (user IDs); adjust if emails
#                     try:
#                         # Filter users by IDs
#                         direct_users = User.objects.filter(id__in=assigned_user_ids).values(
#                             'id', 'firstname', 'lastname', 'email', 'username'
#                         )
#                         for user_data in direct_users:
#                             user_id = user_data['id']
#                             if user_id not in seen_assignee_ids:
#                                 seen_assignee_ids.add(user_id)
#                                 assignees_detail.append({
#                                     "id": user_id,
#                                     "firstname": user_data['firstname'] or user_data['username'] or "Unknown",
#                                     "lastname": user_data['lastname'] or "",
#                                     "email": user_data['email'],
#                                     "name": f"{user_data['firstname']} {user_data['lastname']}".strip() or user_data['username'] or "Unknown"
#                                 })
#                     except Exception as e:
#                         # If IDs are invalid or emails, handle accordingly
#                         print(f"Error fetching direct assignees: {e}")
                
#                 # Handle group assignees: add group members if no direct or to supplement
#                 if assigned_group_ids:
#                     for group_id in assigned_group_ids:
#                         try:
#                             group = UsersGroup.objects.get(id=group_id)
#                             group_members = group.get_users()
#                             for member in group_members:
#                                 member_id = member.id
#                                 if member_id not in seen_assignee_ids:
#                                     seen_assignee_ids.add(member_id)
#                                     assignees_detail.append({
#                                         "id": member_id,
#                                         "firstname": getattr(member, 'firstname', None) or getattr(member, 'name', None) or getattr(member, 'username', "Unknown"),
#                                         "lastname": getattr(member, 'lastname', "") or "",
#                                         "email": member.email,
#                                         "name": f"{getattr(member, 'firstname', '')} {getattr(member, 'lastname', '')}".strip() or getattr(member, 'username', "Unknown") or getattr(member, 'name', "Unknown")
#                                     })
#                         except UsersGroup.DoesNotExist:
#                             pass
#                         except Exception as e:
#                             print(f"Error fetching group members: {e}")
                
#                 # Fallback: if still no assignees, use assigned_group details if present
#                 assigned_groups_detail = []
#                 if not assignees_detail and ticket.assigned_group:
#                     assigned_groups_detail = [{
#                         "id": ticket.assigned_group.id,
#                         "name": ticket.assigned_group.name,
#                         "members": [],  # Empty if not populated
#                         "members_count": 0
#                     }]
#                 elif assigned_group_ids:
#                     # Optionally populate full group details with members
#                     for group_id in assigned_group_ids:
#                         try:
#                             group = UsersGroup.objects.get(id=group_id)
#                             group_members = group.get_users()
#                             assigned_groups_detail.append({
#                                 "id": group.id,
#                                 "name": group.name,
#                                 "members": [  # List of member dicts
#                                     {
#                                         "id": m.id,
#                                         "firstname": getattr(m, 'firstname', None) or getattr(m, 'name', None) or getattr(m, 'username', "Unknown"),
#                                         "lastname": getattr(m, 'lastname', "") or "",
#                                         "email": m.email,
#                                         "name": f"{getattr(m, 'firstname', '')} {getattr(m, 'lastname', '')}".strip() or getattr(m, 'username', "Unknown") or getattr(m, 'name', "Unknown")
#                                     } for m in group_members
#                                 ],
#                                 "members_count": len(group_members)
#                             })
#                         except UsersGroup.DoesNotExist:
#                             pass
                
#                 tickets_data.append({
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": {
#                         "id": ticket.requested.id if ticket.requested else None,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'firstname', None) or 
#                             ticket.requested.email
#                         ) if ticket.requested else None,
#                         "email": ticket.requested.email if ticket.requested else None
#                     } if ticket.requested else None,
#                     "assignees_detail": assignees_detail,  # List of assignee objects (direct + group members)
#                     "assignee": ticket.assignee,  # Legacy single assignee
#                     "assigned_groups_detail": assigned_groups_detail,  # Full group details if needed
#                     "assigned_group": {
#                         "id": ticket.assigned_group.id if ticket.assigned_group else None,
#                         "name": ticket.assigned_group.name if ticket.assigned_group else None
#                     } if ticket.assigned_group else None,
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                 })
            
#             return {
#                 "count": len(tickets_data),  # Use len of list to ensure accurate count
#                 "tickets": tickets_data
#             }

#         # Get NEW requested tickets (user requested) - tickets requested by user with status "New"
#         new_tickets = get_tickets_by_status(user_requested_qs, 'New')
        
#         # Get SOLVED requested tickets (user requested)
#         solved_tickets = get_tickets_by_status(user_requested_qs, 'Solved')
        
#         # Get CLOSED requested tickets (user requested)
#         closed_tickets = get_tickets_by_status(user_requested_qs, 'Closed')
        
#         # Get CANCELLED requested tickets (user requested)
#         cancelled_tickets = get_tickets_by_status(user_requested_qs, 'Cancelled')
        
#         # Total user requested tickets
#         total_user_tickets = user_requested_qs.distinct().count()

#         # Prepare response - use requested keys for compatibility
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "user_stats": {
#                 "total_tickets": total_user_tickets,
#                 "new_assigned": new_tickets["count"],  # Rename to match component, but it's requested
#                 "new_assigned_tickets": new_tickets["tickets"],
#                 "solved": solved_tickets["count"],
#                 "solved_tickets": solved_tickets["tickets"],
#                 "closed": closed_tickets["count"],
#                 "closed_tickets": closed_tickets["tickets"],
#                 "cancelled": cancelled_tickets["count"],
#                 "cancelled_tickets": cancelled_tickets["tickets"],
#                 "ticket_sources": {
#                     "requested_by_me": user_requested_qs.distinct().count(),
#                 }
#             }
#         }
 
#         return Response(data, status=status.HTTP_200_OK)    
# class ApproverTicketView(APIView):
#     def get(self, request):
#         # Get query parameters
#         print("data :", request.GET)
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
#         assignee_user = request.query_params.get('assignee_user')
#         assignee_group = request.query_params.get('assignee_group')
 
#         user_email = request.user.email
        
#         # Filter tickets where current user is in assigned_users
#         assigned_tickets_qs = CreateTicket.objects.all()
        
#         # IMPORTANT: Filter tickets where current user is assigned
#         # Check if user ID or email is in assigned_users array
#         current_user_id = request.user.id
#         current_user_email = request.user.email
        
#         # Create a filter for assigned users containing current user
#         assigned_tickets_qs = assigned_tickets_qs.filter(
#             Q(assigned_users__contains=current_user_id) |
#             Q(assigned_users__contains=current_user_email) |
#             Q(assigned_users__contains=f'"{current_user_email}"') |
#             # Also check legacy assignee field
#             Q(assignee=current_user_id)
#         ).distinct()
        
#         print("assigned_tickets_qs count:", assigned_tickets_qs.count())
        
#         # Apply entity filter
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)
        
#         # Apply assignee_user filter (if provided)
#         if assignee_user:
#             try:
#                 assignee_user_id = int(assignee_user)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_user_id) |
#                     Q(assigned_users__contains=str(assignee_user_id)) |
#                     Q(assignee=assignee_user_id)
#                 ).distinct()
#             except ValueError:
#                 # Treat as email
#                 assignee_email = assignee_user
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_email) |
#                     Q(assigned_users__contains=f'"{assignee_email}"')
#                 ).distinct()
        
#         # Apply assignee_group filter
#         if assignee_group:
#             try:
#                 assignee_group_id = int(assignee_group)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_groups__contains=assignee_group_id) |
#                     Q(assigned_groups__contains=str(assignee_group_id)) |
#                     Q(assigned_group=assignee_group_id)
#                 ).distinct()
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid assignee_group ID"}, status=400)
 
#         # Apply date filter
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)
 
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)
 
#         # Apply search filter
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             assigned_tickets_qs = assigned_tickets_qs.filter(search_filter)

#         # def get_user_details(user_identifier):
#         #     try:
#         #         user_obj = None

#         #         # Case 1: ID
#         #         if isinstance(user_identifier, int) or (
#         #             isinstance(user_identifier, str) and user_identifier.isdigit()
#         #         ):
#         #             user_obj = User.objects.filter(id=int(user_identifier)).first()

#         #         # Case 2: Email
#         #         else:
#         #             email = str(user_identifier).strip().strip('"\'')
#         #             user_obj = User.objects.filter(email__iexact=email).first()

#         #         if not user_obj:
#         #             raise User.DoesNotExist

#         #         return {
#         #             "id": user_obj.id,
#         #             "name": user_obj.email.split("@")[0],
#         #             "email": user_obj.email,
#         #             "full_name": user_obj.email,
#         #             "is_unknown": False
#         #         }

#         #     except User.DoesNotExist:
#         #         identifier = str(user_identifier)
#         #         return {
#         #             "id": None,
#         #             "name": identifier.split("@")[0] if "@" in identifier else identifier,
#         #             "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
#         #             "full_name": identifier,
#         #             "is_unknown": True
#         #         }
#         # def get_user_details(user_identifier):
#         #     try:
#         #         user_obj = None
#         #         if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
#         #             user_obj = User.objects.filter(id=int(user_identifier)).first()
#         #         else:
#         #             email = str(user_identifier).strip().strip('"\'')
#         #             user_obj = User.objects.filter(email__iexact=email).first()

#         #         if not user_obj:
#         #             raise User.DoesNotExist

#         #         firstname = getattr(user_obj, 'firstname', None) or getattr(user_obj, 'username', None) or ""
#         #         lastname = getattr(user_obj, 'lastname', "")  # Safe fallback
#         #         full_name = f"{firstname} {lastname}".strip() or user_obj.email.split("@")[0]

#         #         return {
#         #             "id": user_obj.id,
#         #             "name": firstname or user_obj.email.split("@")[0],
#         #             "email": user_obj.email,
#         #             "full_name": full_name,
#         #             "is_unknown": False
#         #         }

#         #     except User.DoesNotExist:
#         #         identifier = str(user_identifier)
#         #         return {
#         #             "id": None,
#         #             "name": identifier.split("@")[0] if "@" in identifier else identifier,
#         #             "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
#         #             "full_name": identifier,
#         #             "is_unknown": True
#         #         }
#         #     except Exception as e:
#         #         print(f"Error in get_user_details for {user_identifier}: {e}")
#         #         return {
#         #             "id": None,
#         #             "name": str(user_identifier),
#         #             "email": str(user_identifier) if "@" in str(user_identifier) else f"{user_identifier}@unknown.com",
#         #             "full_name": str(user_identifier),
#         #             "is_unknown": True
#         # }
#         def get_user_details(user_identifier):
#             """Get user details from ID or email – safe for models without lastname"""
#             try:
#                 user_obj = None

#                 if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
#                     user_obj = User.objects.filter(id=int(user_identifier)).first()
#                 else:
#                     email = str(user_identifier).strip().strip('"\'')
#                     user_obj = User.objects.filter(email__iexact=email).first()

#                 if not user_obj:
#                     raise User.DoesNotExist

#                 # Safely get firstname (or fallback to username/email)
#                 firstname = getattr(user_obj, 'firstname', None) or getattr(user_obj, 'username', None) or ""
#                 # lastname may not exist — use safe getattr with empty fallback
#                 lastname = getattr(user_obj, 'lastname', "")  
#                 full_name = f"{firstname} {lastname}".strip()
#                 if not full_name:
#                     full_name = user_obj.email.split("@")[0]  # fallback to email prefix

#                 return {
#                     "id": user_obj.id,
#                     "name": firstname or user_obj.email.split("@")[0],
#                     "email": user_obj.email,
#                     "full_name": full_name,
#                     "is_unknown": False
#                 }

#             except User.DoesNotExist:
#                 identifier = str(user_identifier)
#                 return {
#                     "id": None,
#                     "name": identifier.split("@")[0] if "@" in identifier else identifier,
#                     "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
#                     "full_name": identifier,
#                     "is_unknown": True
#                 }
#             except Exception as e:
#                 print(f"Unexpected error in get_user_details for {user_identifier}: {e}")
#                 identifier = str(user_identifier)
#                 return {
#                     "id": None,
#                     "name": identifier.split("@")[0] if "@" in identifier else identifier,
#                     "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
#                     "full_name": identifier,
#                     "is_unknown": True
#                 }
#         def get_group_details(group_id):
#             try:
#                 if isinstance(group_id, str) and group_id.isdigit():
#                     group_id = int(group_id)
                    
#                 group = UsersGroup.objects.get(id=group_id)
#                 return {
#                     "id": group.id,
#                     "name": group.name,
#                     "description": group.description if hasattr(group, 'description') else ""
#                 }
#             except UsersGroup.DoesNotExist:
#                 return {
#                     "id": group_id,
#                     "name": f"Group {group_id}",
#                     "description": "Group not found",
#                 }

#         def parse_assigned_users(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         user_detail = get_user_details(item)
#                         result.append(user_detail)
#                 return result
#             except json.JSONDecodeError as e:
#                 print(f"JSON decode error for assigned_users: {value}, error: {e}")
#                 result = []
#                 if isinstance(value, str):
#                     import re
#                     emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
#                     for email in emails:
#                         user_detail = get_user_details(email)
#                         result.append(user_detail)
                    
#                     ids = re.findall(r'\b\d+\b', value)
#                     for id_str in ids:
#                         if id_str not in emails:
#                             user_detail = get_user_details(int(id_str))
#                             result.append(user_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_users: {value}, error: {e}")
#                 return []

#         def parse_assigned_groups(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         group_detail = get_group_details(item)
#                         result.append(group_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_groups: {value}, error: {e}")
#                 return []

#         # Helper function to get tickets by status (same as before)
#         def get_tickets_by_status(queryset, status_name):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # Parse assigned data
#                 assigned_users = parse_assigned_users(ticket.assigned_users)
#                 assigned_groups = parse_assigned_groups(ticket.assigned_groups)
                
#                 # Check if current user is in assigned_users
#                 current_user_in_assigned = any(
#                     user.get('id') == current_user_id or user.get('email') == current_user_email 
#                     for user in assigned_users
#                 )
                
#                 # If current user is not in assigned_users but we got this ticket through assignee filter,
#                 # add current user to the assignees list for display
#                 if not current_user_in_assigned and ticket.assignee == current_user_id:
#                     current_user_detail = get_user_details(current_user_id)
#                     if current_user_detail:
#                         assigned_users.append(current_user_detail)
                
#                 # Get requested user details
#                 requested_user_detail = None
#                 if ticket.requested:
#                     requested_user_detail = {
#                         "id": ticket.requested.id,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'firstname', None) or 
#                             ticket.requested.email
#                         ),
#                         "email": ticket.requested.email
#                     }
                
#                 tickets_data.append({
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": requested_user_detail,
#                     "assignees": assigned_users,  # Detailed user info
#                     "assigned_users": assigned_users,  # Alias for assignees
#                     "assigned_users_count": len(assigned_users),
#                     "assigned_groups": assigned_groups,
#                     "assigned_groups_count": len(assigned_groups),
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                     "has_assignments": len(assigned_users) > 0 or len(assigned_groups) > 0,
#                 })
            
#             return {
#                 "count": len(tickets_data),
#                 "tickets": tickets_data
#             }

#         # Get NEW tickets assigned to current user
#         new_tickets = get_tickets_by_status(assigned_tickets_qs, 'New')
        
#         # Get SOLVED tickets assigned to current user
#         solved_tickets = get_tickets_by_status(assigned_tickets_qs, 'Solved')
        
#         # Get CLOSED tickets assigned to current user
#         closed_tickets = get_tickets_by_status(assigned_tickets_qs, 'Closed')
        
#         # Get CANCELLED tickets assigned to current user
#         cancelled_tickets = get_tickets_by_status(assigned_tickets_qs, 'Cancelled')
        
#         # Total tickets assigned to current user
#         total_assigned_tickets = assigned_tickets_qs.distinct().count()

#         # Calculate statistics
#         all_tickets = new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"]
#         total_assigned_users = sum(len(ticket.get("assigned_users", [])) for ticket in all_tickets)
#         total_assigned_groups = sum(len(ticket.get("assigned_groups", [])) for ticket in all_tickets)

#         # Prepare response
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "user_stats": {
#                 "total_tickets": total_assigned_tickets,
#                 "new_assigned": new_tickets["count"],
#                 "new_assigned_tickets": new_tickets["tickets"],
#                 "solved": solved_tickets["count"],
#                 "solved_tickets": solved_tickets["tickets"],
#                 "closed": closed_tickets["count"],
#                 "closed_tickets": closed_tickets["tickets"],
#                 "cancelled": cancelled_tickets["count"],
#                 "cancelled_tickets": cancelled_tickets["tickets"],
#                 "ticket_sources": {
#                     "assigned_to_me": total_assigned_tickets,
#                 },
#                 "assignment_stats": {
#                     "total_assigned_users": total_assigned_users,
#                     "total_assigned_groups": total_assigned_groups,
#                     "tickets_with_users": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0),
#                     "tickets_with_groups": sum(1 for ticket in all_tickets if ticket.get("assigned_groups_count", 0) > 0),
#                     "tickets_with_both": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0 and ticket.get("assigned_groups_count", 0) > 0),
#                 }
#             },
#             "filters": {
#                 "assignee_user": assignee_user,
#                 "assignee_group": assignee_group,
#                 "entity_id": entity_id,
#                 "search": search if search else None,
#                 "date_range": {
#                     "start_date": start_date_str,
#                     "end_date": end_date_str
#                 } if start_date_str and end_date_str else None
#             }
#         }
 
#         return Response(data, status=status.HTTP_200_OK)
class TicketView(APIView):
    def get(self, request):
        """Get user ticket stats with New, Solved, Closed, Cancelled, Clarification Required, and Clarification Applied statuses"""
        # Get query parameters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        search = request.query_params.get('search', '').strip()
        entity_id = request.query_params.get('entity_id')
 
        # Get user's email for assignee matching
        user_email = request.user.email
        
        # Base querysets for user - focus on requested tickets for "MY REQUEST"
        user_requested_qs = CreateTicket.objects.filter(requested=request.user)
        
        # Apply entity filter
        if entity_id:
            try:
                entity_id = int(entity_id)
                user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid entity_id"}, status=400)
 
        # Apply date filter
        start_date = end_date = None
        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                )
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
                ) + timedelta(days=1) - timedelta(seconds=1)
 
                user_requested_qs = user_requested_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)
 
        # Apply search filter
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            user_requested_qs = user_requested_qs.filter(search_filter)

        # Helper function to get tickets by status
        def get_tickets_by_status(queryset, status_name):
            tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
            # Simple serialization - no limit, returns all, dedup by id
            tickets_data = []
            seen_ids = set()
            for ticket in tickets:
                if ticket.id in seen_ids:
                    continue
                seen_ids.add(ticket.id)
                
                # assigned_users is already a list from JSONField (assuming list of user IDs or emails)
                assigned_user_ids = ticket.assigned_users if ticket.assigned_users else []
                
                # assigned_groups is already a list from JSONField (list of group IDs)
                assigned_group_ids = ticket.assigned_groups if ticket.assigned_groups else []
                
                # Collect all assignees_detail: list of user objects from direct assignees and group members
                assignees_detail = []
                seen_assignee_ids = set()  # To deduplicate across direct and groups
                
                # Handle direct assignees
                if assigned_user_ids:
                    # Assuming assigned_user_ids is list of integers (user IDs); adjust if emails
                    try:
                        # Filter users by IDs
                        direct_users = User.objects.filter(id__in=assigned_user_ids).values(
                            'id', 'first_name', 'last_name', 'email', 'username'
                        )
                        for user_data in direct_users:
                            user_id = user_data['id']
                            if user_id not in seen_assignee_ids:
                                seen_assignee_ids.add(user_id)
                                assignees_detail.append({
                                    "id": user_id,
                                    "firstname": user_data['first_name'] or user_data['username'] or "Unknown",
                                    "lastname": user_data['last_name'] or "",
                                    "email": user_data['email'],
                                    "name": f"{user_data['first_name']} {user_data['last_name']}".strip() or user_data['username'] or "Unknown"
                                })
                    except Exception as e:
                        # If IDs are invalid or emails, handle accordingly
                        print(f"Error fetching direct assignees: {e}")
                
                # Handle group assignees: add group members if no direct or to supplement
                if assigned_group_ids:
                    for group_id in assigned_group_ids:
                        try:
                            group = UsersGroup.objects.get(id=group_id)
                            group_members = group.get_users()
                            for member in group_members:
                                member_id = member.id
                                if member_id not in seen_assignee_ids:
                                    seen_assignee_ids.add(member_id)
                                    assignees_detail.append({
                                        "id": member_id,
                                        "firstname": getattr(member, 'first_name', None) or getattr(member, 'name', None) or getattr(member, 'username', "Unknown"),
                                        "lastname": getattr(member, 'last_name', "") or "",
                                        "email": member.email,
                                        "name": f"{getattr(member, 'first_name', '')} {getattr(member, 'last_name', '')}".strip() or getattr(member, 'username', "Unknown") or getattr(member, 'name', "Unknown")
                                    })
                        except UsersGroup.DoesNotExist:
                            pass
                        except Exception as e:
                            print(f"Error fetching group members: {e}")
                
                # Fallback: if still no assignees, use assigned_group details if present
                assigned_groups_detail = []
                if not assignees_detail and ticket.assigned_group:
                    assigned_groups_detail = [{
                        "id": ticket.assigned_group.id,
                        "name": ticket.assigned_group.name,
                        "members": [],  # Empty if not populated
                        "members_count": 0
                    }]
                elif assigned_group_ids:
                    # Optionally populate full group details with members
                    for group_id in assigned_group_ids:
                        try:
                            group = UsersGroup.objects.get(id=group_id)
                            group_members = group.get_users()
                            assigned_groups_detail.append({
                                "id": group.id,
                                "name": group.name,
                                "members": [  # List of member dicts
                                    {
                                        "id": m.id,
                                        "firstname": getattr(m, 'first_name', None) or getattr(m, 'name', None) or getattr(m, 'username', "Unknown"),
                                        "lastname": getattr(m, 'last_name', "") or "",
                                        "email": m.email,
                                        "name": f"{getattr(m, 'first_name', '')} {getattr(m, 'last_name', '')}".strip() or getattr(m, 'username', "Unknown") or getattr(m, 'name', "Unknown")
                                    } for m in group_members
                                ],
                                "members_count": len(group_members)
                            })
                        except UsersGroup.DoesNotExist:
                            pass
                
                tickets_data.append({
                    "id": ticket.id,
                    "ticket_no": ticket.ticket_no,
                    "title": ticket.title,
                    "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
                    "status": ticket.status.field_name if ticket.status else None,
                    "status_detail": {
                        "id": ticket.status.id if ticket.status else None,
                        "field_name": ticket.status.field_name if ticket.status else None,
                        "field_values": ticket.status.field_values if ticket.status else None
                    } if ticket.status else None,
                    "priority": ticket.priority.field_name if ticket.priority else None,
                    "priority_detail": {
                        "id": ticket.priority.id if ticket.priority else None,
                        "field_name": ticket.priority.field_name if ticket.priority else None,
                        "field_values": ticket.priority.field_values if ticket.priority else None
                    } if ticket.priority else None,
                    "category": ticket.category.category_name if ticket.category else None,
                    "category_detail": {
                        "id": ticket.category.id if ticket.category else None,
                        "category_name": ticket.category.category_name if ticket.category else None,
                    } if ticket.category else None,
                    "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
                    "subcategory_detail": {
                        "id": ticket.subcategory.id if ticket.subcategory else None,
                        "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
                    } if ticket.subcategory else None,
                    "department": ticket.department.field_name if ticket.department else None,
                    "department_detail": {
                        "id": ticket.department.id if ticket.department else None,
                        "field_name": ticket.department.field_name if ticket.department else None
                    } if ticket.department else None,
                    "location": ticket.location.field_name if ticket.location else None,
                    "location_detail": {
                        "id": ticket.location.id if ticket.location else None,
                        "field_name": ticket.location.field_name if ticket.location else None
                    } if ticket.location else None,
                    "requested_by": ticket.requested.email if ticket.requested else None,
                    "requested_detail": {
                        "id": ticket.requested.id if ticket.requested else None,
                        "name": (
                            getattr(ticket.requested, 'name', None) or 
                            getattr(ticket.requested, 'first_name', None) or 
                            ticket.requested.email
                        ) if ticket.requested else None,
                        "email": ticket.requested.email if ticket.requested else None
                    } if ticket.requested else None,
                    "assignees_detail": assignees_detail,  # List of assignee objects (direct + group members)
                    "assignee": ticket.assignee,  # Legacy single assignee
                    "assigned_groups_detail": assigned_groups_detail,  # Full group details if needed
                    "assigned_group": {
                        "id": ticket.assigned_group.id if ticket.assigned_group else None,
                        "name": ticket.assigned_group.name if ticket.assigned_group else None
                    } if ticket.assigned_group else None,
                    "created_date": ticket.created_date,
                    "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
                })
            
            return {
                "count": len(tickets_data),  # Use len of list to ensure accurate count
                "tickets": tickets_data
            }

        # Get NEW requested tickets (user requested) - tickets requested by user with status "New"
        new_tickets = get_tickets_by_status(user_requested_qs, 'New')
        
        # Get SOLVED requested tickets (user requested)
        solved_tickets = get_tickets_by_status(user_requested_qs, 'Solved')
        
        # Get CLOSED requested tickets (user requested)
        closed_tickets = get_tickets_by_status(user_requested_qs, 'Closed')
        
        # Get CANCELLED requested tickets (user requested)
        cancelled_tickets = get_tickets_by_status(user_requested_qs, 'Cancelled')
        
        # Get CLARIFICATION REQUIRED requested tickets (user requested)
        clarification_required_tickets = get_tickets_by_status(user_requested_qs, 'Clarification Required')
        
        # Get CLARIFICATION APPLIED requested tickets (user requested)
        clarification_applied_tickets = get_tickets_by_status(user_requested_qs, 'Clarification Applied')
        
        # Total user requested tickets
        total_user_tickets = user_requested_qs.distinct().count()

        # Prepare response - use requested keys for compatibility
        data = {
            "success": True,
            "user_email": user_email,
            "user_stats": {
                "total_tickets": total_user_tickets,
                "new_assigned": new_tickets["count"],  # Rename to match component, but it's requested
                "new_assigned_tickets": new_tickets["tickets"],
                "solved": solved_tickets["count"],
                "solved_tickets": solved_tickets["tickets"],
                "closed": closed_tickets["count"],
                "closed_tickets": closed_tickets["tickets"],
                "cancelled": cancelled_tickets["count"],
                "cancelled_tickets": cancelled_tickets["tickets"],
                "clarification_required": clarification_required_tickets["count"],
                "clarification_required_tickets": clarification_required_tickets["tickets"],
                "clarification_applied": clarification_applied_tickets["count"],
                "clarification_applied_tickets": clarification_applied_tickets["tickets"],
                "ticket_sources": {
                    "requested_by_me": user_requested_qs.distinct().count(),
                }
            }
        }
 
        return Response(data, status=status.HTTP_200_OK)    
class ApproverTicketView(APIView):
    def get(self, request):
        # Get query parameters
        print("data :", request.GET)
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        search = request.query_params.get('search', '').strip()
        entity_id = request.query_params.get('entity_id')
        assignee_user = request.query_params.get('assignee_user')
        assignee_group = request.query_params.get('assignee_group')
 
        user_email = request.user.email
        
        # Filter tickets where current user is in assigned_users
        assigned_tickets_qs = CreateTicket.objects.all()
        
        # IMPORTANT: Filter tickets where current user is assigned
        # Check if user ID or email is in assigned_users array
        current_user_id = request.user.id
        current_user_email = request.user.email
        
        # Create a filter for assigned users containing current user
        assigned_tickets_qs = assigned_tickets_qs.filter(
            Q(assigned_users__contains=current_user_id) |
            Q(assigned_users__contains=current_user_email) |
            Q(assigned_users__contains=f'"{current_user_email}"') |
            # Also check legacy assignee field
            Q(assignee=current_user_id)
        ).distinct()
        
        print("assigned_tickets_qs count:", assigned_tickets_qs.count())
        
        # Apply entity filter
        if entity_id:
            try:
                entity_id = int(entity_id)
                assigned_tickets_qs = assigned_tickets_qs.filter(entity_id=entity_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid entity_id"}, status=400)
        
        # Apply assignee_user filter (if provided)
        if assignee_user:
            try:
                assignee_user_id = int(assignee_user)
                assigned_tickets_qs = assigned_tickets_qs.filter(
                    Q(assigned_users__contains=assignee_user_id) |
                    Q(assigned_users__contains=str(assignee_user_id)) |
                    Q(assignee=assignee_user_id)
                ).distinct()
            except ValueError:
                # Treat as email
                assignee_email = assignee_user
                assigned_tickets_qs = assigned_tickets_qs.filter(
                    Q(assigned_users__contains=assignee_email) |
                    Q(assigned_users__contains=f'"{assignee_email}"')
                ).distinct()
        
        # Apply assignee_group filter
        if assignee_group:
            try:
                assignee_group_id = int(assignee_group)
                assigned_tickets_qs = assigned_tickets_qs.filter(
                    Q(assigned_groups__contains=assignee_group_id) |
                    Q(assigned_groups__contains=str(assignee_group_id)) |
                    Q(assigned_group=assignee_group_id)
                ).distinct()
            except (ValueError, TypeError):
                return Response({"error": "Invalid assignee_group ID"}, status=400)
 
        # Apply date filter
        start_date = end_date = None
        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                )
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
                ) + timedelta(days=1) - timedelta(seconds=1)
 
                assigned_tickets_qs = assigned_tickets_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)
 
        # Apply search filter
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            assigned_tickets_qs = assigned_tickets_qs.filter(search_filter)

        # Helper functions (keep the same as before)
        def get_user_details(user_identifier):
            """Get user details from ID or email"""
            try:
                user_obj = None
                
                if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
                    user_id = int(user_identifier)
                    user_obj = User.objects.get(id=user_id)
                else:
                    email = str(user_identifier).strip().strip('"\'')
                    user_obj = User.objects.get(email=email)
                
                return {
                    "id": user_obj.id,
                    "name": getattr(user_obj, 'first_name', None) or getattr(user_obj, 'name', None) or user_obj.email.split('@')[0],
                    "email": user_obj.email,
                    "full_name": f"{user_obj.first_name or ''} {user_obj.last_name or ''}".strip() or user_obj.email.split('@')[0]
                }
            except User.DoesNotExist:
                identifier_str = str(user_identifier)
                return {
                    "id": None,
                    "name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
                    "email": identifier_str if '@' in identifier_str else f"user{identifier_str}@unknown.com",
                    "full_name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
                    "is_unknown": True
                }
            except Exception as e:
                print(f"Error getting user details for {user_identifier}: {e}")
                return {
                    "id": None,
                    "name": str(user_identifier),
                    "email": str(user_identifier) if '@' in str(user_identifier) else f"{user_identifier}@unknown.com",
                    "full_name": str(user_identifier),
                    "is_unknown": True
                }

        def get_group_details(group_id):
            try:
                if isinstance(group_id, str) and group_id.isdigit():
                    group_id = int(group_id)
                    
                group = UsersGroup.objects.get(id=group_id)
                return {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description if hasattr(group, 'description') else ""
                }
            except UsersGroup.DoesNotExist:
                return {
                    "id": group_id,
                    "name": f"Group {group_id}",
                    "description": "Group not found",
                    "is_unknown": True
                }

        def parse_assigned_users(value):
            if not value:
                return []
            try:
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if not cleaned_value or cleaned_value == '[]':
                        return []
                    parsed = json.loads(cleaned_value)
                else:
                    parsed = value
                
                if not isinstance(parsed, list):
                    return []
                
                result = []
                for item in parsed:
                    if item is not None:
                        user_detail = get_user_details(item)
                        result.append(user_detail)
                return result
            except json.JSONDecodeError as e:
                print(f"JSON decode error for assigned_users: {value}, error: {e}")
                result = []
                if isinstance(value, str):
                    import re
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
                    for email in emails:
                        user_detail = get_user_details(email)
                        result.append(user_detail)
                    
                    ids = re.findall(r'\b\d+\b', value)
                    for id_str in ids:
                        if id_str not in emails:
                            user_detail = get_user_details(int(id_str))
                            result.append(user_detail)
                return result
            except Exception as e:
                print(f"Error parsing assigned_users: {value}, error: {e}")
                return []

        def parse_assigned_groups(value):
            if not value:
                return []
            try:
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if not cleaned_value or cleaned_value == '[]':
                        return []
                    parsed = json.loads(cleaned_value)
                else:
                    parsed = value
                
                if not isinstance(parsed, list):
                    return []
                
                result = []
                for item in parsed:
                    if item is not None:
                        group_detail = get_group_details(item)
                        result.append(group_detail)
                return result
            except Exception as e:
                print(f"Error parsing assigned_groups: {value}, error: {e}")
                return []

        # Helper function to get tickets by status (same as before)
        def get_tickets_by_status(queryset, status_name):
            tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
            tickets_data = []
            seen_ids = set()
            for ticket in tickets:
                if ticket.id in seen_ids:
                    continue
                seen_ids.add(ticket.id)
                
                # Parse assigned data
                assigned_users = parse_assigned_users(ticket.assigned_users)
                assigned_groups = parse_assigned_groups(ticket.assigned_groups)
                
                # Check if current user is in assigned_users
                current_user_in_assigned = any(
                    user.get('id') == current_user_id or user.get('email') == current_user_email 
                    for user in assigned_users
                )
                
                # If current user is not in assigned_users but we got this ticket through assignee filter,
                # add current user to the assignees list for display
                if not current_user_in_assigned and ticket.assignee == current_user_id:
                    current_user_detail = get_user_details(current_user_id)
                    if current_user_detail:
                        assigned_users.append(current_user_detail)
                
                # Get requested user details
                requested_user_detail = None
                if ticket.requested:
                    requested_user_detail = {
                        "id": ticket.requested.id,
                        "name": (
                            getattr(ticket.requested, 'name', None) or 
                            getattr(ticket.requested, 'first_name', None) or 
                            ticket.requested.email
                        ),
                        "email": ticket.requested.email
                    }
                
                tickets_data.append({
                    "id": ticket.id,
                    "ticket_no": ticket.ticket_no,
                    "title": ticket.title,
                    "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
                    "status": ticket.status.field_name if ticket.status else None,
                    "status_detail": {
                        "id": ticket.status.id if ticket.status else None,
                        "field_name": ticket.status.field_name if ticket.status else None,
                        "field_values": ticket.status.field_values if ticket.status else None
                    } if ticket.status else None,
                    "priority": ticket.priority.field_name if ticket.priority else None,
                    "priority_detail": {
                        "id": ticket.priority.id if ticket.priority else None,
                        "field_name": ticket.priority.field_name if ticket.priority else None,
                        "field_values": ticket.priority.field_values if ticket.priority else None
                    } if ticket.priority else None,
                    "category": ticket.category.category_name if ticket.category else None,
                    "category_detail": {
                        "id": ticket.category.id if ticket.category else None,
                        "category_name": ticket.category.category_name if ticket.category else None,
                    } if ticket.category else None,
                    "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
                    "subcategory_detail": {
                        "id": ticket.subcategory.id if ticket.subcategory else None,
                        "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
                    } if ticket.subcategory else None,
                    "department": ticket.department.field_name if ticket.department else None,
                    "department_detail": {
                        "id": ticket.department.id if ticket.department else None,
                        "field_name": ticket.department.field_name if ticket.department else None
                    } if ticket.department else None,
                    "location": ticket.location.field_name if ticket.location else None,
                    "location_detail": {
                        "id": ticket.location.id if ticket.location else None,
                        "field_name": ticket.location.field_name if ticket.location else None
                    } if ticket.location else None,
                    "requested_by": ticket.requested.email if ticket.requested else None,
                    "requested_detail": requested_user_detail,
                    "assignees": assigned_users,  # Detailed user info
                    "assigned_users": assigned_users,  # Alias for assignees
                    "assigned_users_count": len(assigned_users),
                    "assigned_groups": assigned_groups,
                    "assigned_groups_count": len(assigned_groups),
                    "created_date": ticket.created_date,
                    "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
                    "has_assignments": len(assigned_users) > 0 or len(assigned_groups) > 0,
                })
            
            return {
                "count": len(tickets_data),
                "tickets": tickets_data
            }

        # Get NEW tickets assigned to current user
        new_tickets = get_tickets_by_status(assigned_tickets_qs, 'New')
        
        # Get SOLVED tickets assigned to current user
        solved_tickets = get_tickets_by_status(assigned_tickets_qs, 'Solved')
        
        # Get CLOSED tickets assigned to current user
        closed_tickets = get_tickets_by_status(assigned_tickets_qs, 'Closed')
        
        # Get CANCELLED tickets assigned to current user
        cancelled_tickets = get_tickets_by_status(assigned_tickets_qs, 'Cancelled')
        
        # Get CLARIFICATION REQUIRED tickets assigned to current user
        clarification_required_tickets = get_tickets_by_status(assigned_tickets_qs, 'Clarification Required')
        
        # Get CLARIFICATION APPLIED tickets assigned to current user
        clarification_applied_tickets = get_tickets_by_status(assigned_tickets_qs, 'Clarification Applied')
        
        # Total tickets assigned to current user
        total_assigned_tickets = assigned_tickets_qs.distinct().count()

        # Calculate statistics
        all_tickets = new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"]
        total_assigned_users = sum(len(ticket.get("assigned_users", [])) for ticket in all_tickets)
        total_assigned_groups = sum(len(ticket.get("assigned_groups", [])) for ticket in all_tickets)

        # Prepare response
        data = {
            "success": True,
            "user_email": user_email,
            "user_stats": {
                "total_tickets": total_assigned_tickets,
                "new_assigned": new_tickets["count"],
                "new_assigned_tickets": new_tickets["tickets"],
                "solved": solved_tickets["count"],
                "solved_tickets": solved_tickets["tickets"],
                "closed": closed_tickets["count"],
                "closed_tickets": closed_tickets["tickets"],
                "cancelled": cancelled_tickets["count"],
                "cancelled_tickets": cancelled_tickets["tickets"],
                "clarification_required": clarification_required_tickets["count"],
                "clarification_required_tickets": clarification_required_tickets["tickets"],
                "clarification_applied": clarification_applied_tickets["count"],
                "clarification_applied_tickets": clarification_applied_tickets["tickets"],
                "ticket_sources": {
                    "assigned_to_me": total_assigned_tickets,
                },
                "assignment_stats": {
                    "total_assigned_users": total_assigned_users,
                    "total_assigned_groups": total_assigned_groups,
                    "tickets_with_users": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0),
                    "tickets_with_groups": sum(1 for ticket in all_tickets if ticket.get("assigned_groups_count", 0) > 0),
                    "tickets_with_both": sum(1 for ticket in all_tickets if ticket.get("assigned_users_count", 0) > 0 and ticket.get("assigned_groups_count", 0) > 0),
                }
            },
            "filters": {
                "assignee_user": assignee_user,
                "assignee_group": assignee_group,
                "entity_id": entity_id,
                "search": search if search else None,
                "date_range": {
                    "start_date": start_date_str,
                    "end_date": end_date_str
                } if start_date_str and end_date_str else None
            }
        }
 
        return Response(data, status=status.HTTP_200_OK)    






class AdminTicketView(APIView):
    def get(self, request):
        # Get query parameters
        print("data :", request.GET)
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        search = request.query_params.get('search', '').strip()
        entity_id = request.query_params.get('entity_id')
        assignee_user = request.query_params.get('assignee_user')
        assignee_group = request.query_params.get('assignee_group')
        user_email = request.user.email
       
        # Base queryset: all tickets for admin
        all_tickets_qs = CreateTicket.objects.all()
       
        print("all_tickets_qs count:", all_tickets_qs.count())
       
        # Apply entity filter
        if entity_id:
            try:
                entity_id = int(entity_id)
                all_tickets_qs = all_tickets_qs.filter(entity_id=entity_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid entity_id"}, status=400)
       
        # Apply assignee_user filter (optional for admin to filter by specific user)
        if assignee_user:
            try:
                assignee_user_id = int(assignee_user)
                all_tickets_qs = all_tickets_qs.filter(
                    Q(assigned_users__contains=assignee_user_id) |
                    Q(assigned_users__contains=str(assignee_user_id)) |
                    Q(assignee=assignee_user_id)
                ).distinct()
            except ValueError:
                # Treat as email
                assignee_email = assignee_user
                all_tickets_qs = all_tickets_qs.filter(
                    Q(assigned_users__contains=assignee_email) |
                    Q(assigned_users__contains=f'"{assignee_email}"')
                ).distinct()
       
        # Apply assignee_group filter (optional)
        if assignee_group:
            try:
                assignee_group_id = int(assignee_group)
                all_tickets_qs = all_tickets_qs.filter(
                    Q(assigned_groups__contains=assignee_group_id) |
                    Q(assigned_groups__contains=str(assignee_group_id)) |
                    Q(assigned_group=assignee_group_id)
                ).distinct()
            except (ValueError, TypeError):
                return Response({"error": "Invalid assignee_group ID"}, status=400)
       
        # Apply date filter
        start_date = end_date = None
        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                )
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
                ) + timedelta(days=1) - timedelta(seconds=1)
                all_tickets_qs = all_tickets_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)
        # Apply search filter
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            all_tickets_qs = all_tickets_qs.filter(search_filter)
       
        # Helper functions for approver/admin style
        # def get_user_details(user_identifier):
        #     """Get user details from ID or email"""
        #     try:
        #         user_obj = None
               
        #         if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
        #             user_id = int(user_identifier)
        #             user_obj = User.objects.get(id=user_id)
        #         else:
        #             email = str(user_identifier).strip().strip('"\'')
        #             user_obj = User.objects.get(email=email)
               
        #         return {
        #             "id": user_obj.id,
        #             "name": getattr(user_obj, 'firstname', None) or getattr(user_obj, 'name', None) or user_obj.email.split('@')[0],
        #             "email": user_obj.email,
        #             "full_name": f"{user_obj.firstname or ''} {user_obj.lastname or ''}".strip() or user_obj.email.split('@')[0]
        #         }
        #     except User.DoesNotExist:
        #         identifier_str = str(user_identifier)
        #         return {
        #             "id": None,
        #             "name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
        #             "email": identifier_str if '@' in identifier_str else f"user{identifier_str}@unknown.com",
        #             "full_name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
        #         }
        #     except Exception as e:
        #         print(f"Error getting user details for {user_identifier}: {e}")
        #         return {
        #             "id": None,
        #             "name": str(user_identifier),
        #             "email": str(user_identifier) if '@' in str(user_identifier) else f"{user_identifier}@unknown.com",
        #             "full_name": str(user_identifier),
        #         }
        def get_user_details(user_identifier):
            """Get user details from ID or email – safe for models without lastname"""
            try:
                user_obj = None

                if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
                    user_obj = User.objects.filter(id=int(user_identifier)).first()
                else:
                    email = str(user_identifier).strip().strip('"\'')
                    user_obj = User.objects.filter(email__iexact=email).first()

                if not user_obj:
                    raise User.DoesNotExist

                # Safely get firstname (or fallback to username/email)
                firstname = getattr(user_obj, 'firstname', None) or getattr(user_obj, 'username', None) or ""
                # lastname may not exist — use safe getattr with empty fallback
                lastname = getattr(user_obj, 'lastname', "")  
                full_name = f"{firstname} {lastname}".strip()
                if not full_name:
                    full_name = user_obj.email.split("@")[0]  # fallback to email prefix

                return {
                    "id": user_obj.id,
                    "name": firstname or user_obj.email.split("@")[0],
                    "email": user_obj.email,
                    "full_name": full_name,
                    "is_unknown": False
                }

            except User.DoesNotExist:
                identifier = str(user_identifier)
                return {
                    "id": None,
                    "name": identifier.split("@")[0] if "@" in identifier else identifier,
                    "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
                    "full_name": identifier,
                }
            except Exception as e:
                print(f"Unexpected error in get_user_details for {user_identifier}: {e}")
                identifier = str(user_identifier)
                return {
                    "id": None,
                    "name": identifier.split("@")[0] if "@" in identifier else identifier,
                    "email": identifier if "@" in identifier else f"{identifier}@unknown.com",
                    "full_name": identifier,  
                }
       
        def get_group_details(group_id):
            try:
                if isinstance(group_id, str) and group_id.isdigit():
                    group_id = int(group_id)
                   
                group = UsersGroup.objects.get(id=group_id)
                return {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description if hasattr(group, 'description') else ""
                }
            except UsersGroup.DoesNotExist:
                return {
                    "id": group_id,
                    "name": f"Group {group_id}",
                    "description": "Group not found",
                }
       
        def parse_assigned_users(value):
            if not value:
                return []
            try:
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if not cleaned_value or cleaned_value == '[]':
                        return []
                    parsed = json.loads(cleaned_value)
                else:
                    parsed = value
               
                if not isinstance(parsed, list):
                    return []
               
                result = []
                for item in parsed:
                    if item is not None:
                        user_detail = get_user_details(item)
                        result.append(user_detail)
                return result
            except json.JSONDecodeError as e:
                print(f"JSON decode error for assigned_users: {value}, error: {e}")
                result = []
                if isinstance(value, str):
                    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
                    for email in emails:
                        user_detail = get_user_details(email)
                        result.append(user_detail)
                   
                    ids = re.findall(r'\b\d+\b', value)
                    for id_str in ids:
                        if id_str not in [e for e in emails if e.isdigit()]:  # Avoid duplicate if email is numeric
                            user_detail = get_user_details(int(id_str))
                            result.append(user_detail)
                return result
            except Exception as e:
                print(f"Error parsing assigned_users: {value}, error: {e}")
                return []
       
        def parse_assigned_groups(value):
            if not value:
                return []
            try:
                if isinstance(value, str):
                    cleaned_value = value.strip()
                    if not cleaned_value or cleaned_value == '[]':
                        return []
                    parsed = json.loads(cleaned_value)
                else:
                    parsed = value
               
                if not isinstance(parsed, list):
                    return []
               
                result = []
                for item in parsed:
                    if item is not None:
                        group_detail = get_group_details(item)
                        result.append(group_detail)
                return result
            except Exception as e:
                print(f"Error parsing assigned_groups: {value}, error: {e}")
                return []
       
        # Helper function to get tickets by status (approver/admin style)
        def get_tickets_by_status(queryset, status_name):
            tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
           
            tickets_data = []
            seen_ids = set()
            for ticket in tickets:
                if ticket.id in seen_ids:
                    continue
                seen_ids.add(ticket.id)
               
                # Parse assigned data
                assigned_users = parse_assigned_users(ticket.assigned_users)
                assigned_groups = parse_assigned_groups(ticket.assigned_groups)
               
                # Get requested user details
                requested_user_detail = None
                if ticket.requested:
                    requested_user_detail = {
                        "id": ticket.requested.id,
                        "name": (
                            getattr(ticket.requested, 'name', None) or
                            getattr(ticket.requested, 'firstname', None) or
                            ticket.requested.email
                        ),
                        "email": ticket.requested.email
                    }
               
                tickets_data.append({
                    "id": ticket.id,
                    "ticket_no": ticket.ticket_no,
                    "title": ticket.title,
                    "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
                    "status": ticket.status.field_name if ticket.status else None,
                    "status_detail": {
                        "id": ticket.status.id if ticket.status else None,
                        "field_name": ticket.status.field_name if ticket.status else None,
                        "field_values": ticket.status.field_values if ticket.status else None
                    } if ticket.status else None,
                    "priority": ticket.priority.field_name if ticket.priority else None,
                    "priority_detail": {
                        "id": ticket.priority.id if ticket.priority else None,
                        "field_name": ticket.priority.field_name if ticket.priority else None,
                        "field_values": ticket.priority.field_values if ticket.priority else None
                    } if ticket.priority else None,
                    "category": ticket.category.category_name if ticket.category else None,
                    "category_detail": {
                        "id": ticket.category.id if ticket.category else None,
                        "category_name": ticket.category.category_name if ticket.category else None,
                    } if ticket.category else None,
                    "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
                    "subcategory_detail": {
                        "id": ticket.subcategory.id if ticket.subcategory else None,
                        "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
                    } if ticket.subcategory else None,
                    "department": ticket.department.field_name if ticket.department else None,
                    "department_detail": {
                        "id": ticket.department.id if ticket.department else None,
                        "field_name": ticket.department.field_name if ticket.department else None
                    } if ticket.department else None,
                    "location": ticket.location.field_name if ticket.location else None,
                    "location_detail": {
                        "id": ticket.location.id if ticket.location else None,
                        "field_name": ticket.location.field_name if ticket.location else None
                    } if ticket.location else None,
                    "requested_by": ticket.requested.email if ticket.requested else None,
                    "requested_detail": requested_user_detail,
                    "assignees": assigned_users, # Detailed user info (direct)
                    "assigned_users": assigned_users, # Alias for assignees
                    "assigned_users_count": len(assigned_users),
                    "assigned_groups": assigned_groups,
                    "assigned_groups_count": len(assigned_groups),
                    "created_date": ticket.created_date,
                    "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
                    "has_assignments": len(assigned_users) > 0 or len(assigned_groups) > 0,
                })
           
            return {
                "count": len(tickets_data),
                "tickets": tickets_data
            }
 
        # Helper function to get tickets by status (user style, with assignees_detail)
        def get_user_tickets_by_status(queryset, status_name):
            tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
           
            tickets_data = []
            seen_ids = set()
            for ticket in tickets:
                if ticket.id in seen_ids:
                    continue
                seen_ids.add(ticket.id)
               
                # assigned_users is already a list from JSONField (assuming list of user IDs or emails)
                assigned_user_ids = ticket.assigned_users if ticket.assigned_users else []
               
                # assigned_groups is already a list from JSONField (list of group IDs)
                assigned_group_ids = ticket.assigned_groups if ticket.assigned_groups else []
               
                # Collect all assignees_detail: list of user objects from direct assignees and group members
                               # Handle direct assignees (supports both IDs and emails)
                assignees_detail = []
                seen_assignee_ids = set()

                if assigned_user_ids:
                    user_ids = []
                    user_emails = []

                    # Safely iterate over assigned_user_ids (in case it's not a list)
                    items = assigned_user_ids if isinstance(assigned_user_ids, list) else []
                    for item in items:
                        if isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
                            try:
                                user_ids.append(int(item))
                            except ValueError:
                                pass
                        elif isinstance(item, str) and '@' in item:
                            cleaned = item.strip().strip('"\'')
                            user_emails.append(cleaned)

                    try:
                        # Fetch by IDs
                        if user_ids:
                            for user in User.objects.filter(id__in=user_ids):
                                if user.id not in seen_assignee_ids:
                                    seen_assignee_ids.add(user.id)
                                    assignees_detail.append({
                                        "id": user.id,
                                        "firstname": getattr(user, 'firstname', '') or getattr(user, 'username', '') or "Unknown",
                                        "lastname": getattr(user, 'lastname', '') or "",
                                        "email": user.email,
                                        "name": (
                                            f"{getattr(user, 'firstname', '')} {getattr(user, 'lastname', '')}".strip()
                                            or getattr(user, 'username', '') 
                                            or user.email 
                                            or "Unknown"
                                        )
                                    })

                        # Fetch by emails
                        if user_emails:
                            for user in User.objects.filter(email__in=user_emails):
                                if user.id not in seen_assignee_ids:
                                    seen_assignee_ids.add(user.id)
                                    assignees_detail.append({
                                        "id": user.id,
                                        "firstname": getattr(user, 'firstname', '') or getattr(user, 'username', '') or "Unknown",
                                        "lastname": getattr(user, 'lastname', '') or "",
                                        "email": user.email,
                                        "name": (
                                            f"{getattr(user, 'firstname', '')} {getattr(user, 'lastname', '')}".strip()
                                            or getattr(user, 'username', '') 
                                            or user.email 
                                            or "Unknown"
                                        )
                                    })

                    except Exception as e:
                        print(f"Error fetching direct assignees: {e}")
                # Handle group assignees: add group members if no direct or to supplement
                if assigned_group_ids:
                    for group_id in assigned_group_ids:
                        try:
                            group = UsersGroup.objects.get(id=group_id)
                            group_members = group.get_users()
                            for member in group_members:
                                member_id = member.id
                                if member_id not in seen_assignee_ids:
                                    seen_assignee_ids.add(member_id)
                                    assignees_detail.append({
                                        "id": member_id,
                                        "firstname": getattr(member, 'firstname', None) or getattr(member, 'name', None) or getattr(member, 'username', "Unknown"),
                                        "lastname": getattr(member, 'lastname', "") or "",
                                        "email": member.email,
                                        "name": f"{getattr(member, 'firstname', '')} {getattr(member, 'lastname', '')}".strip() or getattr(member, 'username', "Unknown") or getattr(member, 'name', "Unknown")
                                    })
                        except UsersGroup.DoesNotExist:
                            pass
                        except Exception as e:
                            print(f"Error fetching group members: {e}")
               
                # Fallback: if still no assignees, use assigned_group details if present
                assigned_groups_detail = []
                if not assignees_detail and ticket.assigned_group:
                    assigned_groups_detail = [{
                        "id": ticket.assigned_group.id,
                        "name": ticket.assigned_group.name,
                        "members": [], # Empty if not populated
                        "members_count": 0
                    }]
                elif assigned_group_ids:
                    # Optionally populate full group details with members
                    for group_id in assigned_group_ids:
                        try:
                            group = UsersGroup.objects.get(id=group_id)
                            group_members = group.get_users()
                            assigned_groups_detail.append({
                                "id": group.id,
                                "name": group.name,
                                "members": [ # List of member dicts
                                    {
                                        "id": m.id,
                                        "firstname": getattr(m, 'firstname', None) or getattr(m, 'name', None) or getattr(m, 'username', "Unknown"),
                                        "lastname": getattr(m, 'lastname', "") or "",
                                        "email": m.email,
                                        "name": f"{getattr(m, 'firstname', '')} {getattr(m, 'lastname', '')}".strip() or getattr(m, 'username', "Unknown") or getattr(m, 'name', "Unknown")
                                    } for m in group_members
                                ],
                                "members_count": len(group_members)
                            })
                        except UsersGroup.DoesNotExist:
                            pass
               
                # Get requested user details
                requested_detail = None
                if ticket.requested:
                    requested_detail = {
                        "id": ticket.requested.id,
                        "name": (
                            getattr(ticket.requested, 'name', None) or
                            getattr(ticket.requested, 'firstname', None) or
                            ticket.requested.email
                        ),
                        "email": ticket.requested.email
                    }
               
                tickets_data.append({
                    "id": ticket.id,
                    "ticket_no": ticket.ticket_no,
                    "title": ticket.title,
                    "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
                    "status": ticket.status.field_name if ticket.status else None,
                    "status_detail": {
                        "id": ticket.status.id if ticket.status else None,
                        "field_name": ticket.status.field_name if ticket.status else None,
                        "field_values": ticket.status.field_values if ticket.status else None
                    } if ticket.status else None,
                    "priority": ticket.priority.field_name if ticket.priority else None,
                    "priority_detail": {
                        "id": ticket.priority.id if ticket.priority else None,
                        "field_name": ticket.priority.field_name if ticket.priority else None,
                        "field_values": ticket.priority.field_values if ticket.priority else None
                    } if ticket.priority else None,
                    "category": ticket.category.category_name if ticket.category else None,
                    "category_detail": {
                        "id": ticket.category.id if ticket.category else None,
                        "category_name": ticket.category.category_name if ticket.category else None,
                    } if ticket.category else None,
                    "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
                    "subcategory_detail": {
                        "id": ticket.subcategory.id if ticket.subcategory else None,
                        "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
                    } if ticket.subcategory else None,
                    "department": ticket.department.field_name if ticket.department else None,
                    "department_detail": {
                        "id": ticket.department.id if ticket.department else None,
                        "field_name": ticket.department.field_name if ticket.department else None
                    } if ticket.department else None,
                    "location": ticket.location.field_name if ticket.location else None,
                    "location_detail": {
                        "id": ticket.location.id if ticket.location else None,
                        "field_name": ticket.location.field_name if ticket.location else None
                    } if ticket.location else None,
                    "requested_by": ticket.requested.email if ticket.requested else None,
                    "requested_detail": requested_detail,
                    "assignees_detail": assignees_detail,  # List of assignee objects (direct + group members)
                    # "assignee": ticket.assignee, 
                   "assignee": ticket.assignee if ticket.assignee else None,


                    "assigned_groups_detail": assigned_groups_detail,  # Full group details if needed
                    "assigned_group": {
                        "id": ticket.assigned_group.id if ticket.assigned_group else None,
                        "name": ticket.assigned_group.name if ticket.assigned_group else None
                    } if ticket.assigned_group else None,
                    "created_date": ticket.created_date,
                    "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
                })
           
            return {
                "count": len(tickets_data),
                "tickets": tickets_data
            }
       
        # Compute for user_stats (all created tickets, user style)
        user_new_tickets = get_user_tickets_by_status(all_tickets_qs, 'New')
        user_solved_tickets = get_user_tickets_by_status(all_tickets_qs, 'Solved')
        user_closed_tickets = get_user_tickets_by_status(all_tickets_qs, 'Closed')
        user_cancelled_tickets = get_user_tickets_by_status(all_tickets_qs, 'Cancelled')
        user_clarification_required_tickets = get_user_tickets_by_status(all_tickets_qs, 'Clarification Required')
        user_clarification_applied_tickets = get_user_tickets_by_status(all_tickets_qs, 'Clarification Applied')
       
        total_user_tickets = all_tickets_qs.distinct().count()
       
        user_stats = {
            "total_tickets": total_user_tickets,
            "new_assigned": user_new_tickets["count"],
            "new_assigned_tickets": user_new_tickets["tickets"],
            "solved": user_solved_tickets["count"],
            "solved_tickets": user_solved_tickets["tickets"],
            "closed": user_closed_tickets["count"],
            "closed_tickets": user_closed_tickets["tickets"],
            "cancelled": user_cancelled_tickets["count"],
            "cancelled_tickets": user_cancelled_tickets["tickets"],
            "clarification_required": user_clarification_required_tickets["count"],
            "clarification_required_tickets": user_clarification_required_tickets["tickets"],
            "clarification_applied": user_clarification_applied_tickets["count"],
            "clarification_applied_tickets": user_clarification_applied_tickets["tickets"],
            "ticket_sources": {
                "requested_by_any": total_user_tickets,
            }
        }
       
        # Compute for admin_stats and approver_stats (approver style)
        # Get tickets by status
        new_tickets = get_tickets_by_status(all_tickets_qs, 'New')
        solved_tickets = get_tickets_by_status(all_tickets_qs, 'Solved')
        closed_tickets = get_tickets_by_status(all_tickets_qs, 'Closed')
        cancelled_tickets = get_tickets_by_status(all_tickets_qs, 'Cancelled')
        clarification_required_tickets = get_tickets_by_status(all_tickets_qs, 'Clarification Required')
        clarification_applied_tickets = get_tickets_by_status(all_tickets_qs, 'Clarification Applied')
       
        # Total tickets
        total_tickets = all_tickets_qs.distinct().count()
       
        # For admin_stats: all tickets
        admin_stats = {
            "total_tickets": total_tickets,
            "new_assigned": new_tickets["count"],
            "new_assigned_tickets": new_tickets["tickets"],
            "solved": solved_tickets["count"],
            "solved_tickets": solved_tickets["tickets"],
            "closed": closed_tickets["count"],
            "closed_tickets": closed_tickets["tickets"],
            "cancelled": cancelled_tickets["count"],
            "cancelled_tickets": cancelled_tickets["tickets"],
            "clarification_required": clarification_required_tickets["count"],
            "clarification_required_tickets": clarification_required_tickets["tickets"],
            "clarification_applied": clarification_applied_tickets["count"],
            "clarification_applied_tickets": clarification_applied_tickets["tickets"],
            "ticket_sources": {
                "all_tickets": total_tickets,
            },
            "assignment_stats": {
                "total_assigned_users": sum(len(ticket.get("assigned_users", [])) for ticket in (new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"])),
                "total_assigned_groups": sum(len(ticket.get("assigned_groups", [])) for ticket in (new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"])),
                "tickets_with_users": sum(1 for ticket in (new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"]) if ticket.get("assigned_users_count", 0) > 0),
                "tickets_with_groups": sum(1 for ticket in (new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"]) if ticket.get("assigned_groups_count", 0) > 0),
                "tickets_with_both": sum(1 for ticket in (new_tickets["tickets"] + solved_tickets["tickets"] + closed_tickets["tickets"] + cancelled_tickets["tickets"] + clarification_required_tickets["tickets"] + clarification_applied_tickets["tickets"]) if ticket.get("assigned_users_count", 0) > 0 and ticket.get("assigned_groups_count", 0) > 0),
            }
        }
       
        # For approver_stats: filter to tickets with assignments
        def filter_assigned(status_tickets_dict):
            filtered_tickets = [t for t in status_tickets_dict["tickets"] if t["has_assignments"]]
            return {
                "count": len(filtered_tickets),
                "tickets": filtered_tickets
            }
       
        new_assigned_filtered = filter_assigned(new_tickets)
        solved_filtered = filter_assigned(solved_tickets)
        closed_filtered = filter_assigned(closed_tickets)
        cancelled_filtered = filter_assigned(cancelled_tickets)
        clarification_required_filtered = filter_assigned(clarification_required_tickets)
        clarification_applied_filtered = filter_assigned(clarification_applied_tickets)
       
        all_assigned_tickets = (new_assigned_filtered["tickets"] + solved_filtered["tickets"] +
                                closed_filtered["tickets"] + cancelled_filtered["tickets"] +
                                clarification_required_filtered["tickets"] + clarification_applied_filtered["tickets"])
        total_assigned_tickets = len(all_assigned_tickets)
       
        approver_stats = {
            "total_tickets": total_assigned_tickets,
            "new_assigned": new_assigned_filtered["count"],
            "new_assigned_tickets": new_assigned_filtered["tickets"],
            "solved": solved_filtered["count"],
            "solved_tickets": solved_filtered["tickets"],
            "closed": closed_filtered["count"],
            "closed_tickets": closed_filtered["tickets"],
            "cancelled": cancelled_filtered["count"],
            "cancelled_tickets": cancelled_filtered["tickets"],
            "clarification_required": clarification_required_filtered["count"],
            "clarification_required_tickets": clarification_required_filtered["tickets"],
            "clarification_applied": clarification_applied_filtered["count"],
            "clarification_applied_tickets": clarification_applied_filtered["tickets"],
            "ticket_sources": {
                "assigned_to_any": total_assigned_tickets,
            },
            "assignment_stats": {
                "total_assigned_users": sum(len(t.get("assigned_users", [])) for t in all_assigned_tickets),
                "total_assigned_groups": sum(len(t.get("assigned_groups", [])) for t in all_assigned_tickets),
                "tickets_with_users": sum(1 for t in all_assigned_tickets if t.get("assigned_users_count", 0) > 0),
                "tickets_with_groups": sum(1 for t in all_assigned_tickets if t.get("assigned_groups_count", 0) > 0),
                "tickets_with_both": sum(1 for t in all_assigned_tickets if t.get("assigned_users_count", 0) > 0 and t.get("assigned_groups_count", 0) > 0),
            }
        }
       
        # Prepare response
        data = {
            "success": True,
            "user_email": user_email,
            "user_stats": user_stats,
            "approver_stats": approver_stats,
            "admin_stats": admin_stats,
            "filters": {
                "assignee_user": assignee_user,
                "assignee_group": assignee_group,
                "entity_id": entity_id,
                "search": search if search else None,
                "date_range": {
                    "start_date": start_date_str,
                    "end_date": end_date_str
                } if start_date_str and end_date_str else None
            }
        }
        return Response(data, status=status.HTTP_200_OK)
 
# class AdminTicketView(APIView):
#     """
#     Combined Admin Ticket View: Shows stats and tickets for both requested and assigned,
#     with comparison totals for all statuses.
#     """
#     def get(self, request):
#         # Get query parameters (shared)
#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()
#         entity_id = request.query_params.get('entity_id')
#         assignee_user = request.query_params.get('assignee_user')
#         assignee_group = request.query_params.get('assignee_group')

#         user_email = request.user.email
#         current_user_id = request.user.id
#         current_user_email = request.user.email

#         # Base querysets
#         user_requested_qs = CreateTicket.objects.filter(requested=request.user)
#         assigned_tickets_qs = CreateTicket.objects.all().filter(
#             Q(assigned_users__contains=current_user_id) |
#             Q(assigned_users__contains=current_user_email) |
#             Q(assigned_users__contains=f'"{current_user_email}"') |
#             Q(assignee=current_user_id)
#         ).distinct()

#         # Apply shared filters to both querysets
#         if entity_id:
#             try:
#                 entity_id = int(entity_id)
#                 user_requested_qs = user_requested_qs.filter(entity_id=entity_id)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(entity_id=entity_id)
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid entity_id"}, status=400)

#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)

#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)
#             assigned_tickets_qs = assigned_tickets_qs.filter(search_filter)

#         # Apply assignee filters to assigned_qs only
#         if assignee_user:
#             try:
#                 assignee_user_id = int(assignee_user)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_user_id) |
#                     Q(assigned_users__contains=str(assignee_user_id)) |
#                     Q(assignee=assignee_user_id)
#                 ).distinct()
#             except ValueError:
#                 assignee_email = assignee_user
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_users__contains=assignee_email) |
#                     Q(assigned_users__contains=f'"{assignee_email}"')
#                 ).distinct()

#         if assignee_group:
#             try:
#                 assignee_group_id = int(assignee_group)
#                 assigned_tickets_qs = assigned_tickets_qs.filter(
#                     Q(assigned_groups__contains=assignee_group_id) |
#                     Q(assigned_groups__contains=str(assignee_group_id)) |
#                     Q(assigned_group=assignee_group_id)
#                 ).distinct()
#             except (ValueError, TypeError):
#                 return Response({"error": "Invalid assignee_group ID"}, status=400)

#         # Shared helper functions (using Approver's parse for consistency, adapt for requested)
#         def get_user_details(user_identifier):
#             """Get user details from ID or email"""
#             try:
#                 user_obj = None
                
#                 if isinstance(user_identifier, int) or (isinstance(user_identifier, str) and user_identifier.isdigit()):
#                     user_id = int(user_identifier)
#                     user_obj = User.objects.get(id=user_id)
#                 else:
#                     email = str(user_identifier).strip().strip('"\'')
#                     user_obj = User.objects.get(email=email)
                
#                 return {
#                     "id": user_obj.id,
#                     "name": getattr(user_obj, 'firstname', None) or getattr(user_obj, 'name', None) or user_obj.email.split('@')[0],
#                     "email": user_obj.email,
#                     "full_name": f"{user_obj.firstname or ''} {user_obj.realname or ''}".strip() or user_obj.email.split('@')[0]
#                 }
#             except User.DoesNotExist:
#                 identifier_str = str(user_identifier)
#                 return {
#                     "id": None,
#                     "name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
#                     "email": identifier_str if '@' in identifier_str else f"user{identifier_str}@unknown.com",
#                     "full_name": identifier_str if '@' in identifier_str else f"User {identifier_str}",
#                     "is_unknown": True
#                 }
#             except Exception as e:
#                 print(f"Error getting user details for {user_identifier}: {e}")
#                 return {
#                     "id": None,
#                     "name": str(user_identifier),
#                     "email": str(user_identifier) if '@' in str(user_identifier) else f"{user_identifier}@unknown.com",
#                     "full_name": str(user_identifier),
#                     "is_unknown": True
#                 }

#         def get_group_details(group_id):
#             try:
#                 if isinstance(group_id, str) and group_id.isdigit():
#                     group_id = int(group_id)
                    
#                 group = UsersGroup.objects.get(id=group_id)
#                 return {
#                     "id": group.id,
#                     "name": group.name,
#                     "description": group.description if hasattr(group, 'description') else ""
#                 }
#             except UsersGroup.DoesNotExist:
#                 return {
#                     "id": group_id,
#                     "name": f"Group {group_id}",
#                     "description": "Group not found",
#                     "is_unknown": True
#                 }

#         def parse_assigned_users(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         user_detail = get_user_details(item)
#                         result.append(user_detail)
#                 return result
#             except json.JSONDecodeError as e:
#                 print(f"JSON decode error for assigned_users: {value}, error: {e}")
#                 result = []
#                 if isinstance(value, str):
#                     emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', value)
#                     for email in emails:
#                         user_detail = get_user_details(email)
#                         result.append(user_detail)
                    
#                     ids = re.findall(r'\b\d+\b', value)
#                     for id_str in ids:
#                         if id_str not in emails:
#                             user_detail = get_user_details(int(id_str))
#                             result.append(user_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_users: {value}, error: {e}")
#                 return []

#         def parse_assigned_groups(value):
#             if not value:
#                 return []
#             try:
#                 if isinstance(value, str):
#                     cleaned_value = value.strip()
#                     if not cleaned_value or cleaned_value == '[]':
#                         return []
#                     parsed = json.loads(cleaned_value)
#                 else:
#                     parsed = value
                
#                 if not isinstance(parsed, list):
#                     return []
                
#                 result = []
#                 for item in parsed:
#                     if item is not None:
#                         group_detail = get_group_details(item)
#                         result.append(group_detail)
#                 return result
#             except Exception as e:
#                 print(f"Error parsing assigned_groups: {value}, error: {e}")
#                 return []

#         # Unified helper for tickets by status (adapted for both requested and assigned)
#         def get_tickets_by_status(queryset, status_name, is_requested=False):
#             tickets = queryset.filter(status__field_name__iexact=status_name).distinct().order_by("-ticket_no")
            
#             tickets_data = []
#             seen_ids = set()
#             for ticket in tickets:
#                 if ticket.id in seen_ids:
#                     continue
#                 seen_ids.add(ticket.id)
                
#                 # Parse assigned data (same for both)
#                 assigned_users = parse_assigned_users(ticket.assigned_users)
#                 assigned_groups = parse_assigned_groups(ticket.assigned_groups)
                
#                 # For requested view, add assignees_detail if needed (merge direct + groups)
#                 assignees_detail = assigned_users.copy()  # Start with direct
#                 seen_assignee_ids = {u.get('id') for u in assignees_detail if u.get('id')}
                
#                 # Add group members to assignees_detail
#                 for group in assigned_groups:
#                     try:
#                         group_obj = UsersGroup.objects.get(id=group['id'])
#                         group_members = group_obj.get_users()
#                         for member in group_members:
#                             member_id = member.id
#                             if member_id not in seen_assignee_ids:
#                                 seen_assignee_ids.add(member_id)
#                                 assignees_detail.append({
#                                     "id": member_id,
#                                     "firstname": getattr(member, 'firstname', None) or getattr(member, 'name', None) or getattr(member, 'username', "Unknown"),
#                                     "lastname": getattr(member, 'lastname', "") or "",
#                                     "email": member.email,
#                                     "name": f"{getattr(member, 'firstname', '')} {getattr(member, 'realname', '')}".strip() or getattr(member, 'username', "Unknown") or getattr(member, 'name', "Unknown")
#                                 })
#                     except UsersGroup.DoesNotExist:
#                         pass
                
#                 # Check if current user is in assigned (for assigned view consistency)
#                 current_user_in_assigned = any(
#                     user.get('id') == current_user_id or user.get('email') == current_user_email 
#                     for user in assigned_users
#                 )
#                 if not current_user_in_assigned and ticket.assignee == current_user_id:
#                     current_user_detail = get_user_details(current_user_id)
#                     if current_user_detail:
#                         assigned_users.append(current_user_detail)
                
#                 # Get requested user details
#                 requested_user_detail = None
#                 if ticket.requested:
#                     requested_user_detail = {
#                         "id": ticket.requested.id,
#                         "name": (
#                             getattr(ticket.requested, 'name', None) or 
#                             getattr(ticket.requested, 'firstname', None) or 
#                             ticket.requested.email
#                         ),
#                         "email": ticket.requested.email
#                     }
                
#                 ticket_dict = {
#                     "id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "title": ticket.title,
#                     "description": ticket.description[:100] + "..." if len(ticket.description) > 100 else ticket.description,
#                     "status": ticket.status.field_name if ticket.status else None,
#                     "status_detail": {
#                         "id": ticket.status.id if ticket.status else None,
#                         "field_name": ticket.status.field_name if ticket.status else None,
#                         "field_values": ticket.status.field_values if ticket.status else None
#                     } if ticket.status else None,
#                     "priority": ticket.priority.field_name if ticket.priority else None,
#                     "priority_detail": {
#                         "id": ticket.priority.id if ticket.priority else None,
#                         "field_name": ticket.priority.field_name if ticket.priority else None,
#                         "field_values": ticket.priority.field_values if ticket.priority else None
#                     } if ticket.priority else None,
#                     "category": ticket.category.category_name if ticket.category else None,
#                     "category_detail": {
#                         "id": ticket.category.id if ticket.category else None,
#                         "category_name": ticket.category.category_name if ticket.category else None,
#                     } if ticket.category else None,
#                     "subcategory": ticket.subcategory.subcategory_name if ticket.subcategory else None,
#                     "subcategory_detail": {
#                         "id": ticket.subcategory.id if ticket.subcategory else None,
#                         "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
#                     } if ticket.subcategory else None,
#                     "department": ticket.department.field_name if ticket.department else None,
#                     "department_detail": {
#                         "id": ticket.department.id if ticket.department else None,
#                         "field_name": ticket.department.field_name if ticket.department else None
#                     } if ticket.department else None,
#                     "location": ticket.location.field_name if ticket.location else None,
#                     "location_detail": {
#                         "id": ticket.location.id if ticket.location else None,
#                         "field_name": ticket.location.field_name if ticket.location else None
#                     } if ticket.location else None,
#                     "requested_by": ticket.requested.email if ticket.requested else None,
#                     "requested_detail": requested_user_detail,
#                     "assignees": assigned_users,  # Detailed user info
#                     "assigned_users": assigned_users,  # Alias
#                     "assigned_users_count": len(assigned_users),
#                     "assigned_groups": assigned_groups,
#                     "assigned_groups_count": len(assigned_groups),
#                     "assignees_detail": assignees_detail if is_requested else None,  # For requested view
#                     "created_date": ticket.created_date,
#                     "updated_date": getattr(ticket, 'updated_date', ticket.created_date),
#                     "has_assignments": len(assigned_users) > 0 or len(assigned_groups) > 0,
#                     "type": "requested" if is_requested else "assigned"  # To distinguish in combined list if needed
#                 }
                
#                 # Legacy fields for compatibility
#                 if is_requested:
#                     ticket_dict["assignee"] = ticket.assignee
#                     ticket_dict["assigned_groups_detail"] = []  # Can populate if needed
#                     if ticket.assigned_group:
#                         ticket_dict["assigned_group"] = {
#                             "id": ticket.assigned_group.id,
#                             "name": ticket.assigned_group.name
#                         }
                
#                 tickets_data.append(ticket_dict)
            
#             return {
#                 "count": len(tickets_data),
#                 "tickets": tickets_data
#             }

#         # Statuses list
#         statuses = ['New', 'Solved', 'Closed', 'Cancelled', 'Clarification Required', 'Clarification Applied']

#         # Fetch for requested
#         requested_stats = {}
#         requested_tickets_all = []
#         total_requested = user_requested_qs.distinct().count()
#         for status_name in statuses:
#             data = get_tickets_by_status(user_requested_qs, status_name, is_requested=True)
#             requested_stats[status_name.lower().replace(' ', '_')] = data["count"]
#             requested_tickets_all.extend(data["tickets"])

#         # Fetch for assigned
#         assigned_stats = {}
#         assigned_tickets_all = []
#         total_assigned = assigned_tickets_qs.distinct().count()
#         for status_name in statuses:
#             data = get_tickets_by_status(assigned_tickets_qs, status_name, is_requested=False)
#             assigned_stats[status_name.lower().replace(' ', '_')] = data["count"]
#             assigned_tickets_all.extend(data["tickets"])

#         # Comparison totals
#         comparison_stats = {}
#         for status_name in statuses:
#             key = status_name.lower().replace(' ', '_')
#             comparison_stats[key] = requested_stats.get(key, 0) + assigned_stats.get(key, 0)

#         # Combined tickets (optional: all tickets from both)
#         combined_tickets = requested_tickets_all + assigned_tickets_all

#         # Assignment stats (from assigned only, or combined if needed)
#         all_assigned_tickets = assigned_tickets_all  # Or extend with requested if overlaps
#         total_assigned_users = sum(len(t.get("assigned_users", [])) for t in all_assigned_tickets)
#         total_assigned_groups = sum(len(t.get("assigned_groups", [])) for t in all_assigned_tickets)
#         tickets_with_users = sum(1 for t in all_assigned_tickets if t.get("assigned_users_count", 0) > 0)
#         tickets_with_groups = sum(1 for t in all_assigned_tickets if t.get("assigned_groups_count", 0) > 0)
#         tickets_with_both = sum(1 for t in all_assigned_tickets if t.get("assigned_users_count", 0) > 0 and t.get("assigned_groups_count", 0) > 0)

#         # Prepare response with sections for comparison
#         data = {
#             "success": True,
#             "user_email": user_email,
#             "total_tickets": {
#                 "requested": total_requested,
#                 "assigned": total_assigned,
#                 "combined": total_requested + total_assigned  # Note: may have overlaps if user requests and assigns to self
#             },
#             "requested_stats": requested_stats,
#             "assigned_stats": assigned_stats,
#             "comparison_stats": comparison_stats,
#             "requested_tickets": {  # Nested by status for easy access
#                 "new": get_tickets_by_status(user_requested_qs, 'New', True)["tickets"],
#                 "solved": get_tickets_by_status(user_requested_qs, 'Solved', True)["tickets"],
#                 "closed": get_tickets_by_status(user_requested_qs, 'Closed', True)["tickets"],
#                 "cancelled": get_tickets_by_status(user_requested_qs, 'Cancelled', True)["tickets"],
#                 "clarification_required": get_tickets_by_status(user_requested_qs, 'Clarification Required', True)["tickets"],
#                 "clarification_applied": get_tickets_by_status(user_requested_qs, 'Clarification Applied', True)["tickets"],
#                 "all": requested_tickets_all
#             },
#             "assigned_tickets": {  # Nested by status
#                 "new": get_tickets_by_status(assigned_tickets_qs, 'New', False)["tickets"],
#                 "solved": get_tickets_by_status(assigned_tickets_qs, 'Solved', False)["tickets"],
#                 "closed": get_tickets_by_status(assigned_tickets_qs, 'Closed', False)["tickets"],
#                 "cancelled": get_tickets_by_status(assigned_tickets_qs, 'Cancelled', False)["tickets"],
#                 "clarification_required": get_tickets_by_status(assigned_tickets_qs, 'Clarification Required', False)["tickets"],
#                 "clarification_applied": get_tickets_by_status(assigned_tickets_qs, 'Clarification Applied', False)["tickets"],
#                 "all": assigned_tickets_all
#             },
#             "combined_tickets": combined_tickets,  # Flat list with type flag
#             "assignment_stats": {  # From assigned
#                 "total_assigned_users": total_assigned_users,
#                 "total_assigned_groups": total_assigned_groups,
#                 "tickets_with_users": tickets_with_users,
#                 "tickets_with_groups": tickets_with_groups,
#                 "tickets_with_both": tickets_with_both,
#             },
#             "filters": {
#                 "assignee_user": assignee_user,
#                 "assignee_group": assignee_group,
#                 "entity_id": entity_id,
#                 "search": search if search else None,
#                 "date_range": {
#                     "start_date": start_date_str,
#                     "end_date": end_date_str
#                 } if start_date_str and end_date_str else None
#             }
#         }

#         return Response(data, status=status.HTTP_200_OK)

from datetime import timedelta
from calendar import monthrange
from django.utils import timezone
# Assuming other necessary imports are already present, like:
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from .models import CreateTicket, TicketApprovalLog # Adjust as per your models

# Common helper functions (can be moved to a utils module for better organization)
def serialize_ticket(ticket):
    return {
        "id": ticket.id,
        "ticket_no": ticket.ticket_no,
        "title": ticket.title,
        "description": ticket.description,
        "status_detail": {
            "field_values": ticket.status.field_values if ticket.status else None
        } if hasattr(ticket, 'status') and ticket.status else None,
        "category_detail": {
            "entity_name": ticket.category.entity.name if ticket.category else None
        } if hasattr(ticket, 'category') and ticket.category else None,
        "subcategory_detail": {
            "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
        } if hasattr(ticket, 'subcategory') and ticket.subcategory else None,
        "priority_detail": {
            "field_values": ticket.priority.field_values if ticket.priority else None
        } if hasattr(ticket, 'priority') and ticket.priority else None,
        "department_detail": {
            "field_name": ticket.department.field_name if ticket.department else None
        } if hasattr(ticket, 'department') and ticket.department else None,
        "location_detail": {
            "field_name": ticket.location.field_name if ticket.location else None
        } if hasattr(ticket, 'location') and ticket.location else None,
        "requested_detail": {
            "name": getattr(ticket.requested, 'name', None) or getattr(ticket.requested, 'email', None),
            "email": getattr(ticket.requested, 'email', None)
        } if ticket.requested else None,
        "created_date": ticket.created_date,
        "updated_date": getattr(ticket, 'updated_date', ticket.created_date),  # Fallback to created_date if no updated_date
    }

def get_sla_breached_data(tickets_qs):
    breached_ids = TicketApprovalLog.objects.filter(
        sla_breach=True,
        ticket__in=tickets_qs
    ).values_list('ticket', flat=True).distinct()
    breached_tickets = tickets_qs.filter(id__in=breached_ids)
    return {
        "count": breached_tickets.count(),
        "tickets": [serialize_ticket(t) for t in breached_tickets]
    }

def get_status_data(tickets_qs, status_value):
    status_tickets = tickets_qs.filter(status__field_values__iexact=status_value)
    return {
        "count": status_tickets.count(),
        "tickets": [serialize_ticket(t) for t in status_tickets]
    }

class BaseTicketStatsView(APIView):
    """
    Base class for common logic like date and search filtering.
    Subclasses should define their own get_data method.
    """
    def get_base_qs(self, request):
        now = timezone.now()
        base_qs = CreateTicket.objects.all()
        user_requested_qs = base_qs.filter(requested=request.user)
        user_assigned_qs = base_qs.filter(assignee=str(request.user.id))
        user_combined_qs = (user_requested_qs | user_assigned_qs).distinct()

        # --- Date filter ---
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date = end_date = None
        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                )
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
                ) + timedelta(days=1) - timedelta(seconds=1)
                user_requested_qs = user_requested_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
                user_assigned_qs = user_assigned_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
                base_qs = base_qs.filter(created_date__gte=start_date, created_date__lte=end_date)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)

        # --- Search filter ---
        search = request.query_params.get('search', '').strip()
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            user_requested_qs = user_requested_qs.filter(search_filter)
            user_assigned_qs = user_assigned_qs.filter(search_filter)
            base_qs = base_qs.filter(search_filter)
            user_combined_qs = user_combined_qs.filter(search_filter)

        return {
            'base_qs': base_qs,
            'user_requested_qs': user_requested_qs,
            'user_assigned_qs': user_assigned_qs,
            'user_combined_qs': user_combined_qs,
            'search': search,
            'start_date': start_date,
            'end_date': end_date,
            'now': now,
        }

class UserStatusView(BaseTicketStatsView):
    def get(self, request):
        """Return user-specific ticket statistics"""
        response_data = self.get_base_qs(request)
        if isinstance(response_data, Response):
            return response_data  # Date error case

        user_requested_qs = response_data['user_requested_qs']
        user_assigned_qs = response_data['user_assigned_qs']
        user_combined_qs = response_data['user_combined_qs']

        # --- User stats ---
        user_sla = get_sla_breached_data(user_requested_qs)
        user_pending = get_status_data(user_requested_qs, 'Pending')
        user_approved = get_status_data(user_requested_qs, 'Approved')
        user_rejected = get_status_data(user_requested_qs, 'Rejected')
        user_on_hold = get_status_data(user_requested_qs, 'On Hold')
        user_solved = get_status_data(user_combined_qs, 'Solved')
        user_closed = get_status_data(user_combined_qs, 'Closed')
        user_new_assigned = get_status_data(user_assigned_qs, 'New')

        data = {
            "user_stats": {
                "total_tickets": user_combined_qs.count(),
                "new_assigned": user_new_assigned["count"],
                "new_assigned_tickets": user_new_assigned["tickets"],
                "solved": user_solved["count"],
                "solved_tickets": user_solved["tickets"],
                "closed": user_closed["count"],
                "closed_tickets": user_closed["tickets"],
                "pending": user_pending["count"],
                "pending_tickets": user_pending["tickets"],
                "approved": user_approved["count"],
                "approved_tickets": user_approved["tickets"],
                "rejected": user_rejected["count"],
                "rejected_tickets": user_rejected["tickets"],
                "on_hold": user_on_hold["count"],
                "on_hold_tickets": user_on_hold["tickets"],
                "sla_breached_count": user_sla["count"],
                "sla_breached_tickets": user_sla["tickets"],
            }
        }
        return Response(data, status=status.HTTP_200_OK)

class WatcherStatusView(BaseTicketStatsView):
    def get(self, request):
        """Return watcher-specific ticket statistics"""
        response_data = self.get_base_qs(request)
        if isinstance(response_data, Response):
            return response_data  # Date error case

        base_qs = response_data['base_qs']
        search = response_data['search']
        start_date = response_data['start_date']
        end_date = response_data['end_date']
        now = response_data['now']

        # --- Watcher stats ---
        watcher_ticket_qs = CreateTicket.objects.filter(watchers=request.user).distinct()
        watcher_ticket_qs = watcher_ticket_qs.filter(
            created_date__gte=start_date if start_date else timezone.make_aware(timezone.datetime(2000,1,1)),
            created_date__lte=end_date if end_date else now
        )
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            watcher_ticket_qs = watcher_ticket_qs.filter(search_filter)

        watcher_sla = get_sla_breached_data(watcher_ticket_qs)
        watcher_pending = get_status_data(watcher_ticket_qs, 'Pending')
        watcher_approved = get_status_data(watcher_ticket_qs, 'Approved')
        watcher_rejected = get_status_data(watcher_ticket_qs, 'Rejected')
        watcher_on_hold = get_status_data(watcher_ticket_qs, 'On Hold')

        data = {
            "watcher_stats": {
                "total_tickets": watcher_ticket_qs.count(),
                "pending": watcher_pending["count"],
                "pending_tickets": watcher_pending["tickets"],
                "approved": watcher_approved["count"],
                "approved_tickets": watcher_approved["tickets"],
                "rejected": watcher_rejected["count"],
                "rejected_tickets": watcher_rejected["tickets"],
                "on_hold": watcher_on_hold["count"],
                "on_hold_tickets": watcher_on_hold["tickets"],
                "sla_breached_count": watcher_sla["count"],
                "sla_breached_tickets": watcher_sla["tickets"],
            }
        }
        return Response(data, status=status.HTTP_200_OK)

class OverallStatusView(BaseTicketStatsView):
    def get(self, request):
        """Return overall ticket statistics with month-wise breakdown"""
        response_data = self.get_base_qs(request)
        if isinstance(response_data, Response):
            return response_data  # Date error case

        base_qs = response_data['base_qs']
        now = response_data['now']

        overall_sla = get_sla_breached_data(base_qs)
        overall_pending = get_status_data(base_qs, 'Pending')
        overall_approved = get_status_data(base_qs, 'Approved')
        overall_rejected = get_status_data(base_qs, 'Rejected')
        overall_on_hold = get_status_data(base_qs, 'On Hold')

        # Month-wise stats
        month_stats = []
        for month in range(1, 13):
            first_day = timezone.make_aware(timezone.datetime(now.year, month, 1))
            last_day_num = monthrange(now.year, month)[1]
            last_day_date = timezone.make_aware(timezone.datetime(now.year, month, last_day_num, 23, 59, 59))
            month_qs = base_qs.filter(created_date__gte=first_day, created_date__lte=last_day_date)
            month_sla = get_sla_breached_data(month_qs)
            month_stats.append({
                "month": first_day.strftime("%B"),
                "total_tickets": month_qs.count(),
                "pending": month_qs.filter(status__field_values__iexact='Pending').count(),
                "approved": month_qs.filter(status__field_values__iexact='Approved').count(),
                "rejected": month_qs.filter(status__field_values__iexact='Rejected').count(),
                "on_hold": month_qs.filter(status__field_values__iexact='On Hold').count(),
                "sla_breached_count": month_sla["count"],
                "sla_breached_tickets": month_sla["tickets"],
            })

        today_start = timezone.make_aware(timezone.datetime(now.year, now.month, now.day))
        today_end = today_start + timedelta(days=1) - timedelta(seconds=1)
        month_start = timezone.make_aware(timezone.datetime(now.year, now.month, 1))
        last_day = monthrange(now.year, now.month)[1]
        month_end = timezone.make_aware(timezone.datetime(now.year, now.month, last_day, 23, 59, 59))

        data = {
            "overall_stats": {
                "total_tickets": base_qs.count(),
                "today_tickets": base_qs.filter(created_date__gte=today_start, created_date__lte=today_end).count(),
                "month_tickets": base_qs.filter(created_date__gte=month_start, created_date__lte=month_end).count(),
                "pending": overall_pending["count"],
                "pending_tickets": overall_pending["tickets"],
                "approved": overall_approved["count"],
                "approved_tickets": overall_approved["tickets"],
                "rejected": overall_rejected["count"],
                "rejected_tickets": overall_rejected["tickets"],
                "on_hold": overall_on_hold["count"],
                "on_hold_tickets": overall_on_hold["tickets"],
                "sla_breached_count": overall_sla["count"],
                "sla_breached_tickets": overall_sla["tickets"],
                "month_wise": month_stats
            }
        }
        return Response(data, status=status.HTTP_200_OK)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Q
# from django.utils import timezone
# from datetime import timedelta
# from .models import CreateTicket  # Assuming your model import

# def is_privileged(user):
#     """Helper function to check if user is privileged (e.g., superuser or staff)"""
#     return user.is_authenticated and (user.is_superuser or user.is_staff)

# class TicketView(APIView):
#     def get(self, request):
#         """Return ticket statistics including user-based, watcher-based, and overall if privileged."""

#         start_date_str = request.query_params.get('start_date')
#         end_date_str = request.query_params.get('end_date')
#         search = request.query_params.get('search', '').strip()

#         base_qs = CreateTicket.objects.all()
#         user_requested_qs = base_qs.filter(requested=request.user)
#         user_assigned_qs = base_qs.filter(assignee=str(request.user.id))  # Assignee is CharField

#         # --- Date filter ---
#         start_date = end_date = None
#         if start_date_str and end_date_str:
#             try:
#                 start_date = timezone.make_aware(
#                     timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
#                 )
#                 end_date = timezone.make_aware(
#                     timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
#                 ) + timedelta(days=1) - timedelta(seconds=1)

#                 user_requested_qs = user_requested_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#                 user_assigned_qs = user_assigned_qs.filter(
#                     created_date__gte=start_date, created_date__lte=end_date
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
#                                 status=status.HTTP_400_BAD_REQUEST)

#         # --- Search filter ---
#         if search:
#             search_filter = Q(title__icontains=search) | Q(description__icontains=search)
#             user_requested_qs = user_requested_qs.filter(search_filter)
#             user_assigned_qs = user_assigned_qs.filter(search_filter)

#         user_combined_qs = (user_requested_qs | user_assigned_qs).distinct()

#         # --- SLA breached helper ---
#         def count_sla_breached(tickets_qs):
#             return TicketApprovalLog.objects.filter(
#                 sla_breach=True,
#                 ticket__in=tickets_qs
#             ).values('ticket').distinct().count()

#         # --- User stats ---
#         data = {
#             "user_stats": {
#                 "total_tickets": user_combined_qs.count(),
#                 "new_assigned": user_assigned_qs.filter(status__field_values__iexact='New').count(),
#                 "solved": user_combined_qs.filter(status__field_values__iexact='Solved').count(),
#                 "closed": user_combined_qs.filter(status__field_values__iexact='Closed').count(),
#                 "pending": user_requested_qs.filter(status__field_values__iexact='Pending').count(),
#                 "approved": user_requested_qs.filter(status__field_values__iexact='Approved').count(),
#                 "rejected": user_requested_qs.filter(status__field_values__iexact='Rejected').count(),
#                 "on_hold": user_requested_qs.filter(status__field_values__iexact='On Hold').count(),
#                 "sla_breached": count_sla_breached(user_requested_qs),
#             }
#         }

#         # --- Watcher stats ---
#         watcher_ticket_qs = CreateTicket.objects.filter(watchers=request.user).distinct()

#         if start_date and end_date:
#             watcher_ticket_qs = watcher_ticket_qs.filter(
#                 created_date__gte=start_date, created_date__lte=end_date
#             )
#         if search:
#             watcher_ticket_qs = watcher_ticket_qs.filter(search_filter)

#         data["watcher_stats"] = {
#             "pending": watcher_ticket_qs.filter(status__field_values__iexact='Pending').count(),
#             "approved": watcher_ticket_qs.filter(status__field_values__iexact='Approved').count(),
#             "rejected": watcher_ticket_qs.filter(status__field_values__iexact='Rejected').count(),
#             "on_hold": watcher_ticket_qs.filter(status__field_values__iexact='On Hold').count(),
#             "sla_breached": count_sla_breached(watcher_ticket_qs),
#         }

#         # --- Overall stats if privileged ---
#         if is_privileged(request.user):
#             all_qs = base_qs
#             if start_date and end_date:
#                 all_qs = all_qs.filter(created_date__gte=start_date, created_date__lte=end_date)
#             if search:
#                 all_qs = all_qs.filter(search_filter)

#             data["overall_stats"] = {
#                 "total_tickets": all_qs.count(),
#                 "new_assigned": all_qs.filter(status__field_values__iexact='New').count(),
#                 "solved": all_qs.filter(status__field_values__iexact='Solved').count(),
#                 "closed": all_qs.filter(status__field_values__iexact='Closed').count(),
#                 "pending": all_qs.filter(status__field_values__iexact='Pending').count(),
#                 "approved": all_qs.filter(status__field_values__iexact='Approved').count(),
#                 "rejected": all_qs.filter(status__field_values__iexact='Rejected').count(),
#                 "on_hold": all_qs.filter(status__field_values__iexact='On Hold').count(),
#                 "sla_breached": count_sla_breached(all_qs),
#             }

#         return Response(data, status=status.HTTP_200_OK)
    
# class CreateTicketView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     def get(self, request, pk=None):
#         """Retrieve ticket or list of tickets"""
#         if pk:
#             ticket = get_object_or_404(
#                 CreateTicket.objects.select_related(
#                     "type", "department", "location", "priority", "status"
#                 ),
#                 id=pk,
#             )

#             if not is_privileged(request.user) and ticket.requested != request.user:
#                 return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#             data = CreateTicketSerializer(ticket, context={"request": request}).data
#             return Response(data, status=status.HTTP_200_OK)

#         qs = CreateTicket.objects.select_related(
#             "type", "department", "location", "priority", "status"
#         )
#         if not is_privileged(request.user):
#             qs = qs.filter(requested=request.user)

#         data = CreateTicketSerializer(qs, many=True, context={"request": request}).data
#         return Response(data, status=status.HTTP_200_OK)

    
#     def post(self, request):
#         """Create new ticket, set approvers, send mail, and start SLA"""
#         try:
#             with transaction.atomic():
#                 serializer = CreateTicketSerializer(data=request.data, context={"request": request})
#                 serializer.is_valid(raise_exception=True)
#                 # ticket = serializer.save(requested=request.user)
#                 ticket = serializer.save()
#                 logger.info(f"🎫 Ticket #{ticket.ticket_no} created by {request.user}")
#                 # --- SET CATEGORY & SUBCATEGORY (THEY ARE NOT SET BY SERIALIZER) ---
#                 try:
#                     category_id = request.data.get("category_id")
#                     if category_id:
#                         ticket.category = TicketCategory.objects.get(id=category_id)
#                         logger.info(f"Category set: {ticket.category.category_name}")
#                     subcategory_id = request.data.get("subcategory_id")
#                     if subcategory_id:
#                         ticket.subcategory = TicketSubcategory.objects.get(id=subcategory_id)
#                         logger.info(f"Subcategory set: {ticket.subcategory.subcategory_name}")
#                     ticket.save()  # ← THIS IS CRITICAL! Save again after setting FK
#                 except Exception as e:
#                     logger.error(f"Error setting category/subcategory: {e}")
#                     # Optional: return error if needed
#                 # --- Save Attachments ---
#                 for f in request.FILES.getlist("documents"):
#                     TicketDocument.objects.create(ticket=ticket, file=f)

#                 # --- Fetch SLA ---
#                 # sla = TicketSLA.objects.filter(
#                 #     category_id=request.data.get("category_id"),
#                 #     subcategory_id=request.data.get("subcategory_id"),
#                 #     is_active="Y",
#                 # ).first()
#                 sla = TicketSLA.objects.filter(
#                     category=ticket.category,
#                     subcategory=ticket.subcategory,
#                     is_active="Y",
#                 ).first()
#                 if not sla:
#                     return Response({"error": "No SLA found for this category/subcategory"}, status=400)

#                 ticket.sla = sla
#                 ticket.save()

#                 # --- Collect Approvers (using USER foreign keys) ---
#                 approver_ids = [
#                     getattr(sla, "Approver_level1_user_id"),
#                     getattr(sla, "Approver_level2_user_id"),
#                     getattr(sla, "Approver_level3_user_id"),
#                     getattr(sla, "Approver_level4_user_id"),
#                     getattr(sla, "Approver_level5_user_id"),
#                 ]
#                 approvers = list(User.objects.filter(id__in=[a for a in approver_ids if a]))

#                 if not approvers:
#                     return Response({"error": "No valid approvers found in SLA"}, status=400)

#                 ticket.total_approval_levels = len(approvers)
#                 ticket.save()

#                 # --- Create Approval Logs ---
#                 for i, approver in enumerate(approvers):
#                     TicketApprovalLog.objects.create(
#                     ticket=ticket,
#                     sla=sla,
#                     current_level=i + 1,
#                     is_current_level=(i == 0),
#                     status="Pending" if i == 0 else "Waiting",
#                     approval_status="Pending",
#                     # created_by=approver,  
#                     created_by_id=approver.id,# ✅ assign the User instance
#                     created_on=timezone.now(),
#                 )
#                 first_log = TicketApprovalLog.objects.filter(
#                     ticket=ticket, current_level=1
#                 ).first()
#                 if first_log and getattr(sla, "Approver_level1_time", None):
#                     hours = parse_sla_time_to_hours(sla.Approver_level1_time)
#                     deadline = add_sla_time_skipping_holidays(ticket.created_date, hours)
#                     first_log.sla_end_time = deadline
#                     first_log.save()
#                     logger.info(f"Level 1 SLA end time set to: {deadline}")
#                 # --- Watchers ---
#                 watcher_ids = request.data.getlist("watchers") or []
#                 watchers = []
#                 if watcher_ids:
#                     watchers = list(User.objects.filter(id__in=watcher_ids))
#                     ticket.watchers.set(watchers)
#                     logger.info(f"👀 Watchers added: {[w.email for w in watchers if w.email]}")

#                 # --- Email Template ---
#                 ticket_created_template = TicketEmailTemplate.objects.filter(
#                 email_event="Ticket_Created",
#                 is_active="Y"
#             ).first()

#             # --- 2️⃣ Load Approval template for approver ---
#             approval_template = TicketEmailTemplate.objects.filter(
#                 email_event="Approval",
#                 is_active="Y"
#             ).first()

#             # --- Requester Email ---
#             requester_email = getattr(request.user, "email", None)
#             requester_name = (
#                 (getattr(request.user, 'firstname', '') or '') + " " +
#                 (getattr(request.user, 'realname', '') or '')
#             ).strip() or "Requester"

#             if requester_email and ticket_created_template:
#                 template = Template(ticket_created_template.email_template)

#                 ticket_context = {
#                     "firstname": requester_name,
#                     "realname": "",
#                     "ticket_no": ticket.ticket_no,
#                     "name": ticket.title or ticket.description,
#                     "date_creation": timezone.localtime(ticket.created_date),
#                     "ticket_url": f"http://yourdomain.com/tickets/{ticket.id}",
#                     "mail_signature": "IT Support Team",
#                 }

#                 html_content = template.render(Context({"ticket": ticket_context}))
#                 cc_emails = [u.email for u in watchers if u.email]

#                 send_email_task.delay(
#                     [requester_email],
#                     f"Ticket #{ticket.ticket_no} Created Successfully",
#                     html_content,
#                     cc=cc_emails
#                 )
#                 logger.info(f"📧 Ticket Created email sent to requester {requester_email}")

#             # --- 3️⃣ First Approver Email ---
#             first_approver = approvers[0]
#             first_approver_email = getattr(first_approver, "email", None)

#             if first_approver_email and approval_template:
#                 template = Template(approval_template.email_template)

#                 approver_context = {
#                 "firstname": requester_name,
#                 "realname": " ",
#                 "date_creation": timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#                 "name": ticket.description or ticket.title or "No description provided",
#                 "ticket_url": f"http://yourdomain.com/tickets/{ticket.id}",
#                 "mail_signature": "IT Support Team",
#                 "year": timezone.now().year,
#             }

#                 html_content = template.render(Context(approver_context))

#                 cc_emails = [u.email for u in watchers if u.email]

#                 send_email_task.delay(
#                     [first_approver_email],
#                     f"Approval Request - Ticket #{ticket.ticket_no}",
#                     html_content,
#                     cc=cc_emails
#                 )

#                 logger.info(f"📧 Approval email sent to Level 1 Approver: {first_approver_email}")
#                 # --- 3️⃣ Schedule SLA Escalation for First Approver ---
#                 first_sla_text = getattr(sla, "Approver_level1_time", None)
#                 first_approver_user = getattr(sla, "Approver_level1_user", None)

#                 if first_sla_text and first_approver_user:
#                     hours = parse_sla_time_to_hours(first_sla_text)
#                     start_time = ticket.created_date
#                     adjusted_end = add_sla_time_skipping_holidays(start_time, hours)
#                     handle_sla_escalation.apply_async(
#                         args=[ticket.id, 1],
#                         eta=adjusted_end  # ← EXACT TIME, NO DELAY
#                     )
#                     logger.info(f"SLA scheduled for {adjusted_end} (exact time)")
#                     # logger.info(
#                     #     f"⏱ SLA escalation scheduled for Ticket #{ticket.ticket_no} "
#                     #     f"(Level 1) after {hours} hours (~{delay_seconds/3600:.2f} hrs, skipping holidays)."
#                     # )
#                 else:
#                     logger.warning(f"⚠️ No SLA time or approver found for Level 1 of Ticket #{ticket.ticket_no}")

#                 # --- ✅ Return Success ---
#                 ticket_data = CreateTicketSerializer(ticket, context={"request": request}).data
#                 return Response({
#                     "success": True,
#                     "ticket_id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "ticket": ticket_data,
#                     "approvers": [a.email for a in approvers if a.email],
#                     "message": (
#                         f"Ticket created successfully. "
#                         f"SLA monitoring started for approver {first_approver_email}."
#                     ),
#                 }, status=status.HTTP_201_CREATED)
            
        

#         except Exception as e:
#             logger.exception("❌ Error creating ticket")
#             return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#     def put(self, request, pk):
#         """Update existing ticket"""
#         try:
#             with transaction.atomic():
#                 ticket = get_object_or_404(
#                     CreateTicket.objects.select_related(
#                         "type", "department", "location", "priority", "status"
#                     ),
#                     id=pk,
#                 )

#                 if not is_privileged(request.user) and ticket.requested != request.user:
#                     return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

#                 serializer = CreateTicketSerializer(
#                     ticket, data=request.data, partial=True, context={"request": request}
#                 )
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save()
#                 logger.info(f"🎫 Ticket #{ticket.ticket_no} updated by {request.user}")

#                 # --- SET CATEGORY & SUBCATEGORY (IF PROVIDED IN UPDATE) ---
#                 try:
#                     category_id = request.data.get("category_id")
#                     if category_id:
#                         ticket.category = TicketCategory.objects.get(id=category_id)
#                         logger.info(f"Category updated: {ticket.category.category_name}")

#                     subcategory_id = request.data.get("subcategory_id")
#                     if subcategory_id:
#                         ticket.subcategory = TicketSubcategory.objects.get(id=subcategory_id)
#                         logger.info(f"Subcategory updated: {ticket.subcategory.subcategory_name}")

#                     ticket.save()  # Save again after setting FK
#                 except Exception as e:
#                     logger.error(f"Error updating category/subcategory: {e}")
#                     # Optional: return error if needed

#                 # --- Add New Attachments (existing ones remain unchanged) ---
#                 for f in request.FILES.getlist("documents"):
#                     TicketDocument.objects.create(ticket=ticket, file=f)

#                 # --- Update Watchers (if provided) ---
#                 watcher_ids = request.data.getlist("watchers") or []
#                 if watcher_ids:
#                     watchers = list(User.objects.filter(id__in=watcher_ids))
#                     ticket.watchers.set(watchers)
#                     logger.info(f"👀 Watchers updated: {[w.email for w in watchers if w.email]}")

#                 # Note: SLA, approvers, and approval logs are not updated here to avoid disrupting ongoing processes.
#                 # If category/subcategory changes affect SLA, consider manual re-triggering or a separate endpoint.

#                 # --- Return Updated Data ---
#                 data = CreateTicketSerializer(ticket, context={"request": request}).data
#                 return Response({
#                     "success": True,
#                     "ticket_id": ticket.id,
#                     "ticket_no": ticket.ticket_no,
#                     "ticket": data,
#                     "message": f"Ticket #{ticket.ticket_no} updated successfully.",
#                 }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.exception("❌ Error updating ticket")
#             return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     # def post(self, request):
#     #         """Create new ticket with watchers, approvers, and SLA flow"""
#     #         try:
#     #             with transaction.atomic():
#     #                 print("🔍 Incoming data:", request.data)
#     #                 print("🔍 Incoming FILES:", request.FILES)

#     #                 # ✅ Extract watchers (list of user IDs)
#     #                 watcher_ids = request.data.getlist('watchers') or []  # ensure plural matches frontend
#     #                 print("✅ Watcher IDs received:", watcher_ids)

#     #                 serializer = CreateTicketSerializer(data=request.data, context={"request": request})
#     #                 serializer.is_valid(raise_exception=True)

#     #                 # ✅ Save ticket
#     #                 ticket = serializer.save(requested=request.user)
#     #                 print(f"🎫 Ticket #{ticket.ticket_no} created by {request.user}")

#     #                 # ✅ Save uploaded files
#     #                 for file_obj in request.FILES.getlist("documents"):
#     #                     TicketDocument.objects.create(ticket=ticket, file=file_obj)

#     #                 # ✅ Assign SLA
#     #                 sla = TicketSLA.objects.filter(
#     #                     category_id=ticket.category_id,
#     #                     subcategory_id=getattr(ticket, 'subcategory_id', None),
#     #                     is_active='Y'
#     #                 ).first()
#     #                 if not sla:
#     #                     return Response({"Error": "No SLA found for this ticket"}, status=400)

#     #                 ticket.sla = sla
#     #                 ticket.save()

#     #                 # ✅ Approvers list
#     #                 approvers = [
#     #                     sla.Approver_level1_user,
#     #                     sla.Approver_level2_user,
#     #                     sla.Approver_level3_user,
#     #                     sla.Approver_level4_user,
#     #                     sla.Approver_level5_user,
#     #                 ]
#     #                 approvers = [a for a in approvers if a]
#     #                 if not approvers:
#     #                     return Response({"Error": "No approvers defined in SLA"}, status=400)

#     #                 ticket.total_approval_levels = len(approvers)
#     #                 ticket.save()

#     #                 # ✅ Approval logs
#     #                 for i, approver in enumerate(approvers):
#     #                     TicketApprovalLog.objects.create(
#     #                         ticket=ticket,
#     #                         sla=sla,
#     #                         current_level=i + 1,
#     #                         is_current_level=(i == 0),
#     #                         status="Pending" if i == 0 else "Waiting",
#     #                         created_by=approver,
#     #                         created_on=timezone.now(),
#     #                         approval_status="Pending",
#     #                     )

#     #                 # ✅ Add watchers (for CC)
#     #                 watchers = []
#     #                 if watcher_ids:
#     #                     watchers = list(User.objects.filter(id__in=watcher_ids))
#     #                     ticket.watchers.set(watchers)
#     #                     print(f"✅ Watchers set for ticket #{ticket.ticket_no}: {[u.email for u in watchers if u.email]}")

#     #                 # ✅ Email setup
#     #                 email_template_obj = TicketEmailTemplate.objects.filter(
#     #                     email_event='Approval', is_active='Y'
#     #                 ).first()
#     #                 creator_user = request.user
#     #                 creator_email = getattr(creator_user, 'email', None)

#     #                 # ✅ Send ticket creation email to requester (with watchers as CC)
#     #                 if email_template_obj and creator_email:
#     #                     current_site = request.build_absolute_uri(f'/api/tickets/tickets/{ticket.id}/')
#     #                     template = Template(email_template_obj.email_template)
#     #                     context = Context({
#     #                         'firstname': getattr(creator_user, 'firstname', '-') or '',
#     #                         'realname': getattr(creator_user, 'realname', '-') or '',
#     #                         'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#     #                         'name': ticket.title or ticket.description,
#     #                         'ticket_url': current_site,
#     #                         'mail_signature': 'IT Support Team',
#     #                         'year': timezone.now().year,
#     #                     })
#     #                     html_content = template.render(context)

#     #                     cc_emails = [u.email for u in watchers if u.email]
#     #                     send_email_task.delay(
#     #                         [creator_email],  # To requester
#     #                         f"Ticket #{ticket.ticket_no} Created Successfully",
#     #                         html_content,
#     #                         cc=cc_emails  # ✅ CC watchers
#     #                     )

#     #                 # ✅ Notify first approver (also CC watchers)
#     #                 first_approver = approvers[0]
#     #                 first_approver_email = first_approver if isinstance(first_approver, str) else getattr(first_approver, 'email', None)
#     #                 if email_template_obj and first_approver_email:
#     #                     template = Template(email_template_obj.email_template)
#     #                     context = Context({
#     #                 'requester': ticket.requested_detail.get('name') if hasattr(ticket, 'requested_detail') else str(ticket.requested),
#     #                 'ticket_no': ticket.ticket_no,
#     #                 'title': ticket.title,
#     #                 'description': ticket.description or "-",
#     #                 'ticket_url': f"http://yourdomain.com/tickets/{ticket.id}",
#     #                 'created_date': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#     #                 'requested_date': timezone.localtime(ticket.requested_date).strftime("%d %B %Y, %I:%M %p") if hasattr(ticket, 'requested_date') else "",
#     #                 'year': timezone.now().year,
#     #             })

#     #                     html_content = template.render(context)

#     #                     cc_emails = [u.email for u in watchers if u.email]
#     #                     send_email_task.delay(
#     #                         [first_approver_email],
#     #                         f"New Ticket #{ticket.ticket_no} Requires Your Approval",
#     #                         html_content,
#     #                         cc=cc_emails  # ✅ CC watchers again
#     #                     )

#     #                 # ✅ SLA escalation scheduling
#     #                 first_time_text = getattr(sla, "Approver_level1_time", "1")
#     #                 hours = parse_sla_time_to_hours(first_time_text)
#     #                 handle_sla_escalation.apply_async(
#     #                     args=[ticket.id, 1],
#     #                     countdown=int(hours * 3600)
#     #                 )

#     #                 ticket_data = CreateTicketSerializer(ticket, context={"request": request}).data

#     #             return Response({
#     #                 "success": True,
#     #                  "ticket_id": ticket.id,
#     #                  "ticket_no": ticket.ticket_no,
#     #                 "ticket": ticket_data,
#     #                 "approvers": [str(a) for a in approvers],
#     #                 "message": f"Ticket created successfully. SLA monitoring started for approver {first_approver}.",
#     #             }, status=status.HTTP_201_CREATED)

#     #         except Exception as e:
#     #             print("❌ Error creating ticket:", e)
#     #             return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     # def post(self, request, ticket_no=None):
#     #     print("🔍 Incoming data:", request.data)
#     #     print("🔍 Incoming FILES:", request.FILES)
#     #     try:
#     #         serializer = CreateTicketSerializer(data=request.data, context={"request": request})
#     #         serializer.is_valid(raise_exception=True)

#     #         # Save ticket with requester as logged-in user
#     #         ticket = serializer.save(requested=request.user)
#     #         data = CreateTicketSerializer(ticket, context={"request": request}).data
#     #         ticket = serializer.save(requested=request.user)

#     #         # ✅ Handle uploaded files (support multiple)
#     #         uploaded_files = request.FILES.getlist("documents")
#     #         print("📂 Uploaded files:", uploaded_files)

#     #         for f in uploaded_files:
#     #             TicketDocument.objects.create(ticket=ticket, file=f)

#     #         current_site = request.build_absolute_uri(f'api/tickets/tickets/{ticket.id}/')
#     #         # -------- Ticket Created Email --------
#     #         creator_user = request.user
#     #         creator_email = getattr(creator_user, 'email', None)
#     #         email_template_obj = TicketEmailTemplate.objects.filter(
#     #             email_event='Approval',
#     #             is_active='Y'
#     #         ).first()

#     #         if email_template_obj and creator_email:
#     #             template = Template(email_template_obj.email_template)
#     #             context = Context({
#     #                 'firstname': getattr(creator_user, 'firstname', '-') or '',
#     #                 'realname': getattr(creator_user, 'realname', '-') or '',
#     #                 'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#     #                 'name': ticket.title or ticket.description,
#     #                 'ticket_url': current_site,
#     #                 # 'ticket_url': f"http://tickets/tickets/{ticket.id}",
#     #                 'mail_signature': 'IT Support Team',
#     #                 'year': timezone.now().year,
#     #             })
#     #             html_content = template.render(context)
#     #             send_email_task.delay(
#     #                 [creator_email],
#     #                 f"Ticket #{ticket.ticket_no} Created Successfully",
#     #                 html_content
#     #             )

#     #         # -------- Handle Approvers & Approval Request Email --------
#     #         sla = TicketSLA.objects.filter(
#     #             category_id=ticket.category_id,
#     #             subcategory_id=getattr(ticket, 'subcategory_id', None),
#     #             is_active='Y'
#     #         ).first()

#     #         if sla:
#     #             approvers = [
#     #                 sla.Approver_level1_user,
#     #                 sla.Approver_level2_user,
#     #                 sla.Approver_level3_user,
#     #                 sla.Approver_level4_user,
#     #                 sla.Approver_level5_user
#     #             ]
#     #             approvers = [a for a in approvers if a]  # Remove empty
#     #             ticket.total_approval_levels = len(approvers)
#     #             ticket.save()

#     #             if approvers:
#     #                 email_template_obj = TicketEmailTemplate.objects.filter(
#     #                     email_event='Approval',
#     #                     is_active='Y'
#     #                 ).first()
#     #                 if email_template_obj:
#     #                     template = Template(email_template_obj.email_template)
#     #                     context = Context({
#     #                         'requester': f"{getattr(creator_user, 'firstname', '-') or ''} {getattr(creator_user, 'realname', '-') or ''}",
#     #                         'ticket_no': ticket.ticket_no,
#     #                         'title': ticket.title,
#     #                         'description': ticket.description,
#     #                         'ticket_url': f"http://yourdomain.com/tickets/{ticket.id}",
#     #                         'created_date': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
#     #                         'year': timezone.now().year,
#     #                     })
#     #                     html_content = template.render(context)

#     #                     # # Send email to first approver
#     #                     # send_email_task.delay(
#     #                     #     [approvers[0]],
#     #                     #     f"New Ticket #{ticket.ticket_no} Requires Your Approval",
#     #                     #     html_content
#     #                     # )

#     #         return Response(data, status=status.HTTP_201_CREATED)

#     #     except Exception as e:
#     #         return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# class CreateTicketView(APIView):
#     # ... existing post (uses serializer for creation) ...
#     def post(self, request):
#         """Create new ticket with helpdesk assignment"""
#         serializer = CreateTicketSerializer(data=request.data, context={"request": request})
#         serializer.is_valid(raise_exception=True)
#         ticket = serializer.save()
    
#         # Attachments
#         for f in request.FILES.getlist("documents"):
#             TicketDocument.objects.create(ticket=ticket, file=f)
    
#         ticket_data = CreateTicketSerializer(ticket, context={"request": request}).data
#         return Response({
#             "success": True,
#             "ticket_id": ticket.id,
#             "ticket_no": ticket.ticket_no,
#             "ticket": ticket_data,
#             "assigned_to": {
#                 "type": "user" if not ticket.assignee or not ticket.assignee.startswith('group:') else "group",
#                 "detail": serializer.get_assignee_detail(ticket) or serializer.get_assigned_group_detail(ticket)
#             },
#             "message": "Ticket created successfully."
#         }, status=status.HTTP_201_CREATED)
    
#     def get(self, request, pk=None):
#         """List/View tickets as 'approver dashboard'—filter by assignment/group"""
#         if pk:
#             ticket = get_object_or_404(
#                 CreateTicket.objects.select_related("type", "department", "location", "priority", "status"),
#                 ticket_no=pk
#             )
#             if not self._can_view_ticket(ticket, request.user):
#                 return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
#             data = CreateTicketSerializer(ticket, context={"request": request}).data
#             return Response(data, status=status.HTTP_200_OK)
 
#         # Dashboard list: All visible tickets (pending or assigned)
#         qs = CreateTicket.objects.select_related(
#             "type", "department", "location", "priority", "status"
#         ).order_by('-created_date')  # Recent first for dashboard
 
#         if not is_privileged(request.user):
#             # Own tickets
#             own = qs.filter(requested=request.user)
#             # Direct user assignee (email match)
#             direct = qs.filter(assignee=request.user.email)
#             # Group: All members via watchers
#             group = qs.filter(watchers=request.user)
#             qs = own | direct | group
 
#         data = CreateTicketSerializer(qs, many=True, context={"request": request}).data
#         return Response({
#             "dashboard_tickets": data,
#             "total_visible": len(data),
#             "message": f"Showing {len(data)} tickets you can view (including group assignments)."
#         }, status=status.HTTP_200_OK)
 
#     def _can_view_ticket(self, ticket, user):
#         if is_privileged(user):
#             return True
#         if ticket.requested == user:
#             return True  # Requester sees own
#         assignee_str = getattr(ticket, 'assignee', '')
#         # Direct user
#         if assignee_str == user.email:
#             return True
#         # Group: Check watchers (all members added)
#         if user in ticket.watchers.all():
#             return True
#         return False
def is_privileged(user):
    # Implement your logic, e.g., return user.is_superuser or user.groups.filter(name='Admin').exists()
    return user.is_superuser  # Placeholder

class CreateTicketView(APIView):
    # ... existing post (uses serializer for creation) ...
    def post(self, request):
        """Create new ticket with helpdesk assignment"""
        logger.info(f"Request data: {request.data}")  # Improved logging
        serializer = CreateTicketSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ticket = serializer.save()  # ← Ticket is saved here

        # === ADD THESE 3 LINES HERE ===
        from Ticket.tasks import send_ticket_created_notification
        send_ticket_created_notification.delay(ticket.id)
        logger.info(f"Notification task queued for new ticket {ticket.ticket_no} (ID: {ticket.id})")
        # ===============================

        # Attachments
        for f in request.FILES.getlist("documents"):
            TicketDocument.objects.create(ticket=ticket, file=f)

        ticket_data = CreateTicketSerializer(ticket, context={"request": request}).data
       
        # Updated assigned_to for multiple
        users_detail = serializer.get_assignees_detail(ticket)
        groups_detail = serializer.get_assigned_groups_detail(ticket)
        assigned_to_type = "mixed" if users_detail and groups_detail else ("user" if users_detail else "group" if groups_detail else None)
        assigned_to_detail = {
            "users": users_detail,
            "groups": groups_detail
        }
       
        logger.info(f"Created ticket {ticket.id} with type: {assigned_to_type}, detail: {assigned_to_detail}")
       
        return Response({
            "success": True,
            "ticket_id": ticket.id,
            "ticket_no": ticket.ticket_no,
            "ticket": ticket_data,
            "assigned_to": {
                "type": assigned_to_type,
                "detail": assigned_to_detail
            },
            "message": "Ticket created successfully."
        }, status=status.HTTP_201_CREATED)
   
    def put(self, request, pk=None):
        """Update ticket - supports partial updates"""
        if not pk:
            return Response({"error": "Ticket ID (pk) is required"}, status=status.HTTP_400_BAD_REQUEST)
       
        # Robust lookup: Try ticket_no first (str), then id (int) - prioritizes ticket_no for URL-based access
        ticket = None
        try:
            # First, try as ticket_no (always str)
            ticket = CreateTicket.objects.get(ticket_no=pk)
        except CreateTicket.DoesNotExist:
            pass
       
        if not ticket:
            try:
                # Fallback to id (int)
                ticket_id = int(pk)
                ticket = CreateTicket.objects.get(id=ticket_id)
            except (ValueError, CreateTicket.DoesNotExist):
                return Response({"error": f"Ticket not found with ID '{pk}' or ticket_no '{pk}'"}, status=status.HTTP_404_NOT_FOUND)
       
        if not self._can_view_ticket(ticket, request.user):
            return Response({"detail": "Not permitted."}, status=status.HTTP_403_FORBIDDEN)
       
        # NEW: Log old status for change tracking
        old_status = ticket.status
        logger.info(f"Update request data for ticket {pk} (resolved to {ticket.id}): {request.data}")
       
        serializer = CreateTicketSerializer(
            instance=ticket,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if not serializer.is_valid():
            logger.error(f"Update validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
        updated_ticket = serializer.save()
       
        # NEW: Log status change if it occurred
        if old_status != updated_ticket.status:
            logger.info(f"Status changed for ticket {updated_ticket.id}: {old_status.field_name} -> {updated_ticket.status.field_name}")
            # TODO: Trigger notifications or workflows here if needed
       
        # Attachments for update (if provided)
        for f in request.FILES.getlist("documents"):
            TicketDocument.objects.create(ticket=updated_ticket, file=f)
       
        ticket_data = CreateTicketSerializer(updated_ticket, context={"request": request}).data
       
        return Response({
            "success": True,
            "ticket_id": updated_ticket.id,
            "ticket_no": updated_ticket.ticket_no,
            "ticket": ticket_data,
            "message": "Ticket updated successfully."
        }, status=status.HTTP_200_OK)
    def get(self, request, pk=None):
        """List/View tickets as 'approver dashboard'—filter by assignment/group"""
        if pk:
            ticket = get_object_or_404(
                CreateTicket.objects.select_related("type", "department", "location", "platform", "priority", "status"),
                ticket_no=pk
            )
            if not self._can_view_ticket(ticket, request.user):
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            data = CreateTicketSerializer(ticket, context={"request": request}).data
            return Response(data, status=status.HTTP_200_OK)
 
        # Dashboard list: All visible tickets (pending or assigned)
        qs = CreateTicket.objects.select_related(
            "type", "department", "location", "platform", "priority", "status"
        ).order_by('-created_date')  # Recent first for dashboard
 
        if not is_privileged(request.user):
            # Own tickets
            own = qs.filter(requested=request.user)
            # Direct user assignee (email match) - for legacy, but update for new if needed
            direct = qs.filter(assignee=request.user.email)
            # Group: All members via watchers
            group = qs.filter(watchers=request.user)
            qs = own | direct | group
 
        data = CreateTicketSerializer(qs, many=True, context={"request": request}).data
        return Response({
            "dashboard_tickets": data,
            "total_visible": len(data),
            "message": f"Showing {len(data)} tickets you can view (including group assignments)."
        }, status=status.HTTP_200_OK)
 
    def _can_view_ticket(self, ticket, user):
        if is_privileged(user):
            return True
        if ticket.requested == user:
            return True  # Requester sees own
        assignee_str = getattr(ticket, 'assignee', '')
        # Direct user
        if assignee_str == user.email:
            return True
        # Check if user email in assigned_users JSON
        if ticket.assigned_users and user.email in ticket.assigned_users:
            return True
        # Group: Check watchers (all members added)
        if user in ticket.watchers.all():
            return True
        return False



class DeleteTicketDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            document = TicketDocument.objects.get(id=pk, ticket__requested=request.user)  # Optional: restrict to requester
            # Or just: document = get_object_or_404(TicketDocument, id=pk)
            document.file.delete()  # Delete from storage
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TicketDocument.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class TicketSLAByIdView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, sla_id):
        try:
            # ticket_sla = TicketSLA.objects.get(id=sla_id)

            # serializer = TicketSLASerializer(ticket_sla)
            ticket_sla = TicketSLA.objects.filter(id=sla_id).values().annotate(Approver_level1_user=F('Approver_level1_user_id__name'),Approver_level2_user=F('Approver_level2_user_id__name'),
            Approver_level3_user=F('Approver_level3_user_id__name'),
            Approver_level4_user=F('Approver_level4_user_id__name'),
            Approver_level5_user=F('Approver_level5_user_id__name'),
            )
            return Response(ticket_sla, status=status.HTTP_200_OK)
        except TicketSLA.DoesNotExist:
            return Response({"detail": "SLA not found."}, status=status.HTTP_404_NOT_FOUND)


class TicketSLAHomeScreenView(APIView):
    permission_classes = [AllowAny]

    # ✅ GET: fetch SLA by category and optional subcategory
    def get(self, request):
        category_id = request.query_params.get("category_id")
        subcategory_id = request.query_params.get("subcategory_id")

        # Check if category_id is provided
        if not category_id:
            return Response(
                {"detail": "category_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category_id = int(category_id)
            subcategory_id = int(subcategory_id) if subcategory_id else None
        except ValueError:
            return Response(
                {"detail": "Invalid category_id or subcategory_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Filter with or without subcategory
        filters = {
            "category_id": category_id,
        }
        if subcategory_id:
            filters["subcategory_id"] = subcategory_id

        #ticket_sla = TicketSLA.objects.filter(**filters).order_by("-id").first()
            ticket_sla = TicketSLA.objects.filter(**filters).values().annotate(Approver_level1_user=F('Approver_level1_user_id__name'),Approver_level2_user=F('Approver_level2_user_id__name'),
                Approver_level3_user=F('Approver_level3_user_id__name'),
                Approver_level4_user=F('Approver_level4_user_id__name'),
                Approver_level5_user=F('Approver_level5_user_id__name'),
                ).order_by("-id").first()
            return Response(ticket_sla, status=status.HTTP_200_OK)

        # if not ticket_sla:
        #     return Response({}, status=status.HTTP_200_OK)

        # serializer = TicketSLASerializer(ticket_sla)
        # return Response(serializer.data, status=status.HTTP_200_OK)

    # ✅ POST: create or update SLA without entity_id (just category_id and subcategory_id)
    def post(self, request):
        category_id = request.query_params.get("category_id")
        subcategory_id = request.query_params.get("subcategory_id")

        if not (category_id and subcategory_id):
            return Response(
                {"detail": "category_id and subcategory_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            category_id = int(category_id)
            subcategory_id = int(subcategory_id)
        except ValueError:
            return Response(
                {"detail": "Invalid category_id or subcategory_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Try to find existing SLA
        ticket_sla = TicketSLA.objects.filter(
            category_id=category_id,
            subcategory_id=subcategory_id
        ).first()

        if ticket_sla:
            # ✅ Update existing SLA
            serializer = TicketSLASerializer(ticket_sla, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_date=timezone.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # ✅ Create new SLA
            serializer = TicketSLASerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    category_id=category_id,
                    subcategory_id=subcategory_id
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TicketSLAListCreateView(APIView):
    permission_classes = [AllowAny]

    # ✅ GET: fetch SLA by entity/category/subcategory
    def get(self, request):
        entity_id = request.query_params.get("entity_id")
        category_id = request.query_params.get("category_id")
        subcategory_id = request.query_params.get("subcategory_id")

        if not (entity_id and category_id):
            return Response(
                {"detail": "entity_id and category_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            entity_id = int(entity_id)
            category_id = int(category_id)
            subcategory_id = int(subcategory_id) if subcategory_id else None
        except ValueError:
            return Response(
                {"detail": "Invalid entity_id, category_id, or subcategory_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Filter with or without subcategory
        filters = {
            "entity_id": entity_id,
            "category_id": category_id,
        }
        if subcategory_id:
            filters["subcategory_id"] = subcategory_id

        # ticket_sla = TicketSLA.objects.filter(**filters).order_by("-id").first()

        ticket_sla = TicketSLA.objects.filter(**filters).values().annotate(Approver_level1_user=F('Approver_level1_user_id__name'),Approver_level2_user=F('Approver_level2_user_id__name'),
        Approver_level3_user=F('Approver_level3_user_id__name'),
        Approver_level4_user=F('Approver_level4_user_id__name'),
        Approver_level5_user=F('Approver_level5_user_id__name'),
        )

        if not ticket_sla:
            return Response({}, status=status.HTTP_200_OK)

        # serializer = TicketSLASerializer(ticket_sla)
        return Response(ticket_sla, status=status.HTTP_200_OK)

    # ✅ POST: update existing or create new SLA
    def post(self, request):
        entity_id = request.query_params.get("entity_id")
        category_id = request.query_params.get("category_id")
        subcategory_id = request.query_params.get("subcategory_id")

        if not (entity_id and category_id and subcategory_id):
            return Response(
                {"detail": "entity_id, category_id, and subcategory_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            entity_id = int(entity_id)
            category_id = int(category_id)
            subcategory_id = int(subcategory_id)
        except ValueError:
            return Response(
                {"detail": "Invalid entity_id, category_id, or subcategory_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Try to find existing SLA
        ticket_sla = TicketSLA.objects.filter(
            entity_id=entity_id,
            category_id=category_id,
            subcategory_id=subcategory_id
        ).first()

        if ticket_sla:
            # ✅ Update existing SLA
            serializer = TicketSLASerializer(ticket_sla, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_date=timezone.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # ✅ Create new SLA
            serializer = TicketSLASerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    entity_id=entity_id,
                    category_id=category_id,
                    subcategory_id=subcategory_id
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TicketSLADetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        
        try:
            ticket_sla = TicketSLA.objects.filter(pk=pk).values().annotate(Approver_level1_user=F('Approver_level1_user_id__name'),Approver_level2_user=F('Approver_level2_user_id__name'),
            Approver_level3_user=F('Approver_level3_user_id__name'),
            Approver_level4_user=F('Approver_level4_user_id__name'),
            Approver_level5_user=F('Approver_level5_user_id__name'),
            )
            # serializer = TicketSLASerializer(ticket_sla)
            return Response(ticket_sla, status=status.HTTP_200_OK)
        except TicketSLA.DoesNotExist:
            return Response({"error": "Ticket SLA not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
       
        try:
            ticket_sla = TicketSLA.objects.get(pk=pk)
            serializer = TicketSLASerializer(ticket_sla, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    updated_by=request.user.username if request.user.is_authenticated else 'anonymous',
                    updated_date=timezone.now()
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TicketSLA.DoesNotExist:
            return Response({"error": "Ticket SLA not found"}, status=status.HTTP_404_NOT_FOUND)


# ---------------- Ticket Actions ----------------
class TicketActionView(APIView):
    permission_classes = [AllowAny]

    VALID_ACTIONS = {'approve', 'reject', 'onhold', 'reassign', 'followup','unhold'}
    ACTION_TO_LABEL = {
        'approve': 'Approved',
        'reject': 'Rejected',
        'onhold': 'On-Hold',
        'reassign': 'Re-assigned',
        'unhold': 'Resumed'
    }

    def _get_master_status(self, label):
        from .models import TicketsMasterConfiguration
        try:
            return TicketsMasterConfiguration.objects.get(
                field_type__iexact='Status',
                field_values__iexact=label,
                is_active='Y'
            )
        except TicketsMasterConfiguration.DoesNotExist:
            return None

    def get(self, request, ticket_no):
        ticket = get_object_or_404(CreateTicket, ticket_no=ticket_no)
        ticket_data = CreateTicketSerializer(ticket, context={'request': request}).data
        logs = TicketApprovalLog.objects.filter(ticket=ticket)\
            .exclude(approval_status__iexact='Follow-Up')\
            .order_by('created_at')
        log_data = TicketApprovalLogSerializer(logs, many=True).data
        return Response({'ticket': ticket_data, 'approval_logs': log_data}, status=200)

    def post(self, request, ticket_no):
        try:
            ticket = get_object_or_404(CreateTicket, ticket_no=ticket_no)
            action = request.data.get("action", "").lower()
            comments = request.data.get("comments", "")
            user = request.user
            reassigned_user_id = request.data.get("reassign_to")
            if action not in self.VALID_ACTIONS:
                return Response({"error": "Invalid action"}, status=400)

            current_log = TicketApprovalLog.objects.filter(ticket=ticket, is_current_level=True).first()
            if not current_log:
                return Response({"error": "No active approver level found."}, status=400)
            if current_log.created_by_id != user.id:
                return Response({"error": "You are not the assigned approver for this level."}, status=403)

            now = timezone.now()

            # ---------------- APPROVE ----------------
            if action == "approve":
                saved_seconds = 0
                # Use frozen time from on-hold (if any)
                if getattr(current_log, 'remaining_sla_seconds', None) is not None:
                    saved_seconds = current_log.remaining_sla_seconds or 0
                # Calculate on-hold duration if it was on hold
                if current_log.onhold_start and current_log.sla_end_time:
                    saved_seconds = int((current_log.sla_end_time - current_log.onhold_start).total_seconds())
                    # Record on-hold duration
                    onhold_duration = int((now - current_log.onhold_start).total_seconds())
                    current_log.total_onhold_seconds = (current_log.total_onhold_seconds or 0) + onhold_duration
                    current_log.onhold_start = None
                    current_log.save()
                elif current_log.sla_end_time:
                    # Normal case: not on-hold
                    if current_log.sla_end_time > now:
                        saved_seconds = int((current_log.sla_end_time - now).total_seconds())
                saved_seconds = max(0, saved_seconds)

                current_log.status = "Approved"
                current_log.approval_status = "Approved"
                current_log.comments = comments or "Approved"
                current_log.approved_by_id = user.id
                current_log.approved_on = now
                current_log.is_current_level = False
                current_log.save()

                # Check if this was the FINAL approver
                next_user = getattr(ticket.sla, f"Approver_level{current_log.current_level + 1}_user", None)
                if not next_user:
                    # FINAL APPROVAL → AUTO CLOSE THE TICKET
                    closed_status = self._get_master_status("Closed")
                    if closed_status:
                        ticket.status = closed_status
                        ticket.closed_on = timezone.now()  # Optional: add this field if you want
                        ticket.save()
                        # Send closure email to requester
                        template = TicketEmailTemplate.objects.filter(email_event="Ticket Closed", is_active="Y").first()
                        if template and ticket.requested.email:
                            ctx = Context({
                                'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
                                'ticket_no': ticket.ticket_no,
                                'name': ticket.title or "Ticket",
                                'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                                'mail_signature': 'IT Support Team',
                            })
                            html = Template(template.email_template).render(ctx)
                            send_email_task.delay([ticket.requested.email], f"Ticket #{ticket.ticket_no} Closed", html)
                        return Response({
                            "success": True,
                            "message": "Ticket approved and CLOSED successfully!",
                            "final_action": True
                        }, status=200)
                # # Not final → escalate with bonus time
                # escalate_to_next_approver(
                #     ticket,
                #     current_log.current_level,
                #     reason="USER_APPROVED",
                #     bonus_seconds=saved_seconds
                # )
                # Update status to Pending (still needs more approvals)
                ticket.status = self._get_master_status("Approved") or self._get_master_status("Pending")
                ticket.save()
                return Response({
                    "success": True,
                    "message": "Approved successfully!",
                    "bonus_time_given_to_next": f"{saved_seconds} seconds"
                }, status=200)

            # ---------------- REJECT ----------------
            elif action == "reject":
                current_log.status = "Rejected"
                current_log.approval_status = "Rejected"
                current_log.comments = comments or "No comments provided"
                current_log.approved_by_id = user.id
                current_log.approved_on = now
                current_log.is_current_level = False
                current_log.save()
                # Update ticket status
                rejected_status = self._get_master_status("Rejected")
                if rejected_status:
                    ticket.status = rejected_status
                    ticket.save()
                # SEND REJECTION EMAIL
                template = TicketEmailTemplate.objects.filter(email_event="Ticket Rejected", is_active="Y").first()
                if template and ticket.requested.email:
                    # SAFE WAY — uses your actual User fields
                    rejected_by_name = f"{user.firstname or ''} {user.realname or ''}".strip()
                    if not rejected_by_name:
                        rejected_by_name = user.email.split('@')[0]  # fallback to username part
                    elif len(rejected_by_name.strip()) < 2:
                        rejected_by_name = user.email
                    ctx = Context({
                        'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
                        'realname': getattr(ticket.requested, 'realname', '') or '',
                        'ticket_no': ticket.ticket_no,
                        'name': ticket.title or ticket.description or "Your Request",
                        'rejection_reason': comments or "No reason was provided.",
                        'rejected_by': rejected_by_name,
                        'ticket_url': f"http://localhost:5173/tickets/{ticket.ticket_no}",  # or use settings.FRONTEND_URL
                        'mail_signature': 'IT Support Team',
                        'year': timezone.now().year,
                    })
                    html = Template(template.email_template).render(ctx)
                    send_email_task.delay(
                        [ticket.requested.email],
                        f"Ticket #{ticket.ticket_no} Rejected",
                        html
                    )
                    # CC watchers
                    watcher_emails = [w.email for w in ticket.watchers.all() if w.email]
                    if watcher_emails:
                        send_email_task.delay(watcher_emails, f"Ticket #{ticket.ticket_no} Rejected", html)
                    logger.info(f"Ticket #{ticket.ticket_no} rejected by {user.email} → Email sent")
                else:
                    logger.warning("Ticket Rejected template missing or requester has no email")
                return Response({
                    "success": True,
                    "message": "Ticket rejected successfully and requester notified!"
                }, status=200)

            # ---------------- REASSIGN (SUPPORTS USER OR GROUP ID) ----------------
            elif action == "reassign":
                if not reassigned_user_id:
                    return Response({"error": "Please select a user or group"}, status=400)

                target_id = int(reassigned_user_id)
                new_user = None

                # Try user first
                try:
                    new_user = User.objects.get(id=target_id)
                except User.DoesNotExist:
                    # Fallback: Assume group ID and pick a member
                    try:
                        from .models import Group  # Adjust import if Group is elsewhere (e.g., django.contrib.auth.models.Group)
                        group = Group.objects.get(id=target_id)
                        if not hasattr(group, 'members') or group.members.count() == 0:  # Adjust if members is a method/relation
                            return Response({"error": "Group has no active members"}, status=400)
                        new_user = group.members.first()  # Or randomize: group.members.order_by('?').first()
                        logger.info(f"Reassigned to group {group.name} → Selected user {new_user.email}")
                    except Group.DoesNotExist:
                        return Response({"error": "Selected user or group does not exist"}, status=400)

                if not new_user:
                    return Response({"error": "No valid assignee found"}, status=400)

                # Only manager or current approver can reassign
                if not (is_privileged(user) or current_log.created_by_id == user.id):
                    return Response({"error": "Only manager or current approver can reassign"}, status=403)

                old_user = current_log.created_by

                # Update only the log (not SLA table)
                current_log.created_by = new_user
                current_log.status = "Reassigned"
                current_log.approval_status = "Reassigned"
                current_log.comments = f"Reassigned from {old_user.email if old_user else 'unknown'} to {new_user.email} by {user.email}"
                current_log.is_current_level = True  # New assignee is now active
                current_log.sla_end_time = current_log.sla_end_time  # Keep exact same SLA time (including bonus)

                # Handle any active on-hold before reassign
                if current_log.onhold_start:
                    onhold_duration = int((now - current_log.onhold_start).total_seconds())
                    current_log.total_onhold_seconds = (current_log.total_onhold_seconds or 0) + onhold_duration
                    current_log.onhold_start = None
                    current_log.save()

                current_log.save()

                # Restart escalation timer for new assignee
                # if current_log.sla_end_time:
                #     delay = max(1, int((current_log.sla_end_time - timezone.now()).total_seconds()))
                #     handle_sla_escalation.apply_async(
                #         args=[ticket.id, current_log.current_level],
                #         countdown=delay
                #     )

                ticket.status = self._get_master_status("Pending")
                ticket.save()

                # Email to new approver
                template = TicketEmailTemplate.objects.filter(email_event="Reassigned", is_active="Y").first()
                if template and new_user.email:
                    ctx = Context({
                        'next_user': new_user.firstname or new_user.username,
                        'firstname': ticket.requested.firstname,
                        'reason': 'This ticket was reassigned to you (previous approver unavailable)',
                        "ticket_no": ticket.ticket_no,
                        "name": ticket.title or ticket.description,
                        "date_creation": timezone.localtime(ticket.created_date),
                        'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                        'mail_signature': 'IT Support Team',
                    })
                    html = Template(template.email_template).render(ctx)
                    send_email_task.delay([new_user.email], f"Reassigned: Approval Request - Ticket #{ticket.ticket_no}", html)

                # Notify old approver
                if old_user and old_user.email and old_user.id != new_user.id:
                    send_email_task.delay([old_user.email], f"Ticket #{ticket.ticket_no} Reassigned", f"You are no longer the approver — reassigned to {new_user.email}")

                return Response({
                    "success": True,
                    "message": f"Reassigned to {new_user.email} — only they can approve now"
                }, status=200)

            # ---------------- ON-HOLD ----------------
            elif action == "onhold":
                if current_log.onhold_start:
                    return Response({"error": "Ticket is already on hold"}, status=400)
                current_log.onhold_start = now
                current_log.status = "On-Hold"
                current_log.approval_status = "On-Hold"
                current_log.comments = comments
                current_log.save()
                ticket.status = self._get_master_status("On-Hold")
                ticket.save()
                template = TicketEmailTemplate.objects.filter(email_event="On Hold", is_active="Y").first()
                recipients = [ticket.requested.email] + [w.email for w in ticket.watchers.all() if w.email]
                if template and recipients:
                    ctx = Context({
                        'current_difference': 'several',
                        'ticket_id': ticket.ticket_no,
                        'firstname': ticket.requested.firstname or ticket.requested.email.split('@')[0],
                        'realname': getattr(ticket.requested, 'realname', '') or '',
                        'date_creation': timezone.localtime(ticket.created_date).strftime("%d %B %Y, %I:%M %p"),
                        'name': ticket.title or ticket.description or "No Title",
                        'ticket_url': f"http://yourdomain.com/tickets/{ticket.ticket_no}",
                        'mail_signature': 'IT Support Team',
                        'year': timezone.now().year,
                    })
                    html = Template(template.email_template).render(ctx)
                    send_email_task.delay(recipient, f"Ticket #{ticket.ticket_no} On Hold", html)
                return Response({"success": "On hold - mail sent"}, status=200)

            # ---------------- UNHOLD (RESUME) ----------------
            elif action == "unhold":
                if not current_log.onhold_start:
                    return Response({"error": "Ticket is not on hold"}, status=400)
                now = timezone.now()

                # Calculate how much time was frozen
                frozen_time_left = int((current_log.sla_end_time - current_log.onhold_start).total_seconds())
                onhold_duration = int((now - current_log.onhold_start).total_seconds())
                # Record total on-hold time
                current_log.total_onhold_seconds = (current_log.total_onhold_seconds or 0) + onhold_duration
                current_log.onhold_start = None
                current_log.status = "Pending"
                current_log.approval_status = "Pending"
                current_log.is_current_level = True
                current_log.comments = comments or "Approval process resumed"
                current_log.save()
                # Resume SLA: Give back the frozen time
                new_sla_end_time = now + timedelta(seconds=max(0, frozen_time_left))
                current_log.sla_end_time = new_sla_end_time
                current_log.save()
                # if current_log.sla_end_time:
                #     delay = max(1, int((current_log.sla_end_time - timezone.now()).total_seconds()))
                #     handle_sla_escalation.apply_async(
                #         args=[ticket.id, current_log.current_level],
                #         countdown=delay
                #     )
                # Update ticket status
                pending_status = self._get_master_status("Pending")
                if pending_status:
                    ticket.status = pending_status
                    ticket.save()
                return Response({
                    "success": True,
                    "message": "Approval resumed — timer restarted with remaining time",
                    "remaining_seconds": max(0, frozen_time_left)
                }, status=200)

            # ---------------- FOLLOWUP ---------------- (Basic implementation: Add log entry without changing status/timer)
            elif action == "followup":
                # Create a new followup log (non-approval, just tracking)
                from .models import TicketApprovalLog  # Ensure import if needed
                followup_log = TicketApprovalLog.objects.create(
                    ticket=ticket,
                    sla=ticket.sla,
                    current_level=current_log.current_level,
                    created_by=user,
                    status="Follow-Up",
                    approval_status="Follow-Up",
                    comments=comments or "Follow-up note added",
                    is_current_level=False,  # Not blocking approval
                )
                return Response({
                    "success": True,
                    "message": "Follow-up note added successfully!",
                    "log_id": followup_log.id
                }, status=200)

            else:
                return Response({"error": "Action not implemented"}, status=400)

        except Exception as e:
            logger.error(f"Ticket action error for {ticket_no}: {str(e)}")
            return Response({"error": str(e)}, status=500)



class WatcherGroupListCreateView(APIView):
    """
    GET: List watcher groups
    POST: Create a new watcher group
    """
    def get(self, request):
        groups = UsersGroup.objects.all().order_by('id')
        serializer = UsersGroupSerializer(groups, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UsersGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatcherGroupDetailView(APIView):
    """
    GET, PUT, DELETE watcher group by ID
    """
    def get_object(self, pk):
        try:
            return UsersGroup.objects.get(pk=pk)
        except UsersGroup.DoesNotExist:
            return None

    def get(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UsersGroupSerializer(group)
        return Response(serializer.data)

    def put(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UsersGroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        group = self.get_object(pk)
        if not group:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        group.delete()
        return Response({"message": "Group deleted"}, status=status.HTTP_204_NO_CONTENT)


class WatcherUserListView(APIView):
    """
    List all users who can act as watchers
    """
    def get(self, request):
        search = request.query_params.get("search", "")
        users = User.objects.filter(
            Q(name__icontains=search) | Q(realname__icontains=search),
            is_deleted=False,
            is_active=True,
        ).order_by('name')
        serializer = WatcherUserSerializer(users, many=True)
        return Response(serializer.data)

# 12/05/2025
# class HolidayAPIView(APIView):
#     """
#     API View for managing Holidays (List, Create, Update, Delete)
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         """List all holidays or get a single holiday by ID."""
#         if pk:
#             holiday = get_object_or_404(Holiday, pk=pk)
#             serializer = HolidaySerializer(holiday)
#             return Response(serializer.data)
#         else:
#             holidays = Holiday.objects.all().order_by("-date")
#             serializer = HolidaySerializer(holidays, many=True)
#             return Response(serializer.data)

#     def post(self, request):
#         """Create a new holiday — only one per entity/location/department/date."""
#         serializer = HolidaySerializer(data=request.data)
#         if serializer.is_valid():
#             date = serializer.validated_data.get("date")
#             entity = serializer.validated_data.get("entity")
#             location = serializer.validated_data.get("location")
#             department = serializer.validated_data.get("department")

#             # ✅ Prevent duplicate holidays for same entity/location/department/date
#             duplicate = Holiday.objects.filter(
#                 date=date,
#                 entity=entity,
#                 location=location,
#                 department=department
#             ).exists()

#             if duplicate:
#                 return Response(
#                     {"error": "A holiday already exists for this entity, location, and department on this date."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         """Update existing holiday — still ensure no duplicates."""
#         holiday = get_object_or_404(Holiday, pk=pk)
#         serializer = HolidaySerializer(holiday, data=request.data, partial=True)
#         if serializer.is_valid():
#             date = serializer.validated_data.get("date", holiday.date)
#             entity = serializer.validated_data.get("entity", holiday.entity)
#             location = serializer.validated_data.get("location", holiday.location)
#             department = serializer.validated_data.get("department", holiday.department)

#             # ✅ Prevent duplicates except for the same record
#             duplicate = Holiday.objects.filter(
#                 date=date,
#                 entity=entity,
#                 location=location,
#                 department=department
#             ).exclude(id=holiday.id).exists()

#             if duplicate:
#                 return Response(
#                     {"error": "Another holiday already exists for this entity, location, and department on this date."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         """Delete a holiday record."""
#         holiday = get_object_or_404(Holiday, pk=pk)
#         holiday.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
class HolidayAPIView(APIView):
    """
    API View for managing Holidays (List, Create, Update, Delete)
    """
    permission_classes = [AllowAny]

    def get_entity_names(self, entity_ids):
        """
        Helper to fetch entity names from entity_ids list
        """
        if not entity_ids:
            return ["No Entity"]
        entities = Entity.objects.filter(id__in=entity_ids)
        return [entity.name for entity in entities if entity.name]

    def get(self, request, pk=None):
        """List all holidays or get a single holiday by ID."""
        if pk:
            holiday = get_object_or_404(Holiday, pk=pk)
            data = HolidaySerializer(holiday).data
            return Response(data)
        else:
            holidays = Holiday.objects.all().order_by("-date")
            serializer = HolidaySerializer(holidays, many=True)
            return Response(serializer.data)

    def post(self, request):
        """Create a new holiday — only one per entity_ids/location/department/date (no overlaps)."""
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            date = validated_data.get("date")
            entity_ids = validated_data.get("entity_ids")
            location = validated_data.get("location")
            department = validated_data.get("department")

            # ✅ Prevent duplicate holidays: check for overlaps in entity_ids
            for entity_id in entity_ids:
                duplicate = Holiday.objects.filter(
                    date=date,
                    entity_ids__contains=[entity_id],
                    location=location,
                    department=department
                ).exists()

                if duplicate:
                    return Response(
                        {"error": f"A holiday already exists for entity ID {entity_id}, location, and department on this date."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Set created/modified by if not provided
            if request.user.is_authenticated:
                validated_data["created_by"] = request.user
                validated_data["modified_by"] = request.user
            serializer.save()
            # Re-serialize to include entity_names
            instance = Holiday.objects.get(id=serializer.data['id'])
            data = HolidaySerializer(instance).data
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Update existing holiday — still ensure no duplicates/overlaps."""
        holiday = get_object_or_404(Holiday, pk=pk)
        serializer = HolidaySerializer(holiday, data=request.data, partial=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            date = validated_data.get("date", holiday.date)
            entity_ids = validated_data.get("entity_ids", holiday.entity_ids)
            location = validated_data.get("location", holiday.location)
            department = validated_data.get("department", holiday.department)

            # ✅ Prevent duplicates/overlaps except for the same record
            for entity_id in entity_ids:
                duplicate = Holiday.objects.filter(
                    date=date,
                    entity_ids__contains=[entity_id],
                    location=location,
                    department=department
                ).exclude(id=holiday.id).exists()

                if duplicate:
                    return Response(
                        {"error": f"Another holiday already exists for entity ID {entity_id}, location, and department on this date."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if request.user.is_authenticated:
                validated_data["modified_by"] = request.user
            serializer.save()
            # Re-serialize to include entity_names
            data = HolidaySerializer(holiday).data
            return Response(data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a holiday record."""
        holiday = get_object_or_404(Holiday, pk=pk)
        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
#working code
# class HolidayAPIView(APIView):
#     """
#     API View for managing Holidays (List, Create, Update, Delete)
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         """List all holidays or get a single holiday by ID."""
#         if pk:
#             holiday = get_object_or_404(Holiday, pk=pk)
#             serializer = HolidaySerializer(holiday)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             holidays = Holiday.objects.all().order_by("date")

#             # Filters
#             entity_id = request.query_params.get("entity_id")
#             department_id = request.query_params.get("department_id")
#             location_id = request.query_params.get("location_id")

#             if entity_id:
#                 holidays = holidays.filter(entity_id=entity_id)
#             if department_id:
#                 holidays = holidays.filter(department_id=department_id)
#             if location_id:
#                 holidays = holidays.filter(location_id=location_id)

#             serializer = HolidaySerializer(holidays, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)


#     def post(self, request):
#         """Create a new holiday."""
#         data = request.data.copy()
#         data["created_by"] = request.user.id
#         data["created_ip"] = self.get_client_ip(request)

#         serializer = HolidaySerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             {"message": "Holiday created successfully", "data": serializer.data},
#             status=status.HTTP_201_CREATED
#         )

#     def put(self, request, pk):
#         """Update an existing holiday."""
#         holiday = get_object_or_404(Holiday, pk=pk)
#         data = request.data.copy()
#         data["modified_by"] = request.user.id
#         data["modified_ip"] = self.get_client_ip(request)

#         serializer = HolidaySerializer(holiday, data=data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(
#             {"message": "Holiday updated successfully", "data": serializer.data},
#             status=status.HTTP_200_OK
#         )

#     def delete(self, request, pk):
#         """Delete a holiday."""
#         holiday = get_object_or_404(Holiday, pk=pk)
#         holiday.delete()
#         return Response(
#             {"message": "Holiday deleted successfully"},
#             status=status.HTTP_204_NO_CONTENT
#         )

#     def get_client_ip(self, request):
#         """Helper to capture client IP"""
#         x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#         if x_forwarded_for:
#             return x_forwarded_for.split(",")[0]
#         return request.META.get("REMOTE_ADDR")


class UpcomingHolidayAPIView(APIView):
    """Fetch upcoming holidays."""
    permission_classes = [AllowAny]

    def get(self, request):
        today = timezone.now().date()
        holidays = Holiday.objects.filter(date__gte=today).order_by("date")
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# class UserRoleMappingAPIView(APIView):
   
#     permission_classes = [AllowAny]  # Adjust to IsAuthenticated or custom permissions as needed

#     def get(self, request, pk=None):
#         if pk:
#             mapping = get_object_or_404(
#                 UserRoleMapping.objects.select_related('user', 'role', 'entity'), pk=pk
#             )
#             serializer = UserRoleMappingSerializer(mapping)
#             return Response(serializer.data)
        
#         # List all; can extend with filters e.g., user_id = request.query_params.get('user_id')
#         mappings = UserRoleMapping.objects.select_related('user', 'role', 'entity')
#         serializer = UserRoleMappingSerializer(mappings, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         data = request.data.copy()
        
#         # Optional: Set audit fields if needed (not in model, but for consistency)
#         user_str = str(request.user) if request.user.is_authenticated else 'Anonymous'
#         # Note: Model uses auto_now_add, so no need to set dates here

#         serializer = UserRoleMappingSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         mapping = get_object_or_404(
#             UserRoleMapping.objects.select_related('user', 'role', 'entity'), pk=pk
#         )
#         data = request.data.copy()
#         # Optional: Set updated_by if adding that field later
#         user_str = str(request.user) if request.user.is_authenticated else 'Anonymous'

#         serializer = UserRoleMappingSerializer(mapping, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         mapping = get_object_or_404(UserRoleMapping, pk=pk)
#         mapping.delete()
#         return Response(
#             {"message": "User role mapping deleted successfully."},
#             status=status.HTTP_204_NO_CONTENT
#         )
class UserRoleMappingAPIView(APIView):
    permission_classes = [AllowAny]  # Adjust to IsAuthenticated or custom permissions as needed

    def get(self, request, pk=None):
        if pk:
            mapping = get_object_or_404(
                UserRoleMapping.objects.select_related('user', 'role', 'entity'), pk=pk
            )
            serializer = UserRoleMappingSerializer(mapping)
            return Response(serializer.data)
        
        # List all; can extend with filters e.g., user_id = request.query_params.get('user_id')
        mappings = UserRoleMapping.objects.select_related('user', 'role', 'entity')
        serializer = UserRoleMappingSerializer(mappings, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        user_id = data.get('user_id')
        role_ids = data.get('role_id', [])  # Expected list of role IDs (integers)
        entity_ids = data.get('entity_id', [])  # Expected list of entity IDs (integers)

        if not user_id or not role_ids or not entity_ids:
            return Response(
                {"error": "Payload must include 'user_id' (int), 'role_id' (list of ints), and 'entity_id' (list of ints)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optional: Set audit fields if needed (not in model, but for consistency)
        user_str = str(request.user) if request.user.is_authenticated else 'Anonymous'
        # Note: Model uses auto_now_add, so no need to set dates here

        handled_mappings = []  # Renamed to reflect create/update/skip
        errors = []

        # Use transaction to ensure atomicity for bulk upsert
        with transaction.atomic():
            for role_id in role_ids:
                for entity_id in entity_ids:
                    # Use standard field names for serializer (user, role, entity as PKs)
                    mapping_data = {
                        'user': user_id,
                        'role': role_id,
                        'entity': entity_id,
                    }
                    # Check for existing
                    existing = UserRoleMapping.objects.filter(
                        user_id=user_id, role_id=role_id, entity_id=entity_id
                    ).first()
                    if existing:
                        # If exists, "update" (but no new data, so just serialize existing; updated_date will trigger on save if needed)
                        serializer = UserRoleMappingSerializer(existing, data=mapping_data, partial=True)
                        if serializer.is_valid():
                            serializer.save()  # This will update updated_date
                            handled_mappings.append(serializer.data)
                        else:
                            errors.append({
                                'role': role_id,
                                'entity': entity_id,
                                'errors': serializer.errors
                            })
                        continue
                    
                    # For new: create via serializer (triggers validation)
                    serializer = UserRoleMappingSerializer(data=mapping_data)
                    if serializer.is_valid():
                        serializer.save()
                        handled_mappings.append(serializer.data)
                    else:
                        errors.append({
                            'role': role_id,
                            'entity': entity_id,
                            'errors': serializer.errors
                        })

        if errors:
            return Response({
                "handled": handled_mappings,
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS if handled_mappings else status.HTTP_400_BAD_REQUEST)

        return Response(handled_mappings, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        mapping = get_object_or_404(
            UserRoleMapping.objects.select_related('user', 'role', 'entity'), pk=pk
        )
        data = request.data.copy()
        # Optional: Set updated_by if adding that field later
        user_str = str(request.user) if request.user.is_authenticated else 'Anonymous'

        serializer = UserRoleMappingSerializer(mapping, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        mapping = get_object_or_404(UserRoleMapping, pk=pk)
        mapping.delete()
        return Response(
            {"message": "User role mapping deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
        
from django.utils import timezone
from datetime import timedelta
from calendar import monthrange
from django.db.models import Q, Avg, Count, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CEODashboardAPIView(APIView):
    def get(self, request):
        """Return CEO dashboard statistics including overall, department-wise, priority-based counts,
        and average resolution times with month-wise breakdown"""

        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        search = request.query_params.get('search', '').strip()

        now = timezone.now()
        base_qs = CreateTicket.objects.all()

        # --- Date filter ---
        start_date = end_date = None
        if start_date_str and end_date_str:
            try:
                start_date = timezone.make_aware(
                    timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                )
                end_date = timezone.make_aware(
                    timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
                ) + timedelta(days=1) - timedelta(seconds=1)

                base_qs = base_qs.filter(
                    created_date__gte=start_date, created_date__lte=end_date
                )
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)

        # --- Search filter ---
        if search:
            search_filter = Q(title__icontains=search) | Q(description__icontains=search)
            base_qs = base_qs.filter(search_filter)

        # --- Helper: serialize ticket fully ---
        def serialize_ticket(ticket):
            return {
                "id": ticket.id,
                "ticket_no": ticket.ticket_no,
                "title": ticket.title,
                "description": ticket.description,
                "status_detail": {
                    "field_values": ticket.status.field_values if ticket.status else None
                } if hasattr(ticket, 'status') and ticket.status else None,
                "category_detail": {
                    "entity_name": ticket.category.entity.name if ticket.category else None
                } if hasattr(ticket, 'category') and ticket.category else None,
                "subcategory_detail": {
                    "subcategory_name": ticket.subcategory.subcategory_name if ticket.subcategory else None
                } if hasattr(ticket, 'subcategory') and ticket.subcategory else None,
                "priority_detail": {
                    "field_values": ticket.priority.field_values if ticket.priority else None
                } if hasattr(ticket, 'priority') and ticket.priority else None,
                "department_detail": {
                    "field_name": ticket.department.field_name if ticket.department else None
                } if hasattr(ticket, 'department') and ticket.department else None,
                "location_detail": {
                    "field_name": ticket.location.field_name if ticket.location else None
                } if hasattr(ticket, 'location') and ticket.location else None,
                "requested_detail": {
                    "name": getattr(ticket.requested, 'name', None) or getattr(ticket.requested, 'email', None),
                    "email": getattr(ticket.requested, 'email', None)
                } if ticket.requested else None,
                "created_date": ticket.created_date,
                "updated_date": getattr(ticket, 'updated_date', ticket.created_date),  # Fallback to created_date if no updated_date
            }

        # --- SLA breached helper ---
        def get_sla_breached_data(tickets_qs):
            breached_ids = TicketApprovalLog.objects.filter(
                sla_breach=True,
                ticket__in=tickets_qs
            ).values_list('ticket', flat=True).distinct()
            breached_tickets = tickets_qs.filter(id__in=breached_ids)
            return {
                "count": breached_tickets.count(),
                "tickets": [serialize_ticket(t) for t in breached_tickets]
            }

        # --- Helper for status-based data ---
        def get_status_data(tickets_qs, status_value):
            status_tickets = tickets_qs.filter(status__field_values__iexact=status_value)
            return {
                "count": status_tickets.count(),
                "tickets": [serialize_ticket(t) for t in status_tickets]
            }

        # --- Helper for overall status counts ---
        def get_overall_status_counts(tickets_qs):
            return {
                "pending": get_status_data(tickets_qs, 'Pending')["count"],
                "approved": get_status_data(tickets_qs, 'Approved')["count"],
                "rejected": get_status_data(tickets_qs, 'Rejected')["count"],
                "on_hold": get_status_data(tickets_qs, 'On Hold')["count"],
                "solved": get_status_data(tickets_qs, 'Solved')["count"],
                "closed": get_status_data(tickets_qs, 'Closed')["count"],
            }

        # --- Helper for average resolution time (in hours) ---
        # def get_average_resolution_time(tickets_qs):
        #     resolved_tickets = tickets_qs.filter(
        #         status__field_values__in=['Solved', 'Closed']
        #     ).annotate(
        #         resolution_hours=(
        #             (F('updated_date') - F('created_date')).total_seconds() / 3600
        #         )
        #     )
        #     avg_hours = resolved_tickets.aggregate(avg_hours=Avg('resolution_hours'))['avg_hours']
        #     return round(avg_hours, 2) if avg_hours else 0

        # --- Overall stats ---
        overall_sla = get_sla_breached_data(base_qs)
        overall_status = get_overall_status_counts(base_qs)
        # overall_avg_time = get_average_resolution_time(base_qs)

        today_start = timezone.make_aware(timezone.datetime(now.year, now.month, now.day))
        today_end = today_start + timedelta(days=1) - timedelta(seconds=1)

        month_start = timezone.make_aware(timezone.datetime(now.year, now.month, 1))
        last_day = monthrange(now.year, now.month)[1]
        month_end = timezone.make_aware(timezone.datetime(now.year, now.month, last_day, 23, 59, 59))

        data = {
            "overall": {
                "total_tickets": base_qs.count(),
                "today_tickets": base_qs.filter(created_date__gte=today_start, created_date__lte=today_end).count(),
                "month_tickets": base_qs.filter(created_date__gte=month_start, created_date__lte=month_end).count(),
                **overall_status,
                "sla_breached_count": overall_sla["count"],
                "sla_breached_tickets": overall_sla["tickets"],
                # "average_resolution_time_hours": overall_avg_time,
                # Status tickets for overall
                "pending_tickets": get_status_data(base_qs, 'Pending')["tickets"],
                "approved_tickets": get_status_data(base_qs, 'Approved')["tickets"],
                "rejected_tickets": get_status_data(base_qs, 'Rejected')["tickets"],
                "on_hold_tickets": get_status_data(base_qs, 'On Hold')["tickets"],
                "solved_tickets": get_status_data(base_qs, 'Solved')["tickets"],
                "closed_tickets": get_status_data(base_qs, 'Closed')["tickets"],
            }
        }

        # --- Department-wise stats ---
        department_stats = []
        departments = base_qs.values('department__field_name').distinct().exclude(department__field_name__isnull=True)
        for dept in departments:
            dept_name = dept['department__field_name']
            dept_qs = base_qs.filter(department__field_name=dept_name)
            dept_sla = get_sla_breached_data(dept_qs)
            dept_status = get_overall_status_counts(dept_qs)
            # dept_avg_time = get_average_resolution_time(dept_qs)
            department_stats.append({
                "department": dept_name,
                "total_tickets": dept_qs.count(),
                **dept_status,
                "sla_breached_count": dept_sla["count"],
                "sla_breached_tickets": dept_sla["tickets"],
                # "average_resolution_time_hours": dept_avg_time,
            })
        data["department_wise"] = department_stats

        # --- Priority-based stats ---
        priority_stats = []
        priorities = base_qs.values('priority__field_values').distinct().exclude(priority__field_values__isnull=True)
        for prio in priorities:
            prio_value = prio['priority__field_values']
            prio_qs = base_qs.filter(priority__field_values__iexact=prio_value)
            prio_sla = get_sla_breached_data(prio_qs)
            prio_status = get_overall_status_counts(prio_qs)
            # prio_avg_time = get_average_resolution_time(prio_qs)
            priority_stats.append({
                "priority": prio_value,
                "total_tickets": prio_qs.count(),
                **prio_status,
                "sla_breached_count": prio_sla["count"],
                "sla_breached_tickets": prio_sla["tickets"],
                # "average_resolution_time_hours": prio_avg_time,
            })
        data["priority_wise"] = priority_stats

        return Response(data, status=status.HTTP_200_OK)

# class RolePermissionMappingAPIView(APIView):
#     """
#     Handles fetching and updating role permissions (menu access).
#     """
#     # permission_classes = [AllowAny]  # Adjust as needed

#     def get(self, request):
#         role_id = request.query_params.get('role_id')
#         entity_id = request.query_params.get('entity_id')
#         qs = RolePermissionMapping.objects.filter(is_active=True)
#         if role_id:
#             qs = qs.filter(role_id=role_id)
#         if entity_id:
#             qs = qs.filter(entity_id=entity_id)
#         serializer = RolePermissionMappingSerializer(qs, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = RolePermissionMappingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request, pk):
#         instance = get_object_or_404(RolePermissionMapping, pk=pk, is_active=True)
#         serializer = RolePermissionMappingSerializer(instance, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         instance = get_object_or_404(RolePermissionMapping, pk=pk, is_active=True)
#         instance.is_active = False  # Soft delete
#         instance.save()
#         return Response({"message": "Permission revoked successfully."}, status=status.HTTP_204_NO_CONTENT)




# class CeoApprovalDashboardApiView(APIView):
#     """
#     API View for managing Holidays (List, Create, Update, Delete)
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         data =  CeoApprovalDashboard(request=None)
#         return Response(data)
    
# class HODApprovalDashboardAPI(APIView):
#     """
#     API View for managing Holidays (List, Create, Update, Delete)
#     """
#     permission_classes = [AllowAny]

#     def get(self, request, pk=None):
#         data =  HODApprovalDashboardAPI(request=None)
#         return Response(data)
    
# class MessageListCreateView(APIView):
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
 
#     def get_queryset(self):
#         queryset = self.queryset
#         # Existing: Filter by userid
#         userid_filter = self.request.query_params.get('userid')
#         if userid_filter:
#             queryset = queryset.filter(userid=userid_filter)
#         # New: Filter by parent (replies to a specific message)
#         parent_filter = self.request.query_params.get('parent')
#         if parent_filter:
#             queryset = queryset.filter(parent_id=parent_filter)
#         # Optional: Or show top-level only (no parent)
#         # if self.request.query_params.get('top_level'):
#         #     queryset = queryset.filter(parent__isnull=True)
#         return queryset
 
#     def get(self, request):
#         messages = self.get_queryset()
#         serializer = self.serializer_class(messages, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
 
#     def post(self, request):
#         data = request.data.copy()
#         # Auto-set userid to current user if not provided
#         if not data.get('userid'):
#             data['userid'] = request.user.id
#         # Ensure the parent exists, if provided
#         if data.get('parent'):
#             try:
#                 parent_message = Message.objects.get(pk=data['parent'])
#             except Message.DoesNotExist:
#                 return Response({"parent": ["Invalid pk \"{}\" - object does not exist.".format(data['parent'])]},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         # parent is optional—serializer handles it
#         serializer = self.serializer_class(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
# class MessageDetailView(APIView):
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     permission_classes = [IsAuthenticatedOrReadOnly]
 
#     def get_object(self):
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(self.queryset, pk=pk)
 
#     def get(self, request, pk):
#         message = self.get_object()
#         # Optional: Include replies in response for easy threading
#         replies = Message.objects.filter(parent=message).order_by('-createdon')
#         reply_serializer = self.serializer_class(replies, many=True)
#         data = self.serializer_class(message).data
#         data['replies'] = reply_serializer.data  # Nested replies (flat list)
#         return Response(data, status=status.HTTP_200_OK)
 
#     def put(self, request, pk):
#         message = self.get_object()
#         data = request.data.copy()
#         data.pop('userid', None)  # Prevent userid change
#         data.pop('parent', None)  # Prevent changing parent (replies are immutable)
#         serializer = self.serializer_class(message, data=data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
#     def patch(self, request, pk):
#         message = self.get_object()
#         data = request.data.copy()
#         data.pop('userid', None)
#         data.pop('parent', None)
#         serializer = self.serializer_class(message, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
#     def delete(self, request, pk):
#         message = self.get_object()
#         # Optional: Cascade delete replies too? (Model handles via on_delete)
#         message.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
 
class MessageListCreateView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
 
    def get_queryset(self):
        queryset = Message.objects.all()
        ticket_no_filter = self.request.query_params.get('ticket_no')
        if ticket_no_filter:
            try:
                ticket = CreateTicket.objects.get(pk=ticket_no_filter)
                # Get all involved users for this ticket: requester + assignees + group members
                involved_users = set([ticket.requested.id] if ticket.requested else [])
                # Add direct assignees
                if hasattr(ticket, 'assigned_users') and ticket.assigned_users:
                    for user_id in ticket.assigned_users:
                        if isinstance(user_id, int):
                            involved_users.add(user_id)
                        elif isinstance(user_id, str) and user_id.isdigit():
                            involved_users.add(int(user_id))
                # Add group members
                if hasattr(ticket, 'assigned_groups') and ticket.assigned_groups:
                    for group_id in ticket.assigned_groups:
                        if isinstance(group_id, int):
                            try:
                                group = UsersGroup.objects.get(id=group_id)
                                for member in group.get_users():
                                    involved_users.add(member.id)
                            except UsersGroup.DoesNotExist:
                                pass
                # Filter messages involving any of these users or current user (admin)
                current_user_id = self.request.user.id
                involved_users.add(current_user_id)
                queryset = queryset.filter(
                    Q(ticket_no=ticket) & (
                        Q(sender_id__in=involved_users) | Q(receiver_id__in=involved_users)
                    )
                ).order_by('createdon')  # Chronological for chat
            except CreateTicket.DoesNotExist:
                queryset = queryset.none()
        return queryset
 
    def get(self, request):
        messages = self.get_queryset()
        serializer = self.serializer_class(messages, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        # For admin, allow sending to single receiver; frontend handles multiples
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Auto-set sender to current user (admin) if not provided
            if not request.data.get('sender'):
                serializer.validated_data['sender'] = request.user
            message = serializer.save()
            # Serialize with context for potential encryption handling
            return Response(self.serializer_class(message, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
# Remove legacy UserMessagesView or update if needed; assuming it's not used for admin
# Cleaned up: Removed userid/parent references

class MessageDetailView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
 
    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Message, pk=pk)
 
    def get(self, request, pk):
        message = self.get_object()
        serializer = self.serializer_class(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def put(self, request, pk):
        message = self.get_object()
        serializer = self.serializer_class(message, data=request.data, partial=False, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def patch(self, request, pk):
        message = self.get_object()
        serializer = self.serializer_class(message, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pk):
        message = self.get_object()
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserMessagesView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
 
    # def get(self, request, userid):
    #     messages = Message.objects.filter(userid=userid).order_by('-createdon')
    #     serializer = MessageSerializer(messages, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    # def get(self, request, userid):
    #     # Fetch messages where the user is sender OR receiver
    #     messages = Message.objects.filter(
    #         Q(sender_id=userid) | Q(receiver_id=userid)
    #     ).order_by('-createdon')
    #     serializer = MessageSerializer(messages, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    def get(self, request, userid, ticket_id=None):
        """
        GET /api/tickets/users/<userid>/messages/                  → All messages involving the user
        GET /api/tickets/users/<userid>/messages/<ticket_id>/      → ALL messages for the specified ticket (if user has access)
        """
        # Authentication & Authorization: Ensure only the user or staff can access
        if not request.user.is_staff and request.user.id != int(userid):
            return Response(
                {"error": "You can only view your own messages."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            userid = int(userid)  # Ensure it's an integer
        except (ValueError, TypeError):
            return Response({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        if ticket_id is None:
            # Case 1: Return all messages where the user is sender OR receiver
            queryset = Message.objects.filter(
                Q(sender_id=userid) | Q(receiver_id=userid)
            ).order_by('createdon')

            serializer = MessageSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)

        else:
            # Case 2: Specific ticket messages
            try:
                ticket_id = int(ticket_id)
                ticket = CreateTicket.objects.get(pk=ticket_id)
            except (ValueError, TypeError):
                return Response({"error": "Invalid ticket ID."}, status=status.HTTP_400_BAD_REQUEST)
            except CreateTicket.DoesNotExist:
                return Response({"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

            # Permission check: Is the user involved in this ticket?
            is_involved = False

            # 1. Requester (ticket creator)
            if ticket.requested_id == userid:
                is_involved = True

            # 2. Directly assigned users (assignees_detail is usually a related name or JSON field)
            # Adjust field name based on your model. Common cases:
            if hasattr(ticket, 'assignees_detail'):
                assigned_user_ids = [u.id for u in ticket.assignees_detail.all()] if ticket.assignees_detail else []
            elif hasattr(ticket, 'assigned_users'):  # If stored as JSON or list
                assigned_user_ids = ticket.assigned_users or []
            else:
                assigned_user_ids = []

            if userid in assigned_user_ids:
                is_involved = True

            # 3. Assigned via groups
            assigned_group_ids = []
            if hasattr(ticket, 'assigned_groups_detail'):
                assigned_group_ids = [g.id for g in ticket.assigned_groups_detail.all()]
            elif hasattr(ticket, 'assigned_groups'):
                assigned_group_ids = ticket.assigned_groups or []

            if assigned_group_ids:
                group_user_ids = UsersGroup.objects.filter(
                    id__in=assigned_group_ids
                ).values_list('users__id', flat=True).distinct()

                if userid in group_user_ids:
                    is_involved = True

            # Final permission check
            if not is_involved and not request.user.is_staff:
                return Response(
                    {"error": "You do not have permission to view messages for this ticket."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Return ALL messages for this ticket (not just between user and assignee)
            queryset = Message.objects.filter(
                ticket_no=ticket
            ).order_by('createdon')

            serializer = MessageSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
    def post(self, request, userid):
        data = request.data.copy()
        data['userid'] = userid  # Enforce from URL
        # parent optional—serializer handles
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminTicketMessagesView(APIView):
    """
    Dedicated endpoint for Admins/Staff to view ALL messages of a specific ticket.
    URL: GET /api/admin/ticket-messages/<int:ticket_no>/
    Only accessible to authenticated staff/admin users.
    Returns all messages for the ticket, ordered chronologically.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_no):
        # Restrict to staff/admin only
        if not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to view ticket messages."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify ticket exists (optional but good practice)
        ticket = get_object_or_404(CreateTicket, pk=ticket_no)

        # Get ALL messages for this ticket — no sender/receiver filtering
        messages = Message.objects.filter(ticket_no=ticket).order_by('createdon')

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response({
            "ticket_no": ticket_no,
            "ticket_title": ticket.title,
            "messages_count": messages.count(),
            "messages": serializer.data
        }, status=status.HTTP_200_OK)

class PlatformAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        entity_id = request.query_params.get('entity_id')
        qs = TicketsMasterConfiguration.objects.filter(field_type='Platform')

        if entity_id:
            try:
                entity_id = int(entity_id)
                qs = qs.filter(entity_ids__contains=[entity_id])
            except ValueError:
                return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)

        data = PlatformSerializer(qs, many=True).data
        return Response(data)

    def post(self, request):
        data = request.data.copy()
        data["created_by"] = request.user.firstname if request.user.is_authenticated else "system"
        data["updated_by"] = data["created_by"]

        serializer = PlatformSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            platform = TicketsMasterConfiguration.objects.get(pk=pk, field_type='Platform')
        except TicketsMasterConfiguration.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data["updated_by"] = request.user.firstname if request.user.is_authenticated else "system"

        serializer = PlatformSerializer(platform, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TicketSLAsWithNestedView(APIView):
    """
    Separate API: GET /api/tickets/slas-nested/
    Fetches SLAs for entity_id, grouped by category (category_name shown only once).
    Response: List of categories (with category_name once), each with subcategories and nested SLAs (no repetition).
    """
    permission_classes = [AllowAny]
 
    def get(self, request, *args, **kwargs):
        entity_id = request.query_params.get("entity_id")
        if not entity_id:
            return Response({"error": "entity_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            entity_id = int(entity_id)
            entity = Entity.objects.get(id=entity_id)
        except (ValueError, Entity.DoesNotExist):
            return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
 
        # Fetch unique categories from SLAs for this entity (to avoid repetition)
        # Use JSONField lookup for entity_ids containing the entity_id
        slas = TicketSLA.objects.filter(
            entity_ids__contains=[entity_id]
        ).select_related('category').order_by('category_id', '-id')
        categories = set(sla.category for sla in slas if sla.category)  # Unique categories
 
        response_data = []
 
        for category in categories:
            # Full category data (category_name shown only once)
            cat_serializer = TicketCategorySerializer(category)
            category_data = cat_serializer.data
            category_data['entity_name'] = entity.name
 
            # Fetch subcategories for this category
            subcategories = TicketSubcategory.objects.filter(category=category).order_by('subcategory_name')
            subcats_data = []
 
            for subcat in subcategories:
                # Fetch SLAs for this subcategory
                # Use JSONField lookups for entity_ids and subcategory_ids
                subcategory_slas = TicketSLA.objects.filter(
                    entity_ids__contains=[entity_id],
                    category=category,
                    subcategory_ids__contains=[subcat.id]
                ).order_by('-id')
 
                # Full subcategory data
                subcat_serializer = TicketSubcategorySerializer(subcat)
                subcat_data = subcat_serializer.data
 
                # Nest SLAs under subcategory (multiple if exist, no repetition)
                slas_list = []
                for sub_sla in subcategory_slas:
                    sla_serializer = TicketSLASerializer(sub_sla)
                    slas_list.append(sla_serializer.data)
 
                subcat_data['slas'] = slas_list  # List of SLAs (empty if none)
 
                subcats_data.append(subcat_data)
 
            # Attach subcategories to category (no repeat of category_name)
            category_data['subcategories'] = subcats_data
 
            response_data.append(category_data)
 
        return Response(response_data, status=status.HTTP_200_OK)
class TicketSubcategoryRetrieveUpdateView(APIView):
    # permission_classes = [IsAuthenticated]  # Requires authentication for all operations
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return TicketSubcategory.objects.get(pk=pk)
        except TicketSubcategory.DoesNotExist:
            return None
 
    def get(self, request, pk, *args, **kwargs):
        # GET single ticket subcategory
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSubcategorySerializer(instance)
        return Response(serializer.data)
 
    def put(self, request, pk, *args, **kwargs):
        # PUT update ticket subcategory
        instance = self.get_object(pk)
        if not instance:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TicketSubcategorySerializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save(
                updated_date=timezone.now(),
                updated_by=request.user.username if request.user.is_authenticated else None
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
 
 
 
def is_privileged(user):
    return getattr(user, "is_superuser", False) or getattr(user, "is_staff", False) or getattr(user, "is_hod", False)
 
 
# class TicketSLAsWithNestedView(APIView):
#     """
#     Separate API: GET /api/tickets/slas-nested/
#     Fetches SLAs for entity_id, grouped by category (category_name shown only once).
#     Response: List of categories (with category_name once), each with subcategories and nested SLAs (no repetition).
#     """
#     permission_classes = [AllowAny]
 
#     def get(self, request, *args, **kwargs):
#         entity_id = request.query_params.get("entity_id")
#         if not entity_id:
#             return Response({"error": "entity_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
#         try:
#             entity_id = int(entity_id)
#             entity = Entity.objects.get(id=entity_id)
#         except (ValueError, Entity.DoesNotExist):
#             return Response({"error": "Invalid entity_id"}, status=status.HTTP_400_BAD_REQUEST)
 
#         # Fetch unique categories from SLAs for this entity (to avoid repetition)
#         slas = TicketSLA.objects.filter(entity_id=entity_id).select_related('category').order_by('category_id', '-id')
#         categories = set(sla.category for sla in slas if sla.category)  # Unique categories
 
#         response_data = []
 
#         for category in categories:
#             # Full category data (category_name shown only once)
#             cat_serializer = TicketCategorySerializer(category)
#             category_data = cat_serializer.data
#             category_data['entity_name'] = entity.name
 
#             # Fetch subcategories for this category
#             subcategories = TicketSubcategory.objects.filter(category=category).order_by('subcategory_name')
#             subcats_data = []
 
#             for subcat in subcategories:
#                 # Fetch SLAs for this subcategory
#                 subcategory_slas = TicketSLA.objects.filter(
#                     entity_id=entity_id,
#                     category=category,
#                     subcategory=subcat
#                 ).order_by('-id')
 
#                 # Full subcategory data
#                 subcat_serializer = TicketSubcategorySerializer(subcat)
#                 subcat_data = subcat_serializer.data
 
#                 # Nest SLAs under subcategory (multiple if exist, no repetition)
#                 slas_list = []
#                 for sub_sla in subcategory_slas:
#                     sla_serializer = TicketSLASerializer(sub_sla)
#                     slas_list.append(sla_serializer.data)
 
#                 subcat_data['slas'] = slas_list  # List of SLAs (empty if none)
 
#                 subcats_data.append(subcat_data)
 
#             # Attach subcategories to category (no repeat of category_name)
#             category_data['subcategories'] = subcats_data
 
#             response_data.append(category_data)
 
#         return Response(response_data, status=status.HTTP_200_OK)