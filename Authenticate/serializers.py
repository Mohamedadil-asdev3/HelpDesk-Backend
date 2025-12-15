from rest_framework import serializers
from .models import User,UsersGroup
from Ticket.models import Entity,TicketsMasterConfiguration
from django.contrib.auth.hashers import make_password

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         exclude = ["password"]   

#     def create(self, validated_data):
#         if 'password' in validated_data:
#             validated_data['password'] = make_password(validated_data['password'])
#         return super().create(validated_data)

# class UsersGroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UsersGroup
#         fields = "__all__"


# class WatcherUserSerializer(serializers.ModelSerializer):
#     department = serializers.CharField(source='department_id.field_name', read_only=True)
#     location = serializers.CharField(source='locations.field_name', read_only=True)
#     entity = serializers.CharField(source='entities_id.entity_name', read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "name",
#             "realname",
#             "email",
#             "department",
#             "location",
#             "entity",
#             "is_hod",
#             "is_active",
#         ]


class WatcherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'realname', 'email', 'groups_id']


class UsersGroupSerializer(serializers.ModelSerializer):
    entity_name = serializers.SerializerMethodField()
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    users = WatcherUserSerializer(many=True, read_only=True, source='get_users')

    class Meta:
        model = UsersGroup
        fields = [
            'id', 'name', 'comment', 'entities_id', 'entity_name',
            'is_recursive',
            'user_ids', 'users'
        ]

    # ✅ Readable Entity name
    def get_entity_name(self, obj):
        if obj.entities_id:
            entity = Entity.objects.filter(id=obj.entities_id).first()
            return entity.name if entity else None
        return None

    # ✅ When creating a group, assign users if provided
    def create(self, validated_data):
        user_ids = validated_data.pop('user_ids', [])
        group = UsersGroup.objects.create(**validated_data)

        if user_ids:
            User.objects.filter(id__in=user_ids).update(groups_id=group.id)

        return group

    # ✅ When updating, reassign users
    def update(self, instance, validated_data):
        user_ids = validated_data.pop('user_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if user_ids is not None:
            # Unassign old users safely (set to 0 instead of NULL)
            User.objects.filter(groups_id=instance.id).update(groups_id=0)
            # Assign new users
            User.objects.filter(id__in=user_ids).update(groups_id=instance.id)

        return instance


   

    
    # class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, required=False)
    # entity_name = serializers.SerializerMethodField()
    # location_name = serializers.SerializerMethodField()
    # department_name = serializers.SerializerMethodField()
    # locations_id = serializers.PrimaryKeyRelatedField(
    #     queryset=TicketsMasterConfiguration.objects.filter(field_type='Location'),
    #     source='locations',
    #     allow_null=True,
    #     required=False
    # )

    # class Meta:
    #     model = User
    #     fields = [
    #         "id",
    #         "name",
    #         "firstname",
    #         "realname",
    #         "email",
    #         "entities_id",
    #         "entity_name",
    #         "locations_id",
    #         "location_name",
    #         "department_id",
    #         "department_name",
    #         "is_hod",
    #         "is_active",
    #         "password",
    #     ]

    # def get_entity_name(self, obj):
    #     try:
    #         return obj.entities_id.name if obj.entities_id else None
    #     except Entity.DoesNotExist:
    #         return None

    # def get_location_name(self, obj):
    #     try:
    #         return obj.locations.field_name if obj.locations else None
    #     except TicketsMasterConfiguration.DoesNotExist:
    #         return None

    # def get_department_name(self, obj):
    #     try:
    #         return obj.department_id.field_name if obj.department_id else None
    #     except TicketsMasterConfiguration.DoesNotExist:
    #         return None

    # # -----------------------