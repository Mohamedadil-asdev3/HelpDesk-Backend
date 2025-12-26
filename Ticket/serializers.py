
from rest_framework import serializers
from .models import *
from Ticket.models import Holiday
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
import base64 
from cryptography.fernet import Fernet
from Authenticate.models import User,UsersGroup
import logging

SECRET_KEY = getattr(settings, 'ENCRYPTION_SECRET', b'default_secret_key_change_me_32_bytes_long!!')

logger = logging.getLogger(__name__)
User = get_user_model()

# class TicketsMasterConfigurationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TicketsMasterConfiguration
#         fields = [
#             'id', 'field_type', 'referrence_to', 'field_name', 'field_values',
#             'is_mandatory', 'is_active', 'created_date', 'created_by',
#             'updated_by', 'updated_date', 'entity_id'
#         ]
#         read_only_fields = ['id']
class TicketsMasterConfigurationSerializer(serializers.ModelSerializer):
    # Map entity_ids as list of integers
    entity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        write_only=True  # Only for input; output via entity_names
    )
    # Add entity_names field for output
    entity_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketsMasterConfiguration
        fields = [
            'id', 'field_type', 'referrence_to', 'field_name', 'field_values',
            'is_mandatory', 'is_active', 'created_date', 'created_by',
            'updated_by', 'updated_date', 'entity_ids', 'entity_names'  # <-- Updated for multi-entity support
        ]
        read_only_fields = ['id', 'entity_names']  # entity_names is computed, so read-only

    def get_entity_names(self, obj):
        # Return list of entity names or ["No Entity"] if not set
        return obj.entity_names


# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=False)
#     entity_name = serializers.SerializerMethodField()
#     location_name = serializers.SerializerMethodField()
#     department_name = serializers.SerializerMethodField()
#     locations_id = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
#         source='locations',
#         allow_null=True,
#         required=False
#     )

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "name",
#             "firstname",
#             "realname",
#             "email",
#             "entities_id",
#             "entity_name",
#             "locations_id",
#             "location_name",
#             "department_id",
#             "department_name",
#             "is_hod",
#             "is_active",
#             "password",
#         ]

#     def get_entity_name(self, obj):
#         try:
#             return obj.entities_id.name if obj.entities_id else None
#         except Entity.DoesNotExist:
#             return None

#     def get_location_name(self, obj):
#         try:
#             return obj.locations.field_name if obj.locations else None
#         except TicketsMasterConfiguration.DoesNotExist:
#             return None

#     def get_department_name(self, obj):
#         try:
#             return obj.department_id.field_name if obj.department_id else None
#         except TicketsMasterConfiguration.DoesNotExist:
#             return None

#     # -----------------------
#     # Custom getters for names
#     # -----------------------
#     # def get_entity_name(self, obj):
#     #     """Return Entity name from Entity table"""
#     #     if obj.entities_id:
#     #         entity = Entity.objects.filter(id=obj.entities_id).first()
#     #         return entity.name if entity else None
#     #     return None

#     # def get_location_name(self, obj):
#     #     """Return Location name from TicketsMasterConfiguration where field_type='Location'"""
#     #     if obj.locations_id:
#     #         location = TicketsMasterConfiguration.objects.filter(
#     #             id=obj.locations_id, field_type="Location"
#     #         ).first()
#     #         return location.field_name if location else None
#     #     return None

#     # def get_department_name(self, obj):
#     #     """Return Department name from TicketsMasterConfiguration where field_type='Department'"""
#     #     if obj.department_id:
#     #         dept = TicketsMasterConfiguration.objects.filter(
#     #             id=obj.department_id, field_type="Department"
#     #         ).first()
#     #         return dept.field_name if dept else None
#     #     return None

#     # -----------------------
#     # Create / Update methods
#     # # -----------------------
#     # def create(self, validated_data):
#     #     password = validated_data.pop("password", None)
#     #     user = User(**validated_data)
#     #     if password:
#     #         user.password = make_password(password)
#     #     user.save()
#     #     return user

#     # def update(self, instance, validated_data):
#     #     password = validated_data.pop("password", None)
#     #     for attr, value in validated_data.items():
#     #         setattr(instance, attr, value)
#     #     if password:
#     #         instance.password = make_password(password)
#     #     instance.save()
#     #     return instance
# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=False)
#     entity_name = serializers.SerializerMethodField()
#     location_name = serializers.SerializerMethodField()
#     department_name = serializers.SerializerMethodField()
#     role_name = serializers.SerializerMethodField()
#     locations_id = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
#         source='locations',
#         allow_null=True,
#         required=False
#     )
#     roles_id = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Role'),
#         allow_null=True,
#         required=False
#     )

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "name",
#             "firstname",
#             "realname",
#             "email",
#             "entities_id",
#             "entity_name",
#             "locations_id",
#             "location_name",
#             "department_id",
#             "department_name",
#             "roles_id",
#             "role_name",
#             "is_hod",
#             "is_active",
#             "password",
#         ]

#     def get_entity_name(self, obj):
#         try:
#             return obj.entities_id.name if obj.entities_id else None
#         except Entity.DoesNotExist:
#             return None

#     def get_location_name(self, obj):
#         try:
#             return obj.locations.field_name if obj.locations else None
#         except TicketsMasterConfiguration.DoesNotExist:
#             return None

#     def get_department_name(self, obj):
#         try:
#             return obj.department_id.field_name if obj.department_id else None
#         except TicketsMasterConfiguration.DoesNotExist:
#             return None

#     def get_role_name(self, obj):
#         try:
#             return obj.roles_id.field_name if obj.roles_id else None
#         except TicketsMasterConfiguration.DoesNotExist:
#             return None
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    entities_names = serializers.SerializerMethodField()  # Changed to plural for multiple entities
    location_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()  # Already plural for multiple roles
    # Define fields for input (arrays of IDs)
    entities_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        required=False
    )
    # locations = serializers.PrimaryKeyRelatedField(
    #     queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
    #     allow_null=True,
    #     required=False
    # )
    locations_id = serializers.PrimaryKeyRelatedField(
    source='locations',  # ← maps to the actual model field "locations"
    queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
    allow_null=True,
    required=False
)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'),
        allow_null=True,
        required=False
    )
    roles_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "firstname",
            "realname",
            "email",
            "entities_ids",
            "entities_names",
            "locations_id",
            # "locations",
            "location_name",
            "department_id",
            "department_name",
            "roles_ids",
            "role_names",
            "is_hod",
            "is_active",
            "password",
        ]

    def get_entities_names(self, obj):
        if obj.entities_ids:
            entities = Entity.objects.filter(id__in=obj.entities_ids)
            return [entity.name for entity in entities]
        return []

    def get_location_name(self, obj):
        try:
            return obj.locations.field_name if obj.locations else None
        except TicketsMasterConfiguration.DoesNotExist:
            return None

    def get_department_name(self, obj):
        try:
            return obj.department_id.field_name if obj.department_id else None
        except TicketsMasterConfiguration.DoesNotExist:
            return None

    def get_role_names(self, obj):
        if obj.roles_ids:
            roles = TicketsMasterConfiguration.objects.filter(id__in=obj.roles_ids, field_type='Role')
            return [role.field_name for role in roles]
        return []

    def create(self, validated_data):
        # Handle password hashing (assuming UserManager has create_user with hashing)
        password = validated_data.pop('password', None)
        # Pop array fields
        entities_ids = validated_data.pop('entities_ids', [])
        roles_ids = validated_data.pop('roles_ids', [])
        user = User.objects.create_user(**validated_data, password=password, entities_ids=entities_ids, roles_ids=roles_ids)
        return user

    def update(self, instance, validated_data):
        # Handle password update if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            instance.password_last_update = timezone.now()  # Update last password change
        # Handle array fields
        entities_ids = validated_data.pop('entities_ids', None)
        if entities_ids is not None:
            instance.entities_ids = entities_ids
        roles_ids = validated_data.pop('roles_ids', None)
        if roles_ids is not None:
            instance.roles_ids = roles_ids
        return super().update(instance, validated_data)

# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Role
#         fields = [
#             'id', 'rolename', 'code', 'created_date', 'created_by',
#             'updated_date', 'updated_by', 'is_active'
#         ]
#         read_only_fields = ['id', 'created_date', 'created_by', 'updated_date', 'updated_by']  # Added 'updated_by'
#         extra_kwargs = {
#             'created_by': {'required': False},
#             'updated_by': {'required': False},
#             'created_date': {'required': False},
#             'updated_date': {'required': False},
#         }
# class EntitySerializer(serializers.ModelSerializer):
#     location = TicketsMasterConfigurationSerializer(read_only=True)
#     location_id = serializers.PrimaryKeyRelatedField(queryset=TicketsMasterConfiguration.objects.all(),
#         source='location',  # map this field to model's location FK
#         write_only=True)
#     class Meta:
#         model = Entity
#         fields = [
#             'id', 'name', 'description', 'display_name', 'address', 'logo',
#             'contact_email', 'location', 'created_date', 'created_by',
#             'updated_date', 'updated_by','location_id'
#         ]
#         read_only_fields = ['id', 'created_date', 'created_by', 'updated_date', 'updated_by']
#         # def to_representation(self, instance):
#         #     data = super().to_representation(instance)
#         #     data['location_data'] = TicketsMasterConfiguration.objects.filter(
#         #         field_type="Location",
#         #         entity_id=instance.id,
#         #     ).annotate(entity_name=F('entity__name')).values(
#         #         "id",
#         #         "entity_id",
#         #         "entity_name",
#         #         "referrence_to",
#         #         "field_name",
#         #         "field_values",
#         #         "is_mandatory",
#         #         "is_active"
#         #     )

#         #     return instance

#         def validate_logo(self, value):
#             max_size = 5 * 1024 * 1024  # 5 MB
#             if value and value.size > max_size:
#                 raise serializers.ValidationError("Logo size should not exceed 5 MB.")
#             return value

# class DepartmentSerializer(serializers.ModelSerializer):
#     # Map entity_id directly to the model's entity_id field
#     entity_id = serializers.IntegerField()

#     class Meta:
#         model = TicketsMasterConfiguration
#         fields = [
#             "id",
#             "entity_id",
#             "field_type",
#             # "referrence_to",
#             "field_name",
#             "field_values",
#             "is_mandatory",
#             "is_active",
#             "created_by",
#             "updated_by",
#             "created_date",
#             "updated_date",
#         ]

#     def create(self, validated_data):
#         # Ensure field_type is always 'Department' when creating
#         validated_data["field_type"] = "Department"
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         # Prevent changing field_type accidentally
#         validated_data["field_type"] = "Department"
#         return super().update(instance, validated_data)
class DepartmentSerializer(serializers.ModelSerializer):
    # Map entity_ids as list of integers
    entity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        write_only=True  # Only for input; output via entity_names
    )
    # Add entity_names field for output
    entity_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketsMasterConfiguration
        fields = [
            "id",
            "entity_ids",  # <-- Array field for input (set entities)
            "entity_names",  # <-- Array of names for output
            "field_type",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def get_entity_names(self, obj):
        # Return list of entity names or ["No Entity"] if not set
        return obj.entity_names

    def create(self, validated_data):
        # Ensure field_type is always 'Department' when creating
        validated_data["field_type"] = "Department"
        # entity_ids is handled directly by JSONField; no pop needed
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing field_type accidentally
        validated_data["field_type"] = "Department"
        # entity_ids is handled directly by JSONField; no pop needed
        return super().update(instance, validated_data)
# class DepartmentSerializer(serializers.ModelSerializer):
#     # Map entity_id directly to the model's entity_id field
#     entity_id = serializers.IntegerField()
#     # Add entity_name field
#     entity_name = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = TicketsMasterConfiguration
#         fields = [
#             "id",
#             "entity_id",
#             "entity_name",  # <-- Added entity name
#             "field_type",
#             "field_name",
#             "field_values",
#             "is_mandatory",
#             "is_active",
#             "created_by",
#             "updated_by",
#             "created_date",
#             "updated_date",
#         ]

#     def get_entity_name(self, obj):
#         # Return entity name or "No Entity" if not set
#         return obj.entity.name if obj.entity else "No Entity"

#     def create(self, validated_data):
#         # Ensure field_type is always 'Department' when creating
#         validated_data["field_type"] = "Department"
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         # Prevent changing field_type accidentally
#         validated_data["field_type"] = "Department"
#         return super().update(instance, validated_data)
# class GlpiUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GlpiUser
#         fields = ['id', 'realname', 'firstname', 'lastname', 'entities_id'] 


# class RoleSerializer(serializers.ModelSerializer):
#     """
#     Serializer for Role configuration in TicketsMasterConfiguration.
#     Assumes the model has fields like id, name, description, entity_id, etc.
#     Customize fields as per your model schema.
#     """
#     entity_id = serializers.IntegerField()
#     # Add entity_name field
#     entity_name = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = TicketsMasterConfiguration
#         fields = [
#             "id",
#             "entity_id",
#             "entity_name",  # <-- Added entity name
#             "field_type",
#             "field_name",
#             "field_values",
#             "is_mandatory",
#             "is_active",
#             "created_by",
#             "updated_by",
#             "created_date",
#             "updated_date",
#         ]
#     def get_entity_name(self, obj):
#         # Return entity name or "No Entity" if not set
#         return obj.entity.name if obj.entity else "No Entity"

#     def create(self, validated_data):
#         # Ensure field_type is always 'Role' when creating
#         validated_data["field_type"] = "Role"
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         # Prevent changing field_type accidentally
#         validated_data["field_type"] = "Role"
#         return super().update(instance, validated_data)    
class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role configuration in TicketsMasterConfiguration.
    Assumes the model has fields like id, name, description, entity_id, etc.
    Customize fields as per your model schema.
    """
    # Map entity_ids as list of integers
    entity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        write_only=True  # Only for input; output via entity_names
    )
    # Add entity_names field for output
    entity_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketsMasterConfiguration
        fields = [
            "id",
            "entity_ids",  # <-- Array field for input (set entities)
            "entity_names",  # <-- Array of names for output
            "field_type",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def get_entity_names(self, obj):
        # Return list of entity names or ["No Entity"] if not set
        return obj.entity_names

    def create(self, validated_data):
        # Ensure field_type is always 'Role' when creating
        validated_data["field_type"] = "Role"
        # entity_ids is handled directly by JSONField; no pop needed
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing field_type accidentally
        validated_data["field_type"] = "Role"
        # entity_ids is handled directly by JSONField; no pop needed
        return super().update(instance, validated_data)   
    

class TicketSubcategorySerializer(serializers.ModelSerializer):
    entity_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    entity_names = serializers.SerializerMethodField()
 
    class Meta:
        model = TicketSubcategory
        fields = [
            'id', 'entity_ids', 'entity_names', 'category_id', 'subcategory_name',
            'subcategory_description', 'is_active',
            'created_date', 'created_by', 'updated_by', 'updated_date'
        ]
 
    def get_entity_names(self, obj):
        if not obj.entity_ids:
            return []
        entities = Entity.objects.filter(id__in=obj.entity_ids)
        return [e.name for e in entities]
 
    def to_internal_value(self, data):
        if 'entity_ids' in data:
            data['entity_ids'] = sorted(data['entity_ids']) if isinstance(data['entity_ids'], list) else []
        return super().to_internal_value(data)
 
class TicketSLASerializer(serializers.ModelSerializer):
    assigned_user_detail = serializers.SerializerMethodField()
    assigned_group_detail = serializers.SerializerMethodField()
 
    class Meta:
        model = TicketSLA
        fields = [
             'confidential', 
            'assigned_user_id', 'assigned_group_id', 'assigned_user_detail', 'assigned_group_detail',
            'Approver_level1_user_id', 'Approver_level1_time',
            'Approver_level2_user_id', 'Approver_level2_time',
            'Approver_level3_user_id', 'Approver_level3_time',
            'Approver_level4_user_id', 'Approver_level4_time',
            'Approver_level5_user_id', 'Approver_level5_time',
            'is_active'
        ]
 
    def get_assigned_user_detail(self, obj):
        if obj.assigned_user_id:
            try:
                user = User.objects.get(id=obj.assigned_user_id)
                return {'id': user.id, 'name': f"{user.firstname}".strip(),'email': user.email}
            except User.DoesNotExist:
                pass
        return None
 
    def get_assigned_group_detail(self, obj):
        if obj.assigned_group_id:
            try:
                group = UsersGroup.objects.get(id=obj.assigned_group_id)
                return {'id': group.id, 'name': group.name,}
            except UsersGroup.DoesNotExist:
                pass
        return None
 
class TicketCategorySerializer(serializers.ModelSerializer):
    entity_ids = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    entity_names = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.field_name', read_only=True)  # Adjusted if department has field_name
 
    # Nested subcategories - Fixed to correct reverse relation source
    subcategories = serializers.SerializerMethodField(read_only=True)  # Use method to ensure all subcategories are fetched
 
    # SLA for assigned_to (shows user/group details)
    sla = serializers.SerializerMethodField(read_only=True)
 
    # Confidential field (direct from model)
    confidential = serializers.CharField(read_only=True)
 
    class Meta:
        model = TicketCategory
        fields = [
            'id', 'entity_ids', 'entity_names', 'department_id', 'department_name',
            'category_name', 'category_description', 'is_active', 'confidential',
            'created_date', 'created_by', 'updated_by', 'updated_date',
            'subcategories', 'sla'  # Added for frontend display
        ]
        extra_kwargs = {
            'department_id': {'required': False, 'allow_null': True},
            'category_name': {'required': False, 'allow_blank': True},
            'category_description': {'required': False, 'allow_blank': True},
            'created_date': {'required': False, 'allow_null': True},
            'created_by': {'required': False, 'allow_null': True},
            'updated_date': {'required': False, 'allow_null': True},
            'updated_by': {'required': False, 'allow_null': True},
        }
 
    def get_entity_names(self, obj):
        if not obj.entity_ids:
            return []
        entities = Entity.objects.filter(id__in=obj.entity_ids)
        return [e.name for e in entities]  # Assume 'name' field on Entity
 
    def get_subcategories(self, obj):
        # Explicitly fetch all subcategories for this category (no filter on entity_ids for list view)
        subcats = TicketSubcategory.objects.filter(category=obj, is_active='Y').order_by('subcategory_name')
        return TicketSubcategorySerializer(subcats, many=True).data
 
    def get_sla(self, obj):
        # Get the active SLA for this category (first match; refine with entity_ids if multi-entity)
        try:
            # Optional: Filter by entity_ids if needed: entity_ids=obj.entity_ids
            sla = TicketSLA.objects.filter(category=obj, is_active='Y').first()
            if sla:
                return TicketSLASerializer(sla).data
        except TicketSLA.DoesNotExist:
            pass
        return None  # Returns empty or null for no SLA
 
    def to_internal_value(self, data):
        if 'entity_ids' in data:
            data['entity_ids'] = sorted(data['entity_ids']) if isinstance(data['entity_ids'], list) else []
        return super().to_internal_value(data)
 
 
 
 
# class EntitySerializer(serializers.ModelSerializer):
#     location = TicketsMasterConfigurationSerializer(read_only=True)
#     location_id = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.all(),
#         source='location',
#         write_only=True
#     )

#     class Meta:
#         model = Entity
#         fields = [
#             'id', 'name', 'description', 'display_name', 'address', 'logo',
#             'contact_email', 'location', 'location_id',
#             'created_date', 'created_by',
#             'updated_date', 'updated_by'
#         ]
#         read_only_fields = ['id', 'created_date', 'created_by', 'updated_date', 'updated_by']

#     def to_representation(self, instance):
#         data = super().to_representation(instance)

#         # ---------------------------
#         # ADDING ROLE CONFIGURATION
#         # ---------------------------
#         role_configs = TicketsMasterConfiguration.objects.filter(
#             field_type="Role",
#             entity_id=instance.id,
#         ).values(
#             'id',
#             'entity_id',
#             'field_type',
#             'field_name',
#             'field_values',
#             'is_mandatory',
#             'is_active',
#         )

#         data['roles'] = role_configs   # ⬅ added

#         return data

#     def validate_logo(self, value):
#         max_size = 5 * 1024 * 1024  # 5 MB
#         if value and value.size > max_size:
#             raise serializers.ValidationError("Logo size should not exceed 5 MB.")
#         return value
class EntitySerializer(serializers.ModelSerializer):
    location = TicketsMasterConfigurationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.all(),
        source='location',
        write_only=True
    )

    class Meta:
        model = Entity
        fields = [
            'id', 'name', 'description', 'display_name', 'address', 'logo',
            'contact_email', 'location', 'location_id',
            'created_date', 'created_by',
            'updated_date', 'updated_by'
        ]
        read_only_fields = ['id', 'created_date', 'created_by', 'updated_date', 'updated_by']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # ---------------------------
        # ADDING ROLE CONFIGURATION
        # ---------------------------
        role_configs = TicketsMasterConfiguration.objects.filter(
            field_type="Role",
            entity_ids__contains=[instance.id],
        ).values(
            'id',
            'entity_ids',  # <-- Changed from 'entity_id' to 'entity_ids'
            'field_type',
            'field_name',
            'field_values',
            'is_mandatory',
            'is_active',
        )

        # Post-process to add entity_names for each role config
        for config in role_configs:
            config['entity_names'] = self.get_entity_names(config['entity_ids'])

        data['roles'] = list(role_configs)  # ⬅ added and converted to list for JSON serialization

        return data

    def get_entity_names(self, entity_ids):
        """
        Helper to fetch entity names from entity_ids list
        """
        if not entity_ids:
            return ["No Entity"]
        entities = Entity.objects.filter(id__in=entity_ids)
        return [entity.name for entity in entities if entity.name]

    def validate_logo(self, value):
        max_size = 5 * 1024 * 1024  # 5 MB
        if value and value.size > max_size:
            raise serializers.ValidationError("Logo size should not exceed 5 MB.")
        return value

# class TicketCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TicketCategory
#         fields = ['id', 'entity_id','department_id', 'category_name', 'category_description', 
#                  'is_active', 'created_date', 'created_by', 'updated_by', 'updated_date']
        
#         # Make these fields optional for POST/PUT requests
#         # extra_kwargs = {
#         #     'created_date': {'required': False, 'allow_null': True},
#         #     'created_by': {'required': False, 'allow_null': True},
#         #     'updated_date': {'required': False, 'allow_null': True},
#         #     'updated_by': {'required': False, 'allow_null': True}
#         # }
#         extra_kwargs = {
#             'department_id': {'required': False, 'allow_null': True},
#             'category_name': {'required': False, 'allow_blank': True},
#             'category_description': {'required': False, 'allow_blank': True},
#             'created_date': {'required': False, 'allow_null': True},
#             'created_by': {'required': False, 'allow_null': True},
#             'updated_date': {'required': False, 'allow_null': True},
#             'updated_by': {'required': False, 'allow_null': True},
#         }
# class TicketSubcategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TicketSubcategory
#         fields = [
#             'id', 'entity_id', 'category_id', 'subcategory_name', 
#             'subcategory_description', 'is_active', 
#             'created_date', 'created_by', 'updated_by', 'updated_date'
#         ]

# Category serializer with nested subcategories
# class TicketCategorySerializer(serializers.ModelSerializer):
#     # Add read-only fields for names based on foreign keys
#     entity_name = serializers.CharField(source='entity.name', read_only=True)
#     department_name = serializers.CharField(source='department.name', read_only=True)

#     # Nested subcategories
#     subcategories = TicketSubcategorySerializer(many=True, read_only=True, source='ticketsubcategory_set')

#     class Meta:
#         model = TicketCategory
#         fields = [
#             'id', 'entity_id', 'entity_name', 'department_id', 'department_name', 
#             'category_name', 'category_description', 'is_active', 
#             'created_date', 'created_by', 'updated_by', 'updated_date',
#             'subcategories',  # Include nested subcategories
#         ]
#         extra_kwargs = {
#             'department_id': {'required': False, 'allow_null': True},
#             'category_name': {'required': False, 'allow_blank': True},
#             'category_description': {'required': False, 'allow_blank': True},
#             'created_date': {'required': False, 'allow_null': True},
#             'created_by': {'required': False, 'allow_null': True},
#             'updated_date': {'required': False, 'allow_null': True},
#             'updated_by': {'required': False, 'allow_null': True},
#         }

class TicketDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = TicketDocument
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
# from rest_framework import serializers
# from django.db import transaction
# from .models import CreateTicket, TicketSLA, TicketDocument, TicketsMasterConfiguration, TicketCategory, TicketSubcategory
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class CreateTicketSerializer(serializers.ModelSerializer):
#     # Write-only PKs
#     type = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='TicketType'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     location = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     priority = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Priority'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
    
#     # Category/Subcategory IDs
#     category = serializers.PrimaryKeyRelatedField(
#         queryset=TicketCategory.objects.all(),
#         write_only=True,
#         required=True
#     )
#     subcategory = serializers.PrimaryKeyRelatedField(
#         queryset=TicketSubcategory.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )

#     # Assignment fields
#     assigned_to_type = serializers.ChoiceField(
#         choices=[('user', 'User'), ('group', 'Group')], 
#         write_only=True, 
#         required=False
#     )
#     assignee = serializers.CharField(write_only=True, required=False, allow_null=True)
#     assigned_group = serializers.PrimaryKeyRelatedField(
#         queryset=UsersGroup.objects.all(), 
#         write_only=True, 
#         required=False,
#         allow_null=True
#     )

#     # Read-only details
#     type_detail = serializers.SerializerMethodField(read_only=True)
#     department_detail = serializers.SerializerMethodField(read_only=True)
#     location_detail = serializers.SerializerMethodField(read_only=True)
#     priority_detail = serializers.SerializerMethodField(read_only=True)
#     category_detail = serializers.SerializerMethodField(read_only=True)
#     subcategory_detail = serializers.SerializerMethodField(read_only=True)
#     requested_detail = serializers.SerializerMethodField(read_only=True)
#     assignee_detail = serializers.SerializerMethodField(read_only=True)
#     assigned_group_detail = serializers.SerializerMethodField(read_only=True)
#     status_detail = serializers.SerializerMethodField(read_only=True)
    
#     # Documents field - Don't import TicketDocumentSerializer here if it causes circular import
#     # Instead, handle it inline
#     documents = serializers.SerializerMethodField(read_only=True)
    
#     # Watchers field
#     watchers = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         many=True,
#         required=False,
#         write_only=True
#     )

#     class Meta:
#         model = CreateTicket
#         fields = [
#             'id', 'ticket_no', 'title', 'description', 
#             'type', 'type_detail', 
#             'department', 'department_detail',
#             'location', 'location_detail', 
#             'priority', 'priority_detail',
#             'category', 'category_detail',
#             'subcategory', 'subcategory_detail',
#             'assigned_to_type', 'assignee', 'assignee_detail',
#             'assigned_group', 'assigned_group_detail',
#             'requested', 'requested_detail', 'watchers',
#             'documents', 'status', 'status_detail',
#             'sla', 'created_date', 'updated_date', 'closed_on'
#         ]
#         read_only_fields = ['id', 'ticket_no', 'created_date', 'updated_date', 'closed_on', 'status', 'sla']

#     def get_documents(self, obj):
#         """Get documents related to the ticket"""
#         try:
#             documents = TicketDocument.objects.filter(ticket=obj)
#             return [
#                 {
#                     'id': doc.id,
#                     'file': doc.file.url if doc.file else None,
#                     '': doc.original_name,
#                 }
#                 for doc in documents
#             ]
#         except Exception:
#             return []

#     def get_type_detail(self, obj):
#         if obj.type:
#             return {'id': obj.type.id, 'field_name': obj.type.field_name}
#         return None

#     def get_department_detail(self, obj):
#         if obj.department:
#             return {'id': obj.department.id, 'field_name': obj.department.field_name}
#         return None

#     def get_location_detail(self, obj):
#         if obj.location:
#             return {'id': obj.location.id, 'field_name': obj.location.field_name}
#         return None

#     def get_priority_detail(self, obj):
#         if obj.priority:
#             return {'id': obj.priority.id, 'field_name': obj.priority.field_name}
#         return None

#     def get_category_detail(self, obj):
#         if obj.category:
#             return {'id': obj.category.id, 'category_name': obj.category.category_name}
#         return None

#     def get_subcategory_detail(self, obj):
#         if obj.subcategory:
#             return {'id': obj.subcategory.id, 'subcategory_name': obj.subcategory.subcategory_name}
#         return None

#     def get_requested_detail(self, obj):
#         if obj.requested:
#             return {
#                 'id': obj.requested.id,
#                 'email': obj.requested.email,
#                 'name': getattr(obj.requested, 'name', None) or 
#                        getattr(obj.requested, 'first_name', None) or 
#                        obj.requested.email
#             }
#         return None

#     def get_status_detail(self, obj):
#         if obj.status:
#             return {'id': obj.status.id, 'field_name': obj.status.field_name}
#         return None

#     def get_assignee_detail(self, obj):
#         assignee_str = getattr(obj, 'assignee', '')
#         if assignee_str and not assignee_str.startswith('group:'):
#             try:
#                 user = User.objects.get(email=assignee_str)
#                 name = getattr(user, 'name', None) or getattr(user, 'first_name', None) or assignee_str
#                 return {"id": user.id, "name": name, "email": assignee_str}
#             except User.DoesNotExist:
#                 return {"email": assignee_str}
#         return None

#     def get_assigned_group_detail(self, obj):
#         # If ticket has an assigned_group ForeignKey, use it
#         if obj.assigned_group:
#             try:
#                 users = obj.assigned_group.get_users()
#                 members_count = users.count()
#                 return {
#                     "id": obj.assigned_group.id, 
#                     "name": obj.assigned_group.name, 
#                     "members_count": members_count
#                 }
#             except Exception:
#                 return {"id": obj.assigned_group.id, "name": obj.assigned_group.name}
        
#         # Fallback: check assignee field for group pattern
#         assignee_str = getattr(obj, 'assignee', '')
#         if assignee_str and assignee_str.startswith('group:'):
#             group_name = assignee_str.replace('group:', '')
#             try:
#                 group = UsersGroup.objects.get(name=group_name)
#                 users = group.get_users()
#                 members_count = users.count()
#                 return {
#                     "id": group.id, 
#                     "name": group_name, 
#                     "members_count": members_count
#                 }
#             except UsersGroup.DoesNotExist:
#                 return {"name": group_name}
#         return None

#     def validate(self, data):
#         """Validate required fields"""
#         if 'category' not in data or not data['category']:
#             raise serializers.ValidationError({"category": "Category is required."})
        
#         assigned_to_type = data.get('assigned_to_type')
#         if assigned_to_type:
#             if assigned_to_type == 'user' and not data.get('assignee'):
#                 raise serializers.ValidationError({"assignee": "Email required for user assignment."})
#             if assigned_to_type == 'group' and not data.get('assigned_group'):
#                 raise serializers.ValidationError({"assigned_group": "Group required for group assignment."})
        
#         return data

#     def create(self, validated_data):
#         # Pop assignment-related fields
#         assigned_to_type = validated_data.pop('assigned_to_type', None)
#         assignee_email = validated_data.pop('assignee', None)
#         assigned_group = validated_data.pop('assigned_group', None)
        
#         # Pop watchers
#         watchers = validated_data.pop('watchers', [])
        
#         # Get "New" status - IMPORTANT: Set status to "New" instead of "Pending"
#         new_status = TicketsMasterConfiguration.objects.filter(
#             field_type='Status', 
#             field_name='New'  # Changed from 'pending' to 'New'
#         ).first()
        
#         if new_status:
#             validated_data['status'] = new_status
#         else:
#             # Fallback: try to get any active status
#             fallback_status = TicketsMasterConfiguration.objects.filter(
#                 field_type='Status',
#                 is_active='Y'
#             ).first()
#             if fallback_status:
#                 validated_data['status'] = fallback_status
        
#         # Set requester from request context
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             validated_data['requested'] = request.user

#         with transaction.atomic():
#             # Save assigned_group to the ticket (this will set assigned_group_id in DB)
#             if assigned_group:
#                 validated_data['assigned_group'] = assigned_group
            
#             # Create ticket instance
#             ticket = CreateTicket.objects.create(**validated_data)
            
#             # Handle assignment
#             if assigned_to_type == 'user' and assignee_email:
#                 ticket.assignee = assignee_email
#                 try:
#                     assignee_user = User.objects.get(email=assignee_email)
#                     ticket.watchers.add(assignee_user)
#                 except User.DoesNotExist:
#                     pass
                    
#             elif assigned_to_type == 'group' and assigned_group:
#                 # Set both assignee field and save the group object
#                 ticket.assignee = f"group:{assigned_group.name}"
#                 ticket.assigned_group = assigned_group  # This sets assigned_group_id
                
#                 # Add group members to watchers using the get_users() method
#                 try:
#                     group_users = assigned_group.get_users()
#                     for member in group_users:
#                         ticket.watchers.add(member)
#                 except Exception as e:
#                     print(f"Error adding group members to watchers: {e}")
#                     # Continue even if group members can't be added
            
#             # Add manual watchers
#             for watcher in watchers:
#                 ticket.watchers.add(watcher)
            
#             # Auto-assign from SLA if no assignment was made
#             if not assigned_to_type and ticket.category and ticket.subcategory:
#                 try:
#                     sla = TicketSLA.objects.filter(
#                         category=ticket.category,
#                         subcategory=ticket.subcategory,
#                         is_active='Y'
#                     ).first()
                    
#                     if sla and sla.Assign_to:
#                         ticket.assignee = sla.Assign_to
                        
#                         if sla.Assign_to.startswith('group:'):
#                             group_name = sla.Assign_to.replace('group:', '')
#                             try:
#                                 group = UsersGroup.objects.get(name=group_name)
#                                 ticket.assigned_group = group
#                                 # Add group members using get_users()
#                                 group_members = group.get_users()
#                                 for member in group_members:
#                                     ticket.watchers.add(member)
#                             except UsersGroup.DoesNotExist:
#                                 pass
#                         else:
#                             try:
#                                 user = User.objects.get(email=sla.Assign_to)
#                                 ticket.watchers.add(user)
#                             except User.DoesNotExist:
#                                 pass
#                 except TicketSLA.DoesNotExist:
#                     pass
            
#             ticket.save()
            
#             # Handle documents from request.FILES
#             request = self.context.get('request')
#             if request and request.FILES:
#                 for file in request.FILES.getlist('documents'):
#                     TicketDocument.objects.create(
#                         ticket=ticket,
#                         file=file,
#                         original_name=file.name
#                     )
            
#             return ticket

#     def update(self, instance, validated_data):
#         """Update ticket"""
#         with transaction.atomic():
#             # Update basic fields
#             for attr, value in validated_data.items():
#                 if attr not in ['assigned_to_type', 'assignee', 'assigned_group', 'watchers']:
#                     setattr(instance, attr, value)
            
#             # Handle assignment changes
#             assigned_to_type = validated_data.get('assigned_to_type')
#             assignee_email = validated_data.get('assignee')
#             assigned_group = validated_data.get('assigned_group')
            
#             if assigned_to_type == 'user' and assignee_email:
#                 instance.assignee = assignee_email
#                 instance.assigned_group = None  # Clear group assignment
#             elif assigned_to_type == 'group' and assigned_group:
#                 instance.assignee = f"group:{assigned_group.name}"
#                 instance.assigned_group = assigned_group
            
#             # Update watchers if provided
#             if 'watchers' in validated_data:
#                 instance.watchers.set(validated_data['watchers'])
            
#             instance.save()
#             return instance
from rest_framework import serializers
from django.db import transaction
from .models import (
    CreateTicket, TicketSLA, TicketDocument, TicketsMasterConfiguration, 
    TicketCategory, TicketSubcategory  # Added UsersGroup import
)
from Authenticate.models import UsersGroup
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)  # Define logger

# class UserSerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()  # Computed name field

#     class Meta:
#         model = User
#         fields = ['id', 'firstname', 'email', 'name']  # Include computed name

#     def get_name(self, obj):
#         """Compute full name"""
#         name = (getattr(obj, 'name', None) or
#                 getattr(obj, 'first_name', '') + ' ' + getattr(obj, 'last_name', '')).strip()
#         return name or obj.username or obj.email

import logging
from django.db import transaction
from rest_framework import serializers

logger = logging.getLogger(__name__)

# class CreateTicketSerializer(serializers.ModelSerializer):
#     # Write-only PKs (unchanged)
#     type = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='TicketType'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     location = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     platform = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Platform'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     priority = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Priority'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
    
#     # NEW: Status as writeable PK field (for updates)
#     status = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Status', is_active='Y'),
#         write_only=False,  # Allow read/write
#         required=False,
#         allow_null=True
#     )
    
#     # Category/Subcategory IDs (unchanged)
#     category = serializers.PrimaryKeyRelatedField(
#         queryset=TicketCategory.objects.all(),
#         write_only=True,
#         required=False,  # Make optional for updates
#         allow_null=True
#     )
#     subcategory = serializers.PrimaryKeyRelatedField(
#         queryset=TicketSubcategory.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )

#     # Assignment fields - Handle multiples via lists of IDs or emails (unchanged)
#     assigned_to_type = serializers.ListField(
#         child=serializers.ChoiceField(choices=[('user', 'User'), ('group', 'Group')]), 
#         write_only=True, 
#         required=False
#     )
#     assignee = serializers.ListField(  # Multiple user IDs or emails
#         child=serializers.CharField(), 
#         write_only=True, 
#         required=False
#     )
#     assigned_group = serializers.ListField(  # Multiple group IDs
#         child=serializers.IntegerField(), 
#         write_only=True, 
#         required=False
#     )

#     # Read-only details (unchanged)
#     type_detail = serializers.SerializerMethodField(read_only=True)
#     department_detail = serializers.SerializerMethodField(read_only=True)
#     location_detail = serializers.SerializerMethodField(read_only=True)
#     platform_detail = serializers.SerializerMethodField(read_only=True)
#     priority_detail = serializers.SerializerMethodField(read_only=True)
#     category_detail = serializers.SerializerMethodField(read_only=True)
#     subcategory_detail = serializers.SerializerMethodField(read_only=True)
#     requested_detail = serializers.SerializerMethodField(read_only=True)
#     assignees_detail = serializers.SerializerMethodField(read_only=True)
#     assigned_groups_detail = serializers.SerializerMethodField(read_only=True)
#     status_detail = serializers.SerializerMethodField(read_only=True)
    
#     # Documents field (unchanged)
#     documents = serializers.SerializerMethodField(read_only=True)
    
#     # Watchers field (unchanged)
#     watchers = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         many=True,
#         required=False,
#         write_only=True
#     )

#     # Title and description - required for create, optional for update (unchanged)
#     title = serializers.CharField(required=False, allow_blank=True)
#     description = serializers.CharField(required=False, allow_blank=True)

#     class Meta:
#         model = CreateTicket
#         fields = [
#             'id', 'ticket_no', 'title', 'description', 
#             'type', 'type_detail', 
#             'department', 'department_detail',
#             'location', 'location_detail', 
#             'platform', 'platform_detail',
#             'priority', 'priority_detail',
#             'category', 'category_detail',
#             'subcategory', 'subcategory_detail',
#             'status', 'status_detail',  # Now fully included
#             'assigned_to_type', 'assignee', 'assignees_detail',
#             'assigned_group', 'assigned_groups_detail',
#             'requested', 'requested_detail', 'watchers',
#             'documents', 'sla', 'created_date', 'updated_date', 'closed_on'
#         ]
#         read_only_fields = ['id', 'ticket_no', 'created_date', 'updated_date', 'closed_on', 'sla']  # Removed 'status'

#     def __init__(self, *args, **kwargs):
#         # Detect if this is an update (partial update)
#         self.partial = kwargs.pop('partial', False)
#         super().__init__(*args, **kwargs)
        
#         # For create, make required fields required (unchanged)
#         if not self.partial:
#             self.fields['title'].required = True
#             self.fields['description'].required = True
#             self.fields['category'].required = True
#             # NEW: For create, status is auto-set, so not required here

#     # All get_ methods unchanged (omitted for brevity)
#     def get_documents(self, obj):
#         """Get documents related to the ticket using correct related_name"""
#         try:
#             documents = obj.documents.all()  # ← This is KEY: use related_name="documents"
#             return [
#                 {
#                     'id': doc.id,
#                     'file': doc.file.url if doc.file else None,
#                     'original_name': doc.original_name or doc.file.name.split('/')[-1] if doc.file else "Unknown",
#                 }
#                 for doc in documents
#             ]
#         except Exception as e:
#             logger.error(f"Error fetching documents for ticket {obj.id}: {e}")
#             return []

#     def get_type_detail(self, obj):
#         if obj.type:
#             return {'id': obj.type.id, 'field_name': obj.type.field_name}
#         return None

#     def get_department_detail(self, obj):
#         if obj.department:
#             return {'id': obj.department.id, 'field_name': obj.department.field_name}
#         return None

#     def get_location_detail(self, obj):
#         if obj.location:
#             return {'id': obj.location.id, 'field_name': obj.location.field_name}
#         return None

#     def get_platform_detail(self, obj):
#         if obj.platform:
#             return {'id': obj.platform.id, 'field_name': obj.platform.field_name}
#         return None

#     def get_priority_detail(self, obj):
#         if obj.priority:
#             return {'id': obj.priority.id, 'field_name': obj.priority.field_name}
#         return None

#     def get_category_detail(self, obj):
#         if obj.category:
#             return {'id': obj.category.id, 'category_name': obj.category.category_name}
#         return None

#     def get_subcategory_detail(self, obj):
#         if obj.subcategory:
#             return {'id': obj.subcategory.id, 'subcategory_name': obj.subcategory.subcategory_name}
#         return None

#     def get_requested_detail(self, obj):
#         if obj.requested:
#             details = self._safe_get_user_details(obj.requested, include_id=True)
#             return details
#         return None

#     def get_status_detail(self, obj):
#         if obj.status:
#             return {'id': obj.status.id, 'field_name': obj.status.field_name, 'field_values': obj.status.field_values}
#         return None

#     def get_assignees_detail(self, obj):
#         """Get details for assignees from JSON field"""
#         assignees = obj.assigned_users or []
#         if assignees:
#             return [
#                 self._safe_get_user_details(assignee_email, include_id=True)
#                 for assignee_email in assignees
#             ]
#         return []

#     def get_assigned_groups_detail(self, obj):
#         """Get details for assigned groups from JSON field - Enhanced with members list"""
#         assigned_groups = obj.assigned_groups or []
#         if assigned_groups:
#             groups_detail = []
#             for group_id in assigned_groups:
#                 try:
#                     group = UsersGroup.objects.get(id=group_id)
#                     members = group.get_users()  # Assuming get_users() returns a queryset of User objects
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": group.name,
#                         "members_count": members.count(),
#                         "members": [
#                             self._safe_get_user_details(member, include_id=True)
#                             for member in members
#                         ]
#                     })
#                 except UsersGroup.DoesNotExist:
#                     logger.warning(f"Group with ID {group_id} not found for ticket {obj.id}")
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": f"Group {group_id} (Not Found)",
#                         "members_count": 0,
#                         "members": []
#                     })
#             return groups_detail
#         return []

#     # Helper methods unchanged (omitted for brevity)
#     def _safe_get_user_details(self, user_or_email, include_id=False):
#         """Inline alternative to get_user_details - safe user details without external import"""
#         if isinstance(user_or_email, User):
#             user = user_or_email
#             email = user.email
#         else:
#             email = user_or_email
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return {'name': email, 'email': email}
        
#         name = (getattr(user, 'name', None) or
#                 getattr(user, 'firstname', '') + ' ' + getattr(user, 'last_name', '')).strip() or user.username or user.email
#         firstname = getattr(user, 'firstname', '') or ''
#         lastname = getattr(user, 'last_name', '') or ''
#         details = {'name': name, 'email': email, 'firstname': firstname, 'lastname': lastname}
#         if include_id:
#             details['id'] = user.id
#         return details

#     def _get_user_id_by_email(self, email):
#         try:
#             user = User.objects.get(email=email)
#             return user.id
#         except User.DoesNotExist:
#             return None

#     def _get_user_name_by_email(self, email):
#         return self._safe_get_user_details(email)['name']

#     def _get_group_name_by_id(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.name
#         except UsersGroup.DoesNotExist:
#             return f"Group {group_id}"

#     def _get_group_members_count(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.get_users().count()
#         except UsersGroup.DoesNotExist:
#             return 0

#     def validate(self, data):
#         """Validate required fields - lenient for partial updates"""
#         if not self.partial:
#             # For create: enforce required fields
#             if 'title' not in data or not data['title'].strip():
#                 raise serializers.ValidationError({"title": "This field is required."})
#             if 'description' not in data or not data['description'].strip():
#                 raise serializers.ValidationError({"description": "This field is required."})
#             if 'category' not in data or not data['category']:
#                 raise serializers.ValidationError({"category": "This field is required."})
#         else:
#             # For update: optional, but validate if provided
#             if 'title' in data and not data['title'].strip():
#                 raise serializers.ValidationError({"title": "Title cannot be empty."})
#             if 'description' in data and not data['description'].strip():
#                 raise serializers.ValidationError({"description": "Description cannot be empty."})
#             if 'category' in data and not data['category']:
#                 raise serializers.ValidationError({"category": "Category cannot be empty."})
        
#         # NEW: Validate status if provided (mandatory single value from valid options)
#         status = data.get('status')
#         if status:
#             if not isinstance(status, TicketsMasterConfiguration) or status.field_type != 'Status' or status.is_active != 'Y':
#                 raise serializers.ValidationError({"status": "Invalid or inactive status provided."})
#         # For create, status is auto-set in create(), so no further check here
        
#         # Handle FormData lists (unchanged)
#         assigned_to_type_list = data.get('assigned_to_type', [])
#         if isinstance(assigned_to_type_list, list):
#             assigned_to_type = [t for t in assigned_to_type_list if t in ['user', 'group']]
#             data['assigned_to_type'] = assigned_to_type
#         else:
#             assigned_to_type = []

#         # Convert assignee IDs or emails to emails (unchanged)
#         assignee_list = data.get('assignee', [])
#         if isinstance(assignee_list, list):
#             emails = []
#             for item in assignee_list:
#                 if isinstance(item, str) and '@' in item:
#                     emails.append(item)
#                 else:
#                     try:
#                         user_id = int(str(item))
#                         user = User.objects.get(id=user_id)
#                         emails.append(user.email)
#                     except (ValueError, User.DoesNotExist):
#                         pass
#             data['assignee'] = emails
#         else:
#             data['assignee'] = []

#         # Validate emails exist (only if provided) (unchanged)
#         assignees = data['assignee']
#         for email in assignees:
#             if not User.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"assignee": f"User with email {email} does not exist."})

#         assigned_group_list = data.get('assigned_group', [])
#         if isinstance(assigned_group_list, list):
#             data['assigned_group'] = [int(g) for g in assigned_group_list if isinstance(g, (str, int))]
#         else:
#             data['assigned_group'] = []

#         # Validate groups exist (only if provided) (unchanged)
#         assigned_groups = data['assigned_group']
#         for gid in assigned_groups:
#             if not UsersGroup.objects.filter(id=gid).exists():
#                 raise serializers.ValidationError({"assigned_group": f"Group {gid} does not exist."})
        
#         has_user = 'user' in assigned_to_type
#         has_group = 'group' in assigned_to_type
        
#         if has_user and not assignees:
#             raise serializers.ValidationError({"assignee": "At least one user email required if User is selected."})
#         if has_group and not assigned_groups:
#             raise serializers.ValidationError({"assigned_group": "At least one group ID required if Group is selected."})
        
#         return data
#     def create(self, validated_data):
#         """Create new ticket - auto set department & location from logged-in user"""
#         request = self.context.get("request")
#         user = request.user if request else None

#         with transaction.atomic():
#             # Pop list fields
#             assigned_to_type = validated_data.pop('assigned_to_type', [])
#             assignees = validated_data.pop('assignee', [])
#             assigned_groups = validated_data.pop('assigned_group', [])
#             watchers = validated_data.pop('watchers', [])

#             # ✅ AUTO SET DEPARTMENT & LOCATION FROM USER
#             if user:
#                 # Department
#                 if not validated_data.get('department') and user.department_id:
#                     validated_data['department'] = user.department_id

#                 # Location
#                 if not validated_data.get('location') and user.locations:
#                     validated_data['location'] = user.locations

#             # ✅ Default Status = "New"
#             if 'status' not in validated_data:
#                 try:
#                     validated_data['status'] = TicketsMasterConfiguration.objects.get(
#                         field_type='Status',
#                         field_name='New',
#                         is_active='Y'
#                     )
#                 except TicketsMasterConfiguration.DoesNotExist:
#                     raise serializers.ValidationError({
#                         "status": "Default 'New' status not found."
#                     })

#             # Create ticket
#             instance = super().create(validated_data)

#             # Save assignments
#             instance.assigned_users = assignees
#             instance.assigned_groups = assigned_groups
#             instance.save()

#             # Add watchers
#             for watcher in watchers:
#                 instance.watchers.add(watcher)

#             return instance

#     # def create(self, validated_data):
#     #     """Create new ticket - set default status to 'New' and handle lists"""
#     #     with transaction.atomic():
#     #         # Pop list fields to avoid passing to super().create
#     #         assigned_to_type = validated_data.pop('assigned_to_type', [])
#     #         assignees = validated_data.pop('assignee', [])  # list of emails
#     #         assigned_groups = validated_data.pop('assigned_group', [])
#     #         watchers = validated_data.pop('watchers', [])
            
#     #         # Set default status to 'New' if not provided
#     #         if 'status' not in validated_data:
#     #             try:
#     #                 new_status = TicketsMasterConfiguration.objects.get(
#     #                     field_type='Status', 
#     #                     field_name='New', 
#     #                     is_active='Y'
#     #                 )
#     #                 validated_data['status'] = new_status
#     #             except TicketsMasterConfiguration.DoesNotExist:
#     #                 raise serializers.ValidationError({"status": "Default 'New' status not found."})
            
#     #         # Create instance with remaining data (no lists)
#     #         instance = super().create(validated_data)
            
#     #         # Set JSON fields for multiples
#     #         instance.assigned_users = assignees  # store emails
#     #         instance.assigned_groups = assigned_groups  # store IDs
#     #         instance.save()
            
#     #         # Add watchers if provided
#     #         for watcher in watchers:
#     #             instance.watchers.add(watcher)
            
#     #         return instance

#     def update(self, instance, validated_data):
#         """Update ticket - partial updates supported"""
#         with transaction.atomic():
#             # Pop list fields if present
#             assigned_to_type = validated_data.pop('assigned_to_type', None)
#             assignees = validated_data.pop('assignee', None)
#             assigned_groups = validated_data.pop('assigned_group', None)
#             watchers = validated_data.pop('watchers', None)
            
#             # Update basic fields (only those provided) - now includes status
#             for attr, value in validated_data.items():
#                 setattr(instance, attr, value)
            
#             # Handle assignment changes (multiple) - FIXED: Additive unless explicitly empty
#             if assigned_to_type is not None:
#                 # Only clear if explicitly empty; otherwise append
#                 if not assigned_to_type:
#                     instance.assigned_users = []
#                     instance.assigned_groups = []
#                 else:
#                     if 'user' in assigned_to_type:
#                         if assignees:  # Append if provided
#                             if instance.assigned_users is None:
#                                 instance.assigned_users = []
#                             instance.assigned_users.extend([e for e in assignees if e not in instance.assigned_users])
#                         # Add new to watchers
#                         for email in assignees or []:
#                             try:
#                                 user = User.objects.get(email=email)
#                                 if user not in instance.watchers.all():
#                                     instance.watchers.add(user)
#                             except User.DoesNotExist:
#                                 pass
#                     if 'group' in assigned_to_type:
#                         if assigned_groups:  # Append if provided
#                             if instance.assigned_groups is None:
#                                 instance.assigned_groups = []
#                             instance.assigned_groups.extend([g for g in assigned_groups if g not in instance.assigned_groups])
#                         # Add new group members to watchers
#                         for group_id in assigned_groups or []:
#                             try:
#                                 group = UsersGroup.objects.get(id=group_id)
#                                 group_users = group.get_users()
#                                 for member in group_users:
#                                     if member not in instance.watchers.all():
#                                         instance.watchers.add(member)
#                             except UsersGroup.DoesNotExist:
#                                 pass
            
#             # Update watchers if provided (set overrides, but could be made additive)
#             if watchers is not None:
#                 instance.watchers.set(watchers)
            
#             instance.save()
#             return instance

# class CreateTicketSerializer(serializers.ModelSerializer):
#     # Write-only PKs (unchanged)
#     # entity = serializers.PrimaryKeyRelatedField(
#     #     queryset=Entity.objects.all(),
#     #     write_only=True,
#     #     required=False,
#     #     allow_null=True
#     # )
#     entity_id = serializers.PrimaryKeyRelatedField(
#         source='entity',
#         queryset=Entity.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     type = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='TicketType'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     location = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     platform = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Platform'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     priority = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Priority'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
    
#     # NEW: Status as writeable PK field (for updates)
#     status = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Status', is_active='Y'),
#         write_only=False,  # Allow read/write
#         required=False,
#         allow_null=True
#     )
    
#     # Category/Subcategory IDs (unchanged)
#     category = serializers.PrimaryKeyRelatedField(
#         queryset=TicketCategory.objects.all(),
#         write_only=True,
#         required=False,  # Make optional for updates
#         allow_null=True
#     )
#     subcategory = serializers.PrimaryKeyRelatedField(
#         queryset=TicketSubcategory.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )

#     # Assignment fields - Handle multiples via lists of IDs or emails (unchanged)
#     assigned_to_type = serializers.ListField(
#         child=serializers.ChoiceField(choices=[('user', 'User'), ('group', 'Group')]), 
#         write_only=True, 
#         required=False
#     )
#     assignee = serializers.ListField(  # Multiple user IDs or emails
#         child=serializers.CharField(), 
#         write_only=True, 
#         required=False
#     )
#     assigned_group = serializers.ListField(  # Multiple group IDs
#         child=serializers.IntegerField(), 
#         write_only=True, 
#         required=False
#     )

#     # Read-only details (unchanged)
#     type_detail = serializers.SerializerMethodField(read_only=True)
#     department_detail = serializers.SerializerMethodField(read_only=True)
#     location_detail = serializers.SerializerMethodField(read_only=True)
#     platform_detail = serializers.SerializerMethodField(read_only=True)
#     priority_detail = serializers.SerializerMethodField(read_only=True)
#     category_detail = serializers.SerializerMethodField(read_only=True)
#     subcategory_detail = serializers.SerializerMethodField(read_only=True)
#     requested_detail = serializers.SerializerMethodField(read_only=True)
#     assignees_detail = serializers.SerializerMethodField(read_only=True)
#     assigned_groups_detail = serializers.SerializerMethodField(read_only=True)
#     status_detail = serializers.SerializerMethodField(read_only=True)
    
#     # Documents field (unchanged)
#     documents = serializers.SerializerMethodField(read_only=True)
    
#     # Watchers field (unchanged)
#     watchers = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         many=True,
#         required=False,
#         write_only=True
#     )

#     # Title and description - required for create, optional for update (unchanged)
#     title = serializers.CharField(required=False, allow_blank=True)
#     description = serializers.CharField(required=False, allow_blank=True)

#     class Meta:
#         model = CreateTicket
#         fields = [
#             'id', 'ticket_no', 'title', 'description', 
#             # 'entity',
#             'entity_id',
#             'type', 'type_detail', 
#             'department', 'department_detail',
#             'location', 'location_detail', 
#             'platform', 'platform_detail',
#             'priority', 'priority_detail',
#             'category', 'category_detail',
#             'subcategory', 'subcategory_detail',
#             'status', 'status_detail',  # Now fully included
#             'assigned_to_type', 'assignee', 'assignees_detail',
#             'assigned_group', 'assigned_groups_detail',
#             'requested', 'requested_detail', 'watchers',
#             'documents', 'sla', 'created_date', 'updated_date', 'closed_on'
#         ]
#         read_only_fields = ['id', 'ticket_no', 'created_date', 'updated_date', 'closed_on', 'sla']  # Removed 'status'

#     def __init__(self, *args, **kwargs):
#         self.partial = kwargs.pop('partial', False)
#         super().__init__(*args, **kwargs)
        
#         if not self.partial:
#             self.fields['title'].required = True
#             self.fields['description'].required = True
#             self.fields['category'].required = True
#             self.fields['entity_id'].required = True
#     # def __init__(self, *args, **kwargs):
#     #     # Detect if this is an update (partial update)
#     #     self.partial = kwargs.pop('partial', False)
#     #     super().__init__(*args, **kwargs)
        
#     #     # For create, make required fields required (unchanged)
#     #     if not self.partial:
#     #         self.fields['title'].required = True
#     #         self.fields['description'].required = True
#     #         self.fields['category'].required = True
#             # NEW: For create, status is auto-set, so not required here

#     # All get_ methods unchanged (omitted for brevity)
#     def get_documents(self, obj):
#         """Get documents related to the ticket"""
#         try:
#             documents = TicketDocument.objects.filter(ticket=obj)
#             return [
#                 {
#                     'id': doc.id,
#                     'file': doc.file.url if doc.file else None,
#                     'original_name': doc.original_name,
#                 }
#                 for doc in documents
#             ]
#         except Exception as e:
#             logger.error(f"Error fetching documents for ticket {obj.id}: {e}")
#             return []

#     def get_type_detail(self, obj):
#         if obj.type:
#             return {'id': obj.type.id, 'field_name': obj.type.field_name}
#         return None

#     def get_department_detail(self, obj):
#         if obj.department:
#             return {'id': obj.department.id, 'field_name': obj.department.field_name}
#         return None

#     def get_location_detail(self, obj):
#         if obj.location:
#             return {'id': obj.location.id, 'field_name': obj.location.field_name}
#         return None

#     def get_platform_detail(self, obj):
#         if obj.platform:
#             return {'id': obj.platform.id, 'field_name': obj.platform.field_name}
#         return None

#     def get_priority_detail(self, obj):
#         if obj.priority:
#             return {'id': obj.priority.id, 'field_name': obj.priority.field_name}
#         return None

#     def get_category_detail(self, obj):
#         if obj.category:
#             return {'id': obj.category.id, 'category_name': obj.category.category_name}
#         return None

#     def get_subcategory_detail(self, obj):
#         if obj.subcategory:
#             return {'id': obj.subcategory.id, 'subcategory_name': obj.subcategory.subcategory_name}
#         return None

#     def get_requested_detail(self, obj):
#         if obj.requested:
#             details = self._safe_get_user_details(obj.requested, include_id=True)
#             return details
#         return None

#     def get_status_detail(self, obj):
#         if obj.status:
#             return {'id': obj.status.id, 'field_name': obj.status.field_name, 'field_values': obj.status.field_values}
#         return None

#     def get_assignees_detail(self, obj):
#         """Get details for assignees from JSON field"""
#         assignees = obj.assigned_users or []
#         if assignees:
#             return [
#                 self._safe_get_user_details(assignee_email, include_id=True)
#                 for assignee_email in assignees
#             ]
#         return []

#     def get_assigned_groups_detail(self, obj):
#         """Get details for assigned groups from JSON field - Enhanced with members list"""
#         assigned_groups = obj.assigned_groups or []
#         if assigned_groups:
#             groups_detail = []
#             for group_id in assigned_groups:
#                 try:
#                     group = UsersGroup.objects.get(id=group_id)
#                     members = group.get_users()  # Assuming get_users() returns a queryset of User objects
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": group.name,
#                         "members_count": members.count(),
#                         "members": [
#                             self._safe_get_user_details(member, include_id=True)
#                             for member in members
#                         ]
#                     })
#                 except UsersGroup.DoesNotExist:
#                     logger.warning(f"Group with ID {group_id} not found for ticket {obj.id}")
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": f"Group {group_id} (Not Found)",
#                         "members_count": 0,
#                         "members": []
#                     })
#             return groups_detail
#         return []

#     # Helper methods unchanged (omitted for brevity)
#     def _safe_get_user_details(self, user_or_email, include_id=False):
#         """Inline alternative to get_user_details - safe user details without external import"""
#         if isinstance(user_or_email, User):
#             user = user_or_email
#             email = user.email
#         else:
#             email = user_or_email
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return {'name': email, 'email': email}
        
#         name = (getattr(user, 'name', None) or
#                 getattr(user, 'first_name', '') + ' ' + getattr(user, 'last_name', '')).strip() or user.username or user.email
#         firstname = getattr(user, 'first_name', '') or ''
#         lastname = getattr(user, 'last_name', '') or ''
#         details = {'name': name, 'email': email, 'firstname': firstname, 'lastname': lastname}
#         if include_id:
#             details['id'] = user.id
#         return details

#     def _get_user_id_by_email(self, email):
#         try:
#             user = User.objects.get(email=email)
#             return user.id
#         except User.DoesNotExist:
#             return None

#     def _get_user_name_by_email(self, email):
#         return self._safe_get_user_details(email)['name']

#     def _get_group_name_by_id(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.name
#         except UsersGroup.DoesNotExist:
#             return f"Group {group_id}"

#     def _get_group_members_count(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.get_users().count()
#         except UsersGroup.DoesNotExist:
#             return 0

#     def validate(self, data):
#         """Validate required fields - lenient for partial updates"""
#         if not self.partial:
#             # For create: enforce required fields
#             if 'title' not in data or not data['title'].strip():
#                 raise serializers.ValidationError({"title": "This field is required."})
#             if 'description' not in data or not data['description'].strip():
#                 raise serializers.ValidationError({"description": "This field is required."})
#             if 'category' not in data or not data['category']:
#                 raise serializers.ValidationError({"category": "This field is required."})
#         else:
#             # For update: optional, but validate if provided
#             if 'title' in data and not data['title'].strip():
#                 raise serializers.ValidationError({"title": "Title cannot be empty."})
#             if 'description' in data and not data['description'].strip():
#                 raise serializers.ValidationError({"description": "Description cannot be empty."})
#             if 'category' in data and not data['category']:
#                 raise serializers.ValidationError({"category": "Category cannot be empty."})
        
#         # NEW: Validate entity, category, subcategory consistency
#         entity = data.get('entity')
#         category = data.get('category')
#         subcategory = data.get('subcategory')

#         if entity and category:
#             if category.entity != entity:
#                 raise serializers.ValidationError({
#                     'category': f"Selected category does not belong to entity '{entity.name}'."
#                 })

#         if entity and subcategory:
#             if subcategory.entity != entity or subcategory.category != category:
#                 raise serializers.ValidationError({
#                     'subcategory': f"Selected subcategory does not belong to entity '{entity.name}' or category '{category.category_name}'."
#                 })
        
#         # NEW: Validate status if provided (mandatory single value from valid options)
#         status = data.get('status')
#         if status:
#             if not isinstance(status, TicketsMasterConfiguration) or status.field_type != 'Status' or status.is_active != 'Y':
#                 raise serializers.ValidationError({"status": "Invalid or inactive status provided."})
#         # For create, status is auto-set in create(), so no further check here
        
#         # Handle FormData lists (unchanged)
#         assigned_to_type_list = data.get('assigned_to_type', [])
#         if isinstance(assigned_to_type_list, list):
#             assigned_to_type = [t for t in assigned_to_type_list if t in ['user', 'group']]
#             data['assigned_to_type'] = assigned_to_type
#         else:
#             assigned_to_type = []

#         # Convert assignee IDs or emails to emails (unchanged)
#         assignee_list = data.get('assignee', [])
#         if isinstance(assignee_list, list):
#             emails = []
#             for item in assignee_list:
#                 if isinstance(item, str) and '@' in item:
#                     emails.append(item)
#                 else:
#                     try:
#                         user_id = int(str(item))
#                         user = User.objects.get(id=user_id)
#                         emails.append(user.email)
#                     except (ValueError, User.DoesNotExist):
#                         pass
#             data['assignee'] = emails
#         else:
#             data['assignee'] = []

#         # Validate emails exist (only if provided) (unchanged)
#         assignees = data['assignee']
#         for email in assignees:
#             if not User.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"assignee": f"User with email {email} does not exist."})

#         assigned_group_list = data.get('assigned_group', [])
#         if isinstance(assigned_group_list, list):
#             data['assigned_group'] = [int(g) for g in assigned_group_list if isinstance(g, (str, int))]
#         else:
#             data['assigned_group'] = []

#         # Validate groups exist (only if provided) (unchanged)
#         assigned_groups = data['assigned_group']
#         for gid in assigned_groups:
#             if not UsersGroup.objects.filter(id=gid).exists():
#                 raise serializers.ValidationError({"assigned_group": f"Group {gid} does not exist."})
        
#         has_user = 'user' in assigned_to_type
#         has_group = 'group' in assigned_to_type
        
#         if has_user and not assignees:
#             raise serializers.ValidationError({"assignee": "At least one user email required if User is selected."})
#         if has_group and not assigned_groups:
#             raise serializers.ValidationError({"assigned_group": "At least one group ID required if Group is selected."})
        
#         return data

#     def create(self, validated_data):
#         """Create new ticket - set default status to 'New' and handle lists"""
#         with transaction.atomic():
#             # Pop list fields to avoid passing to super().create
#             assigned_to_type = validated_data.pop('assigned_to_type', [])
#             assignees = validated_data.pop('assignee', [])  # list of emails
#             assigned_groups = validated_data.pop('assigned_group', [])
#             watchers = validated_data.pop('watchers', [])
            
#             # Set default status to 'New' if not provided
#             if 'status' not in validated_data:
#                 try:
#                     new_status = TicketsMasterConfiguration.objects.get(
#                         field_type='Status', 
#                         field_name='New', 
#                         is_active='Y'
#                     )
#                     validated_data['status'] = new_status
#                 except TicketsMasterConfiguration.DoesNotExist:
#                     raise serializers.ValidationError({"status": "Default 'New' status not found."})
            
#             # Create instance with remaining data (no lists)
#             instance = super().create(validated_data)
            
#             # Set JSON fields for multiples
#             instance.assigned_users = assignees  # store emails
#             instance.assigned_groups = assigned_groups  # store IDs
#             instance.save()
            
#             # Add watchers if provided
#             for watcher in watchers:
#                 instance.watchers.add(watcher)
            
#             return instance

#     def update(self, instance, validated_data):
        
#         with transaction.atomic():
#             # Pop list fields if present (so they don't interfere with basic updates)
#             assigned_to_type = validated_data.pop('assigned_to_type', None)
#             assignees = validated_data.pop('assignee', None)
#             assigned_groups = validated_data.pop('assigned_group', None)
#             watchers = validated_data.pop('watchers', None)
            
#             # Update all simple fields from validated_data (including status, title, etc.)
#             for attr, value in validated_data.items():
#                 setattr(instance, attr, value)  # ← FIXED: Now passes the value

#             # Handle assignments (additive behavior - only adds new ones)
#             if assigned_to_type is not None:
#                 if not assigned_to_type:
#                     # Explicitly empty → clear assignments
#                     instance.assigned_users = []
#                     instance.assigned_groups = []
#                 else:
#                     # Add new users
#                     if 'user' in assigned_to_type and assignees:
#                         if instance.assigned_users is None:
#                             instance.assigned_users = []
#                         for email in assignees:
#                             if email not in instance.assigned_users:
#                                 instance.assigned_users.append(email)
                        
#                         # Add users to watchers
#                         for email in assignees:
#                             try:
#                                 user = User.objects.get(email=email)
#                                 if user not in instance.watchers.all():
#                                     instance.watchers.add(user)
#                             except User.DoesNotExist:
#                                 pass

#                     # Add new groups
#                     if 'group' in assigned_to_type and assigned_groups:
#                         if instance.assigned_groups is None:
#                             instance.assigned_groups = []
#                         for gid in assigned_groups:
#                             if gid not in instance.assigned_groups:
#                                 instance.assigned_groups.append(gid)
                        
#                         # Add group members to watchers
#                         for group_id in assigned_groups:
#                             try:
#                                 group = UsersGroup.objects.get(id=group_id)
#                                 for member in group.get_users():
#                                     if member not in instance.watchers.all():
#                                         instance.watchers.add(member)
#                             except UsersGroup.DoesNotExist:
#                                 pass

#             # Override watchers if explicitly provided
#             if watchers is not None:
#                 instance.watchers.set(watchers)
            
#             instance.save()
#             return instance

class CreateTicketSerializer(serializers.ModelSerializer):
    # Write-only PKs (unchanged)
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    type = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='TicketType'),
        write_only=True,
        required=False,
        allow_null=True
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'),
        write_only=True,
        required=False,
        allow_null=True
    )
    location = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
        write_only=True,
        required=False,
        allow_null=True
    )
    platform = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Platform'),
        write_only=True,
        required=False,
        allow_null=True
    )
    priority = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Priority'),
        write_only=True,
        required=False,
        allow_null=True
    )
   
    # NEW: Status as writeable PK field (for updates)
    status = serializers.PrimaryKeyRelatedField(
        queryset=TicketsMasterConfiguration.objects.filter(field_type='Status', is_active='Y'),
        write_only=False,  # Allow read/write
        required=False,
        allow_null=True
    )
   
    # Category/Subcategory IDs (unchanged)
    category = serializers.PrimaryKeyRelatedField(
        queryset=TicketCategory.objects.all(),
        write_only=True,
        required=False,  # Make optional for updates
        allow_null=True
    )
    subcategory = serializers.PrimaryKeyRelatedField(
        queryset=TicketSubcategory.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
 
    # Assignment fields - Handle multiples via lists of IDs or emails (unchanged)
    assigned_to_type = serializers.ListField(
        child=serializers.ChoiceField(choices=[('user', 'User'), ('group', 'Group')]),
        write_only=True,
        required=False
    )
    assignee = serializers.ListField(  # Multiple user IDs or emails
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    assigned_group = serializers.ListField(  # Multiple group IDs
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
 
    # Read-only details (unchanged)
    type_detail = serializers.SerializerMethodField(read_only=True)
    department_detail = serializers.SerializerMethodField(read_only=True)
    location_detail = serializers.SerializerMethodField(read_only=True)
    platform_detail = serializers.SerializerMethodField(read_only=True)
    priority_detail = serializers.SerializerMethodField(read_only=True)
    category_detail = serializers.SerializerMethodField(read_only=True)
    subcategory_detail = serializers.SerializerMethodField(read_only=True)
    requested_detail = serializers.SerializerMethodField(read_only=True)
    assignees_detail = serializers.SerializerMethodField(read_only=True)
    assigned_groups_detail = serializers.SerializerMethodField(read_only=True)
    status_detail = serializers.SerializerMethodField(read_only=True)
   
    # Documents field (unchanged)
    documents = serializers.SerializerMethodField(read_only=True)
   
    # Watchers field (unchanged)
    watchers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
 
    # Title and description - required for create, optional for update (unchanged)
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
 
    class Meta:
        model = CreateTicket
        fields = [
            'id', 'ticket_no', 'title', 'description',
            'entity',
            'type', 'type_detail',
            'department', 'department_detail',
            'location', 'location_detail',
            'platform', 'platform_detail',
            'priority', 'priority_detail',
            'category', 'category_detail',
            'subcategory', 'subcategory_detail',
            'status', 'status_detail',  # Now fully included
            'assigned_to_type', 'assignee', 'assignees_detail',
            'assigned_group', 'assigned_groups_detail',
            'requested', 'requested_detail', 'watchers',
            'documents', 'sla', 'created_date', 'updated_date', 'closed_on'
        ]
        read_only_fields = ['id', 'ticket_no', 'created_date', 'updated_date', 'closed_on', 'sla']  # Removed 'status'
 
    def __init__(self, *args, **kwargs):
        # Detect if this is an update (partial update)
        self.partial = kwargs.pop('partial', False)
        super().__init__(*args, **kwargs)
       
        # For create, make required fields required (unchanged)
        if not self.partial:
            self.fields['title'].required = True
            self.fields['description'].required = True
            self.fields['category'].required = True
            # NEW: For create, status is auto-set, so not required here
 
    # All get_ methods unchanged (omitted for brevity)
    def get_documents(self, obj):
        """Get documents related to the ticket"""
        try:
            documents = TicketDocument.objects.filter(ticket=obj)
            return [
                {
                    'id': doc.id,
                    'file': doc.file.url if doc.file else None,
                    'original_name': doc.original_name,
                }
                for doc in documents
            ]
        except Exception as e:
            logger.error(f"Error fetching documents for ticket {obj.id}: {e}")
            return []
 
    def get_type_detail(self, obj):
        if obj.type:
            return {'id': obj.type.id, 'field_name': obj.type.field_name}
        return None
 
    def get_department_detail(self, obj):
        if obj.department:
            return {'id': obj.department.id, 'field_name': obj.department.field_name}
        return None
 
    def get_location_detail(self, obj):
        if obj.location:
            return {'id': obj.location.id, 'field_name': obj.location.field_name}
        return None
 
    def get_platform_detail(self, obj):
        if obj.platform:
            return {'id': obj.platform.id, 'field_name': obj.platform.field_name}
        return None
 
    def get_priority_detail(self, obj):
        if obj.priority:
            return {'id': obj.priority.id, 'field_name': obj.priority.field_name}
        return None
 
    def get_category_detail(self, obj):
        if obj.category:
            return {'id': obj.category.id, 'category_name': obj.category.category_name}
        return None
 
    def get_subcategory_detail(self, obj):
        if obj.subcategory:
            return {'id': obj.subcategory.id, 'subcategory_name': obj.subcategory.subcategory_name}
        return None
 
    def get_requested_detail(self, obj):
        if obj.requested:
            details = self._safe_get_user_details(obj.requested, include_id=True)
            return details
        return None
 
    def get_status_detail(self, obj):
        if obj.status:
            return {'id': obj.status.id, 'field_name': obj.status.field_name, 'field_values': obj.status.field_values}
        return None
 
    def get_assignees_detail(self, obj):
        """Get details for assignees from JSON field"""
        assignees = obj.assigned_users or []
        if assignees:
            return [
                self._safe_get_user_details(assignee_email, include_id=True)
                for assignee_email in assignees
            ]
        return []
 
    def get_assigned_groups_detail(self, obj):
        """Get details for assigned groups from JSON field - Enhanced with members list"""
        assigned_groups = obj.assigned_groups or []
        if assigned_groups:
            groups_detail = []
            for group_id in assigned_groups:
                try:
                    group = UsersGroup.objects.get(id=group_id)
                    members = group.get_users()  # Assuming get_users() returns a queryset of User objects
                    groups_detail.append({
                        "id": group_id,
                        "name": group.name,
                        "members_count": members.count(),
                        "members": [
                            self._safe_get_user_details(member, include_id=True)
                            for member in members
                        ]
                    })
                except UsersGroup.DoesNotExist:
                    logger.warning(f"Group with ID {group_id} not found for ticket {obj.id}")
                    groups_detail.append({
                        "id": group_id,
                        "name": f"Group {group_id} (Not Found)",
                        "members_count": 0,
                        "members": []
                    })
            return groups_detail
        return []
 
    # Helper methods unchanged (omitted for brevity)
    def _safe_get_user_details(self, user_or_email, include_id=False):
        """Inline alternative to get_user_details - safe user details without external import"""
        if isinstance(user_or_email, User):
            user = user_or_email
            email = user.email
        else:
            email = user_or_email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return {'name': email, 'email': email}
       
        name = (getattr(user, 'name', None) or
                getattr(user, 'first_name', '') + ' ' + getattr(user, 'last_name', '')).strip() or user.username or user.email
        firstname = getattr(user, 'first_name', '') or ''
        lastname = getattr(user, 'last_name', '') or ''
        details = {'name': name, 'email': email, 'firstname': firstname, 'lastname': lastname}
        if include_id:
            details['id'] = user.id
        return details
 
    def _get_user_id_by_email(self, email):
        try:
            user = User.objects.get(email=email)
            return user.id
        except User.DoesNotExist:
            return None
 
    def _get_user_name_by_email(self, email):
        return self._safe_get_user_details(email)['name']
 
    def _get_group_name_by_id(self, group_id):
        try:
            group = UsersGroup.objects.get(id=group_id)
            return group.name
        except UsersGroup.DoesNotExist:
            return f"Group {group_id}"
 
    def _get_group_members_count(self, group_id):
        try:
            group = UsersGroup.objects.get(id=group_id)
            return group.get_users().count()
        except UsersGroup.DoesNotExist:
            return 0
 
    def validate(self, data):
        """Validate required fields - lenient for partial updates"""
        if not self.partial:
            # For create: enforce required fields
            if 'title' not in data or not data['title'].strip():
                raise serializers.ValidationError({"title": "This field is required."})
            if 'description' not in data or not data['description'].strip():
                raise serializers.ValidationError({"description": "This field is required."})
            if 'category' not in data or not data['category']:
                raise serializers.ValidationError({"category": "This field is required."})
        else:
            # For update: optional, but validate if provided
            if 'title' in data and not data['title'].strip():
                raise serializers.ValidationError({"title": "Title cannot be empty."})
            if 'description' in data and not data['description'].strip():
                raise serializers.ValidationError({"description": "Description cannot be empty."})
            if 'category' in data and not data['category']:
                raise serializers.ValidationError({"category": "Category cannot be empty."})
       
        # NEW: Validate entity, category, subcategory consistency
        entity = data.get('entity')
        category = data.get('category')
        subcategory = data.get('subcategory')
 
        if entity and category:
            if category.entity != entity:
                raise serializers.ValidationError({
                    'category': f"Selected category does not belong to entity '{entity.name}'."
                })
 
        if entity and subcategory:
            if subcategory.entity != entity or subcategory.category != category:
                raise serializers.ValidationError({
                    'subcategory': f"Selected subcategory does not belong to entity '{entity.name}' or category '{category.category_name}'."
                })
       
        # NEW: Validate status if provided (mandatory single value from valid options)
        status = data.get('status')
        if status:
            if not isinstance(status, TicketsMasterConfiguration) or status.field_type != 'Status' or status.is_active != 'Y':
                raise serializers.ValidationError({"status": "Invalid or inactive status provided."})
        # For create, status is auto-set in create(), so no further check here
       
        # Handle FormData lists (unchanged)
        assigned_to_type_list = data.get('assigned_to_type', [])
        if isinstance(assigned_to_type_list, list):
            assigned_to_type = [t for t in assigned_to_type_list if t in ['user', 'group']]
            data['assigned_to_type'] = assigned_to_type
        else:
            assigned_to_type = []
 
        # Convert assignee IDs or emails to emails (unchanged)
        assignee_list = data.get('assignee', [])
        if isinstance(assignee_list, list):
            emails = []
            for item in assignee_list:
                if isinstance(item, str) and '@' in item:
                    emails.append(item)
                else:
                    try:
                        user_id = int(str(item))
                        user = User.objects.get(id=user_id)
                        emails.append(user.email)
                    except (ValueError, User.DoesNotExist):
                        pass
            data['assignee'] = emails
        else:
            data['assignee'] = []
 
        # Validate emails exist (only if provided) (unchanged)
        assignees = data['assignee']
        for email in assignees:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError({"assignee": f"User with email {email} does not exist."})
 
        assigned_group_list = data.get('assigned_group', [])
        if isinstance(assigned_group_list, list):
            data['assigned_group'] = [int(g) for g in assigned_group_list if isinstance(g, (str, int))]
        else:
            data['assigned_group'] = []
 
        # Validate groups exist (only if provided) (unchanged)
        assigned_groups = data['assigned_group']
        for gid in assigned_groups:
            if not UsersGroup.objects.filter(id=gid).exists():
                raise serializers.ValidationError({"assigned_group": f"Group {gid} does not exist."})
       
        has_user = 'user' in assigned_to_type
        has_group = 'group' in assigned_to_type
       
        if has_user and not assignees:
            raise serializers.ValidationError({"assignee": "At least one user email required if User is selected."})
        if has_group and not assigned_groups:
            raise serializers.ValidationError({"assigned_group": "At least one group ID required if Group is selected."})
       
        return data
 
    def create(self, validated_data):
        """Create new ticket - set default status to 'New' and handle lists"""
        with transaction.atomic():
            # Pop list fields to avoid passing to super().create
            assigned_to_type = validated_data.pop('assigned_to_type', [])
            assignees = validated_data.pop('assignee', [])  # list of emails
            assigned_groups = validated_data.pop('assigned_group', [])
            watchers = validated_data.pop('watchers', [])
           
            # Set default status to 'New' if not provided
            if 'status' not in validated_data:
                try:
                    new_status = TicketsMasterConfiguration.objects.get(
                        field_type='Status',
                        field_name='New',
                        is_active='Y'
                    )
                    validated_data['status'] = new_status
                except TicketsMasterConfiguration.DoesNotExist:
                    raise serializers.ValidationError({"status": "Default 'New' status not found."})
           
            # Create instance with remaining data (no lists)
            instance = super().create(validated_data)
           
            # Set JSON fields for multiples
            instance.assigned_users = assignees  # store emails
            instance.assigned_groups = assigned_groups  # store IDs
            instance.save()
           
            # Add watchers if provided
            for watcher in watchers:
                instance.watchers.add(watcher)
           
            return instance
 
    def update(self, instance, validated_data):
        """Update ticket - partial updates supported"""
        with transaction.atomic():
            # Pop list fields if present
            assigned_to_type = validated_data.pop('assigned_to_type', None)
            assignees = validated_data.pop('assignee', None)
            assigned_groups = validated_data.pop('assigned_group', None)
            watchers = validated_data.pop('watchers', None)
           
            # Update basic fields (only those provided) - now includes status
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
           
            # Handle assignment changes (multiple) - FIXED: Additive unless explicitly empty
            if assigned_to_type is not None:
                # Only clear if explicitly empty; otherwise append
                if not assigned_to_type:
                    instance.assigned_users = []
                    instance.assigned_groups = []
                else:
                    if 'user' in assigned_to_type:
                        if assignees:  # Append if provided
                            if instance.assigned_users is None:
                                instance.assigned_users = []
                            instance.assigned_users.extend([e for e in assignees if e not in instance.assigned_users])
                        # Add new to watchers
                        for email in assignees or []:
                            try:
                                user = User.objects.get(email=email)
                                if user not in instance.watchers.all():
                                    instance.watchers.add(user)
                            except User.DoesNotExist:
                                pass
                    if 'group' in assigned_to_type:
                        if assigned_groups:  # Append if provided
                            if instance.assigned_groups is None:
                                instance.assigned_groups = []
                            instance.assigned_groups.extend([g for g in assigned_groups if g not in instance.assigned_groups])
                        # Add new group members to watchers
                        for group_id in assigned_groups or []:
                            try:
                                group = UsersGroup.objects.get(id=group_id)
                                group_users = group.get_users()
                                for member in group_users:
                                    if member not in instance.watchers.all():
                                        instance.watchers.add(member)
                            except UsersGroup.DoesNotExist:
                                pass
           
            # Update watchers if provided (set overrides, but could be made additive)
            if watchers is not None:
                instance.watchers.set(watchers)
           
            instance.save()
            return instance
# class CreateTicketSerializer(serializers.ModelSerializer):
#     # Write-only PKs (unchanged)
#     # entity = serializers.PrimaryKeyRelatedField(
#     #     queryset=Entity.objects.all(),
#     #     write_only=True,
#     #     required=False,
#     #     allow_null=True
#     # )
#     entity_id = serializers.PrimaryKeyRelatedField(
#         source='entity',
#         queryset=Entity.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     type = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='TicketType'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     department = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Department'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     location = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     platform = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Platform'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
#     priority = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Priority'), 
#         write_only=True,
#         required=False,
#         allow_null=True
#     )
    
#     # NEW: Status as writeable PK field (for updates)
#     status = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Status', is_active='Y'),
#         write_only=False,  # Allow read/write
#         required=False,
#         allow_null=True
#     )
    
#     # Category/Subcategory IDs (unchanged)
#     category = serializers.PrimaryKeyRelatedField(
#         queryset=TicketCategory.objects.all(),
#         write_only=True,
#         required=False,  # Make optional for updates
#         allow_null=True
#     )
#     subcategory = serializers.PrimaryKeyRelatedField(
#         queryset=TicketSubcategory.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True
#     )

#     # Assignment fields - Handle multiples via lists of IDs or emails (unchanged)
#     assigned_to_type = serializers.ListField(
#         child=serializers.ChoiceField(choices=[('user', 'User'), ('group', 'Group')]), 
#         write_only=True, 
#         required=False
#     )
#     assignee = serializers.ListField(  # Multiple user IDs or emails
#         child=serializers.CharField(), 
#         write_only=True, 
#         required=False
#     )
#     assigned_group = serializers.ListField(  # Multiple group IDs
#         child=serializers.IntegerField(), 
#         write_only=True, 
#         required=False
#     )

#     # Read-only details (unchanged)
#     type_detail = serializers.SerializerMethodField(read_only=True)
#     department_detail = serializers.SerializerMethodField(read_only=True)
#     location_detail = serializers.SerializerMethodField(read_only=True)
#     platform_detail = serializers.SerializerMethodField(read_only=True)
#     priority_detail = serializers.SerializerMethodField(read_only=True)
#     category_detail = serializers.SerializerMethodField(read_only=True)
#     subcategory_detail = serializers.SerializerMethodField(read_only=True)
#     requested_detail = serializers.SerializerMethodField(read_only=True)
#     assignees_detail = serializers.SerializerMethodField(read_only=True)
#     assigned_groups_detail = serializers.SerializerMethodField(read_only=True)
#     status_detail = serializers.SerializerMethodField(read_only=True)
    
#     # Documents field (unchanged)
#     documents = serializers.SerializerMethodField(read_only=True)
    
#     # Watchers field (unchanged)
#     watchers = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         many=True,
#         required=False,
#         write_only=True
#     )

#     # Title and description - required for create, optional for update (unchanged)
#     title = serializers.CharField(required=False, allow_blank=True)
#     description = serializers.CharField(required=False, allow_blank=True)

#     class Meta:
#         model = CreateTicket
#         fields = [
#             'id', 'ticket_no', 'title', 'description', 
#             # 'entity',
#             'entity_id',
#             'type', 'type_detail', 
#             'department', 'department_detail',
#             'location', 'location_detail', 
#             'platform', 'platform_detail',
#             'priority', 'priority_detail',
#             'category', 'category_detail',
#             'subcategory', 'subcategory_detail',
#             'status', 'status_detail',  # Now fully included
#             'assigned_to_type', 'assignee', 'assignees_detail',
#             'assigned_group', 'assigned_groups_detail',
#             'requested', 'requested_detail', 'watchers',
#             'documents', 'sla', 'created_date', 'updated_date', 'closed_on'
#         ]
#         read_only_fields = ['id', 'ticket_no', 'created_date', 'updated_date', 'closed_on', 'sla']  # Removed 'status'

#     def __init__(self, *args, **kwargs):
#         self.partial = kwargs.pop('partial', False)
#         super().__init__(*args, **kwargs)
        
#         if not self.partial:
#             self.fields['title'].required = True
#             self.fields['description'].required = True
#             self.fields['category'].required = True
#             self.fields['entity_id'].required = True
#     # def __init__(self, *args, **kwargs):
#     #     # Detect if this is an update (partial update)
#     #     self.partial = kwargs.pop('partial', False)
#     #     super().__init__(*args, **kwargs)
        
#     #     # For create, make required fields required (unchanged)
#     #     if not self.partial:
#     #         self.fields['title'].required = True
#     #         self.fields['description'].required = True
#     #         self.fields['category'].required = True
#             # NEW: For create, status is auto-set, so not required here

#     # All get_ methods unchanged (omitted for brevity)
#     def get_documents(self, obj):
#         """Get documents related to the ticket"""
#         try:
#             documents = TicketDocument.objects.filter(ticket=obj)
#             return [
#                 {
#                     'id': doc.id,
#                     'file': doc.file.url if doc.file else None,
#                     'original_name': doc.original_name,
#                 }
#                 for doc in documents
#             ]
#         except Exception as e:
#             logger.error(f"Error fetching documents for ticket {obj.id}: {e}")
#             return []

#     def get_type_detail(self, obj):
#         if obj.type:
#             return {'id': obj.type.id, 'field_name': obj.type.field_name}
#         return None

#     def get_department_detail(self, obj):
#         if obj.department:
#             return {'id': obj.department.id, 'field_name': obj.department.field_name}
#         return None

#     def get_location_detail(self, obj):
#         if obj.location:
#             return {'id': obj.location.id, 'field_name': obj.location.field_name}
#         return None

#     def get_platform_detail(self, obj):
#         if obj.platform:
#             return {'id': obj.platform.id, 'field_name': obj.platform.field_name}
#         return None

#     def get_priority_detail(self, obj):
#         if obj.priority:
#             return {'id': obj.priority.id, 'field_name': obj.priority.field_name}
#         return None

#     def get_category_detail(self, obj):
#         if obj.category:
#             return {'id': obj.category.id, 'category_name': obj.category.category_name}
#         return None

#     def get_subcategory_detail(self, obj):
#         if obj.subcategory:
#             return {'id': obj.subcategory.id, 'subcategory_name': obj.subcategory.subcategory_name}
#         return None

#     def get_requested_detail(self, obj):
#         if obj.requested:
#             details = self._safe_get_user_details(obj.requested, include_id=True)
#             return details
#         return None

#     def get_status_detail(self, obj):
#         if obj.status:
#             return {'id': obj.status.id, 'field_name': obj.status.field_name, 'field_values': obj.status.field_values}
#         return None

#     def get_assignees_detail(self, obj):
#         """Get details for assignees from JSON field"""
#         assignees = obj.assigned_users or []
#         if assignees:
#             return [
#                 self._safe_get_user_details(assignee_email, include_id=True)
#                 for assignee_email in assignees
#             ]
#         return []

#     def get_assigned_groups_detail(self, obj):
#         """Get details for assigned groups from JSON field - Enhanced with members list"""
#         assigned_groups = obj.assigned_groups or []
#         if assigned_groups:
#             groups_detail = []
#             for group_id in assigned_groups:
#                 try:
#                     group = UsersGroup.objects.get(id=group_id)
#                     members = group.get_users()  # Assuming get_users() returns a queryset of User objects
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": group.name,
#                         "members_count": members.count(),
#                         "members": [
#                             self._safe_get_user_details(member, include_id=True)
#                             for member in members
#                         ]
#                     })
#                 except UsersGroup.DoesNotExist:
#                     logger.warning(f"Group with ID {group_id} not found for ticket {obj.id}")
#                     groups_detail.append({
#                         "id": group_id,
#                         "name": f"Group {group_id} (Not Found)",
#                         "members_count": 0,
#                         "members": []
#                     })
#             return groups_detail
#         return []

#     # Helper methods unchanged (omitted for brevity)
#     def _safe_get_user_details(self, user_or_email, include_id=False):
#         """Inline alternative to get_user_details - safe user details without external import"""
#         if isinstance(user_or_email, User):
#             user = user_or_email
#             email = user.email
#         else:
#             email = user_or_email
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return {'name': email, 'email': email}
        
#         name = (getattr(user, 'name', None) or
#                 getattr(user, 'first_name', '') + ' ' + getattr(user, 'last_name', '')).strip() or user.username or user.email
#         firstname = getattr(user, 'first_name', '') or ''
#         lastname = getattr(user, 'last_name', '') or ''
#         details = {'name': name, 'email': email, 'firstname': firstname, 'lastname': lastname}
#         if include_id:
#             details['id'] = user.id
#         return details

#     def _get_user_id_by_email(self, email):
#         try:
#             user = User.objects.get(email=email)
#             return user.id
#         except User.DoesNotExist:
#             return None

#     def _get_user_name_by_email(self, email):
#         return self._safe_get_user_details(email)['name']

#     def _get_group_name_by_id(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.name
#         except UsersGroup.DoesNotExist:
#             return f"Group {group_id}"

#     def _get_group_members_count(self, group_id):
#         try:
#             group = UsersGroup.objects.get(id=group_id)
#             return group.get_users().count()
#         except UsersGroup.DoesNotExist:
#             return 0

#     def validate(self, data):
#         """Validate required fields - lenient for partial updates"""
#         if not self.partial:
#             # For create: enforce required fields
#             if 'title' not in data or not data['title'].strip():
#                 raise serializers.ValidationError({"title": "This field is required."})
#             if 'description' not in data or not data['description'].strip():
#                 raise serializers.ValidationError({"description": "This field is required."})
#             if 'category' not in data or not data['category']:
#                 raise serializers.ValidationError({"category": "This field is required."})
#         else:
#             # For update: optional, but validate if provided
#             if 'title' in data and not data['title'].strip():
#                 raise serializers.ValidationError({"title": "Title cannot be empty."})
#             if 'description' in data and not data['description'].strip():
#                 raise serializers.ValidationError({"description": "Description cannot be empty."})
#             if 'category' in data and not data['category']:
#                 raise serializers.ValidationError({"category": "Category cannot be empty."})
        
#         # NEW: Validate entity, category, subcategory consistency
#         entity = data.get('entity')
#         category = data.get('category')
#         subcategory = data.get('subcategory')

#         if entity and category:
#             if category.entity != entity:
#                 raise serializers.ValidationError({
#                     'category': f"Selected category does not belong to entity '{entity.name}'."
#                 })

#         if entity and subcategory:
#             if subcategory.entity != entity or subcategory.category != category:
#                 raise serializers.ValidationError({
#                     'subcategory': f"Selected subcategory does not belong to entity '{entity.name}' or category '{category.category_name}'."
#                 })
        
#         # NEW: Validate status if provided (mandatory single value from valid options)
#         status = data.get('status')
#         if status:
#             if not isinstance(status, TicketsMasterConfiguration) or status.field_type != 'Status' or status.is_active != 'Y':
#                 raise serializers.ValidationError({"status": "Invalid or inactive status provided."})
#         # For create, status is auto-set in create(), so no further check here
        
#         # Handle FormData lists (unchanged)
#         assigned_to_type_list = data.get('assigned_to_type', [])
#         if isinstance(assigned_to_type_list, list):
#             assigned_to_type = [t for t in assigned_to_type_list if t in ['user', 'group']]
#             data['assigned_to_type'] = assigned_to_type
#         else:
#             assigned_to_type = []

#         # Convert assignee IDs or emails to emails (unchanged)
#         assignee_list = data.get('assignee', [])
#         if isinstance(assignee_list, list):
#             emails = []
#             for item in assignee_list:
#                 if isinstance(item, str) and '@' in item:
#                     emails.append(item)
#                 else:
#                     try:
#                         user_id = int(str(item))
#                         user = User.objects.get(id=user_id)
#                         emails.append(user.email)
#                     except (ValueError, User.DoesNotExist):
#                         pass
#             data['assignee'] = emails
#         else:
#             data['assignee'] = []

#         # Validate emails exist (only if provided) (unchanged)
#         assignees = data['assignee']
#         for email in assignees:
#             if not User.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"assignee": f"User with email {email} does not exist."})

#         assigned_group_list = data.get('assigned_group', [])
#         if isinstance(assigned_group_list, list):
#             data['assigned_group'] = [int(g) for g in assigned_group_list if isinstance(g, (str, int))]
#         else:
#             data['assigned_group'] = []

#         # Validate groups exist (only if provided) (unchanged)
#         assigned_groups = data['assigned_group']
#         for gid in assigned_groups:
#             if not UsersGroup.objects.filter(id=gid).exists():
#                 raise serializers.ValidationError({"assigned_group": f"Group {gid} does not exist."})
        
#         has_user = 'user' in assigned_to_type
#         has_group = 'group' in assigned_to_type
        
#         if has_user and not assignees:
#             raise serializers.ValidationError({"assignee": "At least one user email required if User is selected."})
#         if has_group and not assigned_groups:
#             raise serializers.ValidationError({"assigned_group": "At least one group ID required if Group is selected."})
        
#         return data

#     def create(self, validated_data):
#         """Create new ticket - set default status to 'New' and handle lists"""
#         with transaction.atomic():
#             # Pop list fields to avoid passing to super().create
#             assigned_to_type = validated_data.pop('assigned_to_type', [])
#             assignees = validated_data.pop('assignee', [])  # list of emails
#             assigned_groups = validated_data.pop('assigned_group', [])
#             watchers = validated_data.pop('watchers', [])
            
#             # Set default status to 'New' if not provided
#             if 'status' not in validated_data:
#                 try:
#                     new_status = TicketsMasterConfiguration.objects.get(
#                         field_type='Status', 
#                         field_name='New', 
#                         is_active='Y'
#                     )
#                     validated_data['status'] = new_status
#                 except TicketsMasterConfiguration.DoesNotExist:
#                     raise serializers.ValidationError({"status": "Default 'New' status not found."})
            
#             # Create instance with remaining data (no lists)
#             instance = super().create(validated_data)
            
#             # Set JSON fields for multiples
#             instance.assigned_users = assignees  # store emails
#             instance.assigned_groups = assigned_groups  # store IDs
#             instance.save()
            
#             # Add watchers if provided
#             for watcher in watchers:
#                 instance.watchers.add(watcher)
            
#             return instance

#     def update(self, instance, validated_data):
#         """Update ticket - partial updates supported"""
#         with transaction.atomic():
#             # Pop list fields if present
#             assigned_to_type = validated_data.pop('assigned_to_type', None)
#             assignees = validated_data.pop('assignee', None)
#             assigned_groups = validated_data.pop('assigned_group', None)
#             watchers = validated_data.pop('watchers', None)
            
#             # Update basic fields (only those provided) - now includes status
#             for attr, value in validated_data.items():
#                 setattr(instance, attr)
            
#             # Handle assignment changes (multiple) - FIXED: Additive unless explicitly empty
#             if assigned_to_type is not None:
#                 # Only clear if explicitly empty; otherwise append
#                 if not assigned_to_type:
#                     instance.assigned_users = []
#                     instance.assigned_groups = []
#                 else:
#                     if 'user' in assigned_to_type:
#                         if assignees:  # Append if provided
#                             if instance.assigned_users is None:
#                                 instance.assigned_users = []
#                             instance.assigned_users.extend([e for e in assignees if e not in instance.assigned_users])
#                         # Add new to watchers
#                         for email in assignees or []:
#                             try:
#                                 user = User.objects.get(email=email)
#                                 if user not in instance.watchers.all():
#                                     instance.watchers.add(user)
#                             except User.DoesNotExist:
#                                 pass
#                     if 'group' in assigned_to_type:
#                         if assigned_groups:  # Append if provided
#                             if instance.assigned_groups is None:
#                                 instance.assigned_groups = []
#                             instance.assigned_groups.extend([g for g in assigned_groups if g not in instance.assigned_groups])
#                         # Add new group members to watchers
#                         for group_id in assigned_groups or []:
#                             try:
#                                 group = UsersGroup.objects.get(id=group_id)
#                                 group_users = group.get_users()
#                                 for member in group_users:
#                                     if member not in instance.watchers.all():
#                                         instance.watchers.add(member)
#                             except UsersGroup.DoesNotExist:
#                                 pass
            
#             # Update watchers if provided (set overrides, but could be made additive)
#             if watchers is not None:
#                 instance.watchers.set(watchers)
            
#             instance.save()
#             return instance

# class TicketSLASerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TicketSLA
#         fields = [
#             'id',
#             'entity',
#             'category',
#             'subcategory',
#             'Approver_level1_user',
#             'Approver_level1_time',
#             'Approver_level2_user',
#             'Approver_level2_time',
#             'Approver_level3_user',
#             'Approver_level3_time',
#             'Approver_level4_user',
#             'Approver_level4_time',
#             'Approver_level5_user',
#             'Approver_level5_time',
#             'Assign_to',
#             'Execution_by',
#             'is_active',
#             'created_date',
#             'updated_date',
#             'created_by',
#             'updated_by',
#         ]
#         read_only_fields = ['id', 'created_date', 'updated_date']

#     def validate(self, data):
#         if data.get('is_active') not in ['Y', 'N']:
#             raise serializers.ValidationError({"is_active": "Must be 'Y' or 'N'"})
#         return data
    
class TicketEmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketEmailTemplate
        fields = '__all__'


class TicketApprovalLogSerializer(serializers.ModelSerializer):
    ticket_id = serializers.IntegerField(source='ticket.id', read_only=True)
    # ticket_no = serializers.IntegerField(read_only=True)
    ticket_no = serializers.IntegerField(source='ticket.ticket_no', read_only=True)

    status = serializers.SerializerMethodField() 

    class Meta:
        model = TicketApprovalLog
        fields = [
            'id',
            'ticket_id',
            'ticket_no',
            'status',  
            'created_by',
            'created_on',
            'approval_status',
            'approved_by',
            'approved_on',
            'comments',
            'created_at',
        ]
        read_only_fields = ['id', 'ticket_id', 'ticket_no', 'created_at']

    def get_status(self, obj):
           if hasattr(obj, 'status_detail') and obj.status_detail:
            return obj.status_detail.referrence_to
           return obj.status  
    
class HolidaySerializer(serializers.ModelSerializer):
    # Map entity_ids as list of integers
    entity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        write_only=True  # Only for input; output via entity_names
    )
    # Add entity_names field for output
    entity_names = serializers.SerializerMethodField(read_only=True)
    department_name = serializers.CharField(source="department.field_name", read_only=True)
    location_name = serializers.CharField(source="location.field_name", read_only=True)

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "description",
            "entity_ids",  # <-- Array field for input (set entities)
            "entity_names",  # <-- Array of names for output
            "department",
            "department_name",
            "location",
            "location_name",
            "status",
            "code",
            "created_on",
            "created_by",
            "created_ip",
            "modified_on",
            "modified_by",
            "modified_ip",
        ]
        read_only_fields = ["created_on", "created_by", "created_ip", "modified_on", "modified_by", "modified_ip"]

    def get_entity_names(self, obj):
        # Return list of entity names or ["No Entity"] if not set
        return obj.entity_names

    def validate(self, data):
        entity_ids = data.get('entity_ids', [])
        if not entity_ids:
            raise serializers.ValidationError({"entity_ids": "At least one entity is required."})
        # Optional: Validate entity_ids exist
        existing_entities = Entity.objects.filter(id__in=entity_ids).count()
        if existing_entities != len(entity_ids):
            raise serializers.ValidationError({"entity_ids": "Some entity IDs do not exist."})
        return data
# class HolidaySerializer(serializers.ModelSerializer):
#     entity_name = serializers.CharField(source="entity.name", read_only=True)
#     department_name = serializers.CharField(source="department.field_name", read_only=True)
#     location_name = serializers.CharField(source="location.field_name", read_only=True)

#     class Meta:
#         model = Holiday
#         fields = [
#             "id",
#             "name",
#             "date",
#             "description",
#             "entity",
#             "entity_name",
#             "department",
#             "department_name",
#             "location",
#             "location_name",
#             "status",
#             "code",
#             "created_on",
#             "created_by",
#             "created_ip",
#             "modified_on",
#             "modified_by",
#             "modified_ip",
#         ]
#         read_only_fields = ["created_on", "created_by", "created_ip", "modified_on", "modified_by", "modified_ip"]
        
# class UserRoleMappingSerializer(serializers.ModelSerializer):
#     """
#     Serializer for UserRoleMapping.
#     Handles read/write with nested read-only representations and write-only IDs.
#     """
#     user = UserSerializer(read_only=True)
#     role = RoleSerializer(read_only=True)
#     entity = EntitySerializer(read_only=True)
    
#     user_id = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.filter(is_deleted=False, is_active=True),
#         source='user',
#         write_only=True
#     )
#     role_id = serializers.PrimaryKeyRelatedField(
#         queryset=TicketsMasterConfiguration.objects.filter(field_type='Role'),
#         source='role',
#         write_only=True
#     )
#     entity_id = serializers.PrimaryKeyRelatedField(
#         queryset=Entity.objects.all(),  # Assuming Entity has no soft-delete; adjust if needed
#         source='entity',
#         write_only=True
#     )

#     class Meta:
#         model = UserRoleMapping
#         fields = [
#             'id', 'user', 'role', 'entity',
#             'user_id', 'role_id', 'entity_id',
#             'created_date', 'updated_date'
#         ]
#         read_only_fields = ['created_date', 'updated_date']

#     def validate(self, data):
#         # Optional: Ensure user belongs to the entity
#         user = data.get('user')
#         entity = data.get('entity')
#         if user and entity and user.entities_id != entity:
#             raise serializers.ValidationError(
#                 "User must belong to the specified entity."
#             )
#         return data
class UserRoleMappingSerializer(serializers.ModelSerializer):
    # Optionally, add read-only fields for the related objects' details if needed
    # user_name = serializers.CharField(source='user.name', read_only=True)
    # role_name = serializers.CharField(source='role.field_name', read_only=True)
    # entity_name = serializers.CharField(source='entity.name', read_only=True)

    class Meta:
        model = UserRoleMapping
        fields = ['id', 'user', 'role', 'entity', 'created_date', 'updated_date']
        # If you want to include nested details, add them above and adjust fields

    def validate(self, data):
        user = data.get('user')
        entity = data.get('entity')
        # Fixed: Assuming User model has 'entity_id' field (ForeignKey to Entity).
        # Change 'entity_id' to the actual field name in your User model if different.
        # Also compare to entity.id since entity is the instance.
        if user and entity and hasattr(user, 'entity_id') and user.entity_id != entity.id:
            raise serializers.ValidationError("User is not associated with this entity.")
        return data  
# class RolePermissionMappingSerializer(serializers.ModelSerializer):
#     role_id = serializers.PrimaryKeyRelatedField(queryset=TicketsMasterConfiguration.objects.filter(field_type='Role'), source='role', write_only=True)
#     entity_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), source='entity', allow_null=True, required=False, write_only=True)

#     class Meta:
#         model = RolePermissionMapping
#         fields = [
#             'id', 'role_id', 'permission_key', 'entity_id', 'is_active',
#             'created_date', 'updated_date'
#         ]
#         read_only_fields = ['created_date', 'updated_date']

#     def create(self, validated_data):
#         # Handle creation logic if needed
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         # Handle update logic if needed
#         return super().update(instance, validated_data)
# class MessageSerializer(serializers.ModelSerializer):
#     sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     ticket_no = serializers.PrimaryKeyRelatedField(queryset=CreateTicket.objects.all())
#     sender_name = serializers.ReadOnlyField(source='sender.username')
#     receiver_name = serializers.ReadOnlyField(source='receiver.username')
 
#     class Meta:
#         model = Message
#         fields = [
#             'id', 'sender', 'receiver',  
#             'sender_name', 'receiver_name',
#             'ticket_no', 'message', 'createdon'
#         ]
#         read_only_fields = ['createdon']

# class MessageSerializer(serializers.ModelSerializer):
#     sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

#     # ✅ USE ticket_no INSTEAD OF ID
#     ticket_no = serializers.SlugRelatedField(
#         queryset=CreateTicket.objects.all(),
#         slug_field='ticket_no'
#     )

#     sender_name = serializers.ReadOnlyField(source='sender.username')
#     receiver_name = serializers.ReadOnlyField(source='receiver.username')

#     class Meta:
#         model = Message
#         fields = [
#             'id', 'sender', 'receiver',
#             'sender_name', 'receiver_name',
#             'ticket_no', 'message', 'createdon'
#         ]
#         read_only_fields = ['createdon']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    ticket_no = serializers.SlugRelatedField(
        queryset=CreateTicket.objects.all(),
        slug_field='ticket_no'
    )
    sender_name = serializers.ReadOnlyField(source='sender.username')
    receiver_name = serializers.ReadOnlyField(source='receiver.username')
    protected = serializers.BooleanField(default=False)
    encrypted_message = serializers.SerializerMethodField()  # Raw encrypted (if protected)
    decrypted_message = serializers.SerializerMethodField()  # Always decrypted (no auth restriction for this field)
 
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver',
            'sender_name', 'receiver_name',
            'ticket_no', 'message', 'protected', 'encrypted_message', 'decrypted_message', 'createdon'
        ]
        read_only_fields = ['createdon']
 
    def get_encrypted_message(self, instance):
        # Always return the raw encrypted message (if protected); empty otherwise
        if instance.protected and instance.message.startswith('ENCRYPTED:'):
            return instance.message  # Full "ENCRYPTED:<token>"
        return None
 
    def get_decrypted_message(self, instance):
        # Always attempt decryption if protected (no viewer auth check; for full visibility/debug)
        if not instance.protected:
            return None
        message = instance.message
        if not message.startswith('ENCRYPTED:'):
            return None
        try:
            receiver_id = str(instance.receiver.id)
            key_material = (SECRET_KEY + receiver_id.encode()).ljust(32, b'0')[:32]
            key = base64.urlsafe_b64encode(key_material)
            fernet = Fernet(key)
            decrypted = fernet.decrypt(message[10:].encode('utf-8')).decode('utf-8')
            return decrypted
        except Exception as e:
            return f"Decryption failed: {str(e)}"
 
    def validate(self, data):
        # Ensure ticket_no is provided and valid
        if not data.get('ticket_no'):
            raise serializers.ValidationError({"ticket_no": "Ticket is required."})
        # Ensure receiver is valid
        if not data.get('receiver'):
            raise serializers.ValidationError({"receiver": "Receiver is required."})
        return data
 
    def create(self, validated_data):
        # If protected, encrypt the message before saving
        message_text = validated_data['message']
        protected = validated_data.get('protected', False)
        if protected:
            # Derive key from receiver ID + secret (simple symmetric; in prod, use asymmetric for true privacy)
            receiver_id = str(validated_data['receiver'].id)
            key_material = (SECRET_KEY + receiver_id.encode()).ljust(32, b'0')[:32]  # Pad/truncate to 32 bytes
            key = base64.urlsafe_b64encode(key_material)
            fernet = Fernet(key)
            encrypted_message = fernet.encrypt(message_text.encode('utf-8')).decode('utf-8')
            validated_data['message'] = f"ENCRYPTED:{encrypted_message}"  # Prefix to indicate encrypted
        instance = super().create(validated_data)
        return instance
 
    def to_representation(self, instance):
        # On read, set message: Decrypted (if authorized) or masked (privacy for main 'message' field)
        data = super().to_representation(instance)
        message = instance.message
        protected = instance.protected
        request = self.context.get('request')
        if protected and request and request.user.id == instance.receiver.id:
            # Decrypt for authorized receiver
            if message.startswith('ENCRYPTED:'):
                try:
                    receiver_id = str(instance.receiver.id)
                    key_material = (SECRET_KEY + receiver_id.encode()).ljust(32, b'0')[:32]
                    key = base64.urlsafe_b64encode(key_material)
                    fernet = Fernet(key)
                    decrypted = fernet.decrypt(message[10:].encode('utf-8')).decode('utf-8')  # Remove prefix
                    data['message'] = decrypted
                except Exception:
                    data['message'] = "Decryption failed (invalid key or corrupted)."
            data['protected'] = False  # Hide protected flag after decryption
        elif protected and message.startswith('ENCRYPTED:'):
            # Mask for unauthorized (admin, etc.)
            data['message'] = "*** PROTECTED MESSAGE - VISIBLE ONLY TO RECEIVER ***"
        # Always add encrypted/decrypted fields (decrypted always succeeds for visibility)
        data['encrypted_message'] = self.get_encrypted_message(instance)
        data['decrypted_message'] = self.get_decrypted_message(instance)
        return data
 
class PlatformSerializer(serializers.ModelSerializer):
    entity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[],
        write_only=True
    )

    entity_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TicketsMasterConfiguration
        fields = [
            "id",
            "entity_ids",
            "entity_names",
            "field_type",
            "field_name",
            "field_values",
            "is_mandatory",
            "is_active",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def get_entity_names(self, obj):
        return obj.entity_names

    def create(self, validated_data):
        validated_data["field_type"] = "Platform"
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["field_type"] = "Platform"
        return super().update(instance, validated_data)

