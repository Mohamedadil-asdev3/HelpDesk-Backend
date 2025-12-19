from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime,timedelta
# from Authenticate.models import UsersGroup
# from django.contrib.auth import get_user_model
USER = 'Authenticate.User'

# from Authenticate.models import User 
class Role(models.Model):
    """
    Dedicated model for roles in the ticketing system.
    Replaces using TicketsMasterConfiguration with field_type='Role'.
    """
    rolename = models.CharField(max_length=100, unique=True)  # e.g., 'superadmin', 'technician', 'user'
    code = models.CharField(max_length=50, unique=True, help_text="Short code for the role, e.g., 'SA' for superadmin")
    is_active = models.CharField(max_length=1, default='Y', db_column='is_active')  # 'Y'/'N'
    created_date = models.DateTimeField(db_column='created_date', auto_now_add=True)  
    created_by = models.CharField(max_length=255, db_column='created_by')
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_created_by')  # Uncomment if switching to FK
    updated_by = models.CharField(max_length=255, db_column='updated_by')
    updated_date = models.DateTimeField(db_column='updated_date', auto_now=True)  # Changed: Updates on every save

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        db_table = 'master_roles'
        ordering = ['rolename']

    def __str__(self):
        return self.rolename

    def save(self, *args, **kwargs):
        # Removed: self.created_on = timezone.now() (field doesn't exist; auto_now_add handles it)
        super().save(*args, **kwargs)
        
class RoleEntitymapping(models.Model):
    """
    Mapping table for Role-Entity associations.
    """
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='entity_mappings', db_column='role_id')
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE, related_name='role_mappings', db_column='entity_id')
    created_date = models.DateTimeField(auto_now_add=True, db_column='created_date')
    updated_date = models.DateTimeField(auto_now=True, db_column='updated_date')

    class Meta:
        db_table = 'role_entity_mapping'
        unique_together = ('role', 'entity')
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.role.rolename} - {self.entity.name}"
# class TicketsMasterConfiguration(models.Model):
#     id = models.AutoField(primary_key=True)
#     field_type = models.CharField(max_length=50, db_column='field_type')
#     referrence_to = models.CharField(max_length=45, db_column='referrence_to', null=True, blank=True)
#     field_name = models.CharField(max_length=250, db_column='field_name')
#     field_values = models.CharField(max_length=250, db_column='field_values', blank=True, null=True)
#     is_mandatory = models.CharField(max_length=5, db_column='is_mandatory',null=True,blank=True)
#     is_active = models.CharField(max_length=1, default='Y', db_column='is_active')
#     created_date = models.DateTimeField(db_column='created_date',auto_now_add=True)
#     created_by = models.CharField(max_length=255, db_column='created_by')
#     # created_by =  models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True,related_name='%(class)s_created_by')
#     updated_by = models.CharField(max_length=255, db_column='updated_by')
#     updated_date = models.DateTimeField(db_column='updated_date',auto_now_add=True)
#     entity = models.ForeignKey(
#         'Entity',
#         on_delete=models.CASCADE,
#         db_column='entity_id',
#         related_name='master_configurations',
#         null=True
#     )

#     class Meta:
#         db_table = 'tickets_master_configuration'

#     def __str__(self):
#         return f"{self.field_type}: {self.referrence_to} -> {self.field_name}"
class TicketsMasterConfiguration(models.Model):
    id = models.AutoField(primary_key=True)
    field_type = models.CharField(max_length=50, db_column='field_type')
    referrence_to = models.CharField(max_length=45, db_column='referrence_to', null=True, blank=True)
    field_name = models.CharField(max_length=250, db_column='field_name')
    field_values = models.CharField(max_length=250, db_column='field_values', blank=True, null=True)
    # JSONField for entity IDs (MySQL-compatible; stores as JSON array)
    # Requires MySQL 5.7+ for native JSON support
    entity_ids = models.JSONField(
        default=list,
        blank=True,
        null=True,
        db_column='entity_ids'  # Custom db_column if needed; adjust migration accordingly
    )
    is_mandatory = models.CharField(max_length=5, db_column='is_mandatory', null=True, blank=True)
    is_active = models.CharField(max_length=1, default='Y', db_column='is_active')
    created_date = models.DateTimeField(db_column='created_date', auto_now_add=True)
    created_by = models.CharField(max_length=255, db_column='created_by')
    updated_by = models.CharField(max_length=255, db_column='updated_by')
    updated_date = models.DateTimeField(db_column='updated_date', auto_now_add=True)
    # Retain original entity for backward compatibility if needed, or remove it
    # entity = models.ForeignKey('Entity', on_delete=models.CASCADE, db_column='entity_id', related_name='master_configurations', null=True)

    class Meta:
        db_table = 'tickets_master_configuration'

    def __str__(self):
        return f"{self.field_type}: {self.referrence_to} -> {self.field_name}"

    @property
    def entity_names(self):
        # Fetch names based on entity_ids (no dynamic import; assume Entity is accessible)
        if self.entity_ids:
            try:
                # Adjust import/path as needed; assuming Entity is in scope (same file or imported at top)
                entities = Entity.objects.filter(id__in=self.entity_ids)
                return [entity.name for entity in entities if entity.name]
            except NameError:
                # Fallback if Entity not in scope (temporary; fix import)
                return ["Entity Unavailable"]
        return ["No Entity"]
    
# class Entity(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     display_name = models.TextField(blank=True, null=True)
#     address = models.CharField(max_length=500, blank=True, null=True)
#     logo = models.ImageField(upload_to='entity_logos/', blank=True, null=True)  # changed
#     contact_email = models.EmailField(max_length=100, blank=True, null=True)
#     location = models.ForeignKey('TicketsMasterConfiguration',on_delete=models.SET_NULL,null=True,
#     blank=True,db_column='location',related_name='entities')
#     created_date = models.DateTimeField(blank=True, null=True)
#     created_by = models.CharField(max_length=255, blank=True, null=True)
#     updated_by = models.CharField(max_length=255, blank=True, null=True)
#     updated_date = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         db_table = 'tickets_entity'

#     def __str__(self):
#         return self.name
class Entity(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    display_name = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    logo = models.ImageField(upload_to='entity_logos/', blank=True, null=True)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.SET_NULL, null=True,
                                 blank=True, db_column='location', related_name='entities')
    # roles = models.ManyToManyField('Role', blank=True, related_name='entities')  # Added ManyToMany for multiple roles
    
    is_active = models.BooleanField(default=True)  # Added for soft delete
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'tickets_entity'

    def __str__(self):
        return self.name    

class TicketCategory(models.Model):
    id = models.AutoField(primary_key=True)
    entity= models.ForeignKey(Entity, on_delete=models.CASCADE, db_column='entity_id')
    department = models.ForeignKey(
        TicketsMasterConfiguration,
        on_delete=models.CASCADE,blank=True, null=True,
        db_column='department_id'
    )
    category_name = models.CharField(max_length=255, blank=True, null=True)
    category_description = models.CharField(max_length=500, null=True,blank=True)
    is_active = models.CharField(max_length=25, default="Y")
    created_date = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tickets_category"



class TicketSubcategory(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, db_column='entity_id')
    category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE, db_column='category_id')
    subcategory_name = models.TextField(blank=True, null=True)
    subcategory_description = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.CharField(max_length=25, default='Y')
    created_date = models.DateTimeField(blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    updated_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'tickets_subcategory'

    def __str__(self):
        return self.subcategory_name or ''
    


# class CreateTicket(models.Model):
#     id = models.AutoField(primary_key=True)
#     ticket_no = models.PositiveIntegerField(unique=True, editable=False)
#     type = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='type')
#     department = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True , related_name='department')
#     location = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='location')
#     priority = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='priority')
#     status = models.ForeignKey('TicketsMasterConfiguration',on_delete=models.CASCADE,related_name='status',null=True,blank=True)
#     sla = models.ForeignKey('TicketSLA',on_delete=models.SET_NULL,null=True,blank=True,related_name='tickets')

#     requested = models.ForeignKey(settings.AUTH_USER_MODEL,   on_delete=models.PROTECT,related_name='tickets_requested',db_index=True,null=True, blank=True,db_column='requested_id' )
#     entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
#     category = models.ForeignKey(
#     TicketCategory,
#     on_delete=models.CASCADE,
#     related_name='tickets',
#     db_column='category_id',      # keeps your DB column name
#     db_constraint=False           # important if data already exists
#     )
#     subcategory = models.ForeignKey(
#         TicketSubcategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='tickets',
#         db_column='subcategory_id',
#         db_constraint=False
#     )
#     title = models.CharField(max_length=255)
#     description = models.TextField(null=False, blank=False)
#     # watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watched_tickets', blank=True)
#     watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="watched_tickets", blank=True)
#     assigned_group = models.ForeignKey(
#         'Authenticate.UsersGroup',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='watcher_tickets'
#     )
#     assignee = models.CharField(max_length=255, blank=True, null=True)
#     created_date = models.DateTimeField(auto_now_add=True)  
#     updated_date = models.DateTimeField(auto_now=True)
#     closed_on = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         db_table = "tickets_createtickets"

#     def save(self, *args, **kwargs):
#         if not self.ticket_no:
#             last_ticket = CreateTicket.objects.order_by('-id').first()
#             self.ticket_no = (last_ticket.ticket_no + 1) if last_ticket else 1
#         super().save(*args, **kwargs)
class CreateTicket(models.Model):
    id = models.AutoField(primary_key=True)
    ticket_no = models.PositiveIntegerField(unique=True, editable=False)
    type = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='type')
    department = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True , related_name='department')
    location = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='location')
    platform = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='platform_tickets')
    priority = models.ForeignKey('TicketsMasterConfiguration', on_delete=models.CASCADE, null=True, blank=True ,related_name='priority')
    status = models.ForeignKey('TicketsMasterConfiguration',on_delete=models.CASCADE,related_name='status',null=True,blank=True)
    sla = models.ForeignKey('TicketSLA',on_delete=models.SET_NULL,null=True,blank=True,related_name='tickets')

    requested = models.ForeignKey(settings.AUTH_USER_MODEL,   on_delete=models.PROTECT,related_name='tickets_requested',db_index=True,null=True, blank=True,db_column='requested_id' )
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(
    TicketCategory,
    on_delete=models.CASCADE,
    related_name='tickets',
    db_column='category_id',      # keeps your DB column name
    db_constraint=False           # important if data already exists
    )
    subcategory = models.ForeignKey(
        TicketSubcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        db_column='subcategory_id',
        db_constraint=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=False, blank=False)
    watchers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="watched_tickets", blank=True)
    
    # Array fields for multiple assignments (JSONField)
    assigned_users = models.JSONField(default=list, blank=True)  # List of emails
    assigned_groups = models.JSONField(default=list, blank=True)  # List of group IDs
    
    # Legacy fields - keep for backward compatibility
    assignee = models.CharField(max_length=255, blank=True, null=True)
    assigned_group = models.ForeignKey(
        'Authenticate.UsersGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_assigned_tickets'
    )
    
    created_date = models.DateTimeField(auto_now_add=True)  
    updated_date = models.DateTimeField(auto_now=True)
    closed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tickets_createtickets"

    def save(self, *args, **kwargs):
        if not self.ticket_no:
            last_ticket = CreateTicket.objects.order_by('-id').first()
            self.ticket_no = (last_ticket.ticket_no + 1) if last_ticket else 1
        super().save(*args, **kwargs)
class TicketDocument(models.Model):
    id = models.AutoField(primary_key=True)
    ticket = models.ForeignKey(CreateTicket, related_name="documents", on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to="ticket_documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tickets_documents"

class Message(models.Model):
    sender = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    ticket_no = models.ForeignKey(
        CreateTicket,
        on_delete=models.CASCADE,
        related_name='ticket_messages'
    )
    message = models.TextField(max_length=500)
    createdon = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'transaction_messages'
        ordering = ['-createdon']
 
    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.message[:50]}"
class TicketEmailTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    email_event = models.CharField(max_length=45)
    email_template = models.TextField()  # longtext → TextField in Django
    is_active = models.CharField(max_length=25, default='Y')

    class Meta:
        db_table = 'ticket_email_templates'
        verbose_name = 'Ticket Email Template'
        verbose_name_plural = 'Ticket Email Templates'

    def __str__(self):
        return f"{self.email_event} ({'Active' if self.is_active == 'Y' else 'Inactive'})"
    
class TicketSLA(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey('Entity', on_delete=models.CASCADE, related_name='sla_entities', db_column='entity_id')
    category = models.ForeignKey('TicketCategory', on_delete=models.CASCADE, related_name='sla_categories', null=True, blank=True, db_column='category_id')
    subcategory = models.ForeignKey('TicketSubcategory', on_delete=models.CASCADE, related_name='sla_subcategories', null=True, blank=True, db_column='subcategory_id')

    Approver_level1_user = models.ForeignKey(USER,on_delete=models.CASCADE, related_name='Approver_level1_user', null=True)
    Approver_level1_time = models.CharField(max_length=150, null=True, blank=True)
    Approver_level2_user = models.ForeignKey(USER,on_delete=models.CASCADE, related_name='Approver_level2_user', null=True)
    Approver_level2_time = models.CharField(max_length=150, null=True, blank=True)
    Approver_level3_user = models.ForeignKey(USER,on_delete=models.CASCADE, related_name='Approver_level3_user', null=True)
    Approver_level3_time = models.CharField(max_length=150, null=True, blank=True)
    Approver_level4_user = models.ForeignKey(USER,on_delete=models.CASCADE, related_name='Approver_level4_user', null=True)
    Approver_level4_time = models.CharField(max_length=150, null=True, blank=True)
    Approver_level5_user = models.ForeignKey(USER,on_delete=models.CASCADE, related_name='Approver_level5_user', null=True)
    Approver_level5_time = models.CharField(max_length=150, null=True, blank=True)

    Assign_to = models.CharField(max_length=150, null=True, blank=True)
    Execution_by = models.CharField(max_length=150, null=True, blank=True)
    # on_hold = models.BooleanField(default=False)
    # on_hold_start = models.DateTimeField(null=True, blank=True)
    is_active = models.CharField(max_length=25, default='Y')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
  
    class Meta:
        db_table = 'tickets_sla'
        verbose_name = "Ticket SLA"
        verbose_name_plural = "Tickets SLA"

    def __str__(self):
        return f"SLA for {self.category} - {self.subcategory}"



class TicketApprovalLog(models.Model):

    ticket = models.ForeignKey(
        'CreateTicket',
        on_delete=models.CASCADE,
        related_name='approval_logs'
    )
    sla = models.ForeignKey(
        'TicketSLA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_logs'
    )

    is_current_level = models.BooleanField(default=False)
    sla_breach = models.BooleanField(default=False)
    current_level = models.IntegerField(default=1)

    status = models.CharField(max_length=100, null=True, blank=True)
    approval_status = models.CharField(max_length=50, null=True, blank=True)

    created_by = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='created_approval_logs'
    )
    approved_by = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='approved_approval_logs',
        null=True,
        blank=True
    )
    created_on = models.DateTimeField(null=True, blank=True)
    approved_on = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ NEW FIELDS
    onhold_start = models.DateTimeField(null=True, blank=True)
    total_onhold_seconds = models.IntegerField(default=0) 
    sla_end_time = models.DateTimeField(null=True, blank=True) 
    remaining_sla_seconds = models.PositiveIntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = 'tickets_approval_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"Log #{self.id} - Ticket #{self.ticket.ticket_no if self.ticket else 'N/A'}"

    

    

class UserRoleMapping(models.Model):
    """
    Mapping table for User-Role-Entity associations.
    Role is a TicketsMasterConfiguration with field_type='Role'.
    """
    user = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name='role_mappings',
        db_column='user_id'
    )
    role = models.ForeignKey(
        TicketsMasterConfiguration,
        on_delete=models.CASCADE,
        limit_choices_to={'field_type': 'Role'},
        related_name='user_mappings',
        db_column='role_id',
        null=True,
        blank=True
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='user_role_mappings',
        db_column='entity_id'
    )
    created_date = models.DateTimeField(auto_now_add=True, db_column='created_date')
    updated_date = models.DateTimeField(auto_now=True, db_column='updated_date')

    class Meta:
        db_table = 'user_role_mapping'
        unique_together = ('user', 'role', 'entity')
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.user.name} - {self.role.field_name} - {self.entity.name}"
    

class Holiday(models.Model):
    # entity_ids for multiple entities (JSONField for MySQL)
    entity_ids = models.JSONField(
        default=list,
        blank=True,
        null=True,
        db_column='entity_ids'
    )
    department = models.ForeignKey(
        TicketsMasterConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='holiday_departments'  
    )
    location = models.ForeignKey(
        TicketsMasterConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='holiday_locations' 
    )
    # Removed single entity FK; use entity_ids instead
    name = models.CharField(max_length=100, null=True, blank=True)  
    date = models.DateField()  
    description = models.TextField(blank=True, null=True)  
    status = models.SmallIntegerField(choices=((1, 'Active'), (2, 'Inactive'), (3, 'Delete')))  
    created_on = models.DateTimeField(auto_now_add=True)  
    created_by = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_created_by') 
    created_ip = models.GenericIPAddressField(null=True) 
    modified_on = models.DateTimeField(auto_now=True)  
    modified_by = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True, null=True, related_name='%(class)s_modified_by') 
    modified_ip = models.GenericIPAddressField(blank=True, null=True)  
    code = models.CharField(max_length=15, db_index=True, null=True)  
    
    def __str__(self):
        return self.name  # Returning the holiday name for representation

    @property
    def entity_names(self):
        if self.entity_ids:
            entities = Entity.objects.filter(id__in=self.entity_ids)
            return [entity.name for entity in entities if entity.name]
        return ["No Entity"]

    class Meta:
        db_table = 'master_holiday'  # Specifying the database table name
        verbose_name = 'Holiday'  # Singular representation in admin
        verbose_name_plural = 'Holidays'  # Plural representation in admin
