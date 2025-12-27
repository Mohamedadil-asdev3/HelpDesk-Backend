from django.urls import path
from .views import (
    # GlpiUser,
    TicketsMasterConfigurationView,
    TicketCategoryListCreateView,
    TicketCategoryRetrieveUpdateView,
    TicketSubcategoryListCreateView,
    TicketSubcategoryRetrieveUpdateView,
    CreateTicketView,
    EntityAPIView,LocationByCountryAPIView,
    # SLAByEntityCategoryAPIView,
    DepartmentAPIView,UserManagementAPIView,
    TicketSLAListCreateView,
    TicketSLADetailView,TicketEmailTemplateListCreateView,
    TicketEmailTemplateDetailView,TicketSLAHomeScreenView,
    TicketSLAByIdView,WatcherGroupListCreateView,WatcherGroupDetailView,
    WatcherUserListView,HolidayAPIView,UpcomingHolidayAPIView,
    TicketView,HodUserAPIView,RoleAPIView,OverallStatusView,UserStatusView,TicketActionView,
    WatcherStatusView,UserRoleMappingAPIView,CEODashboardAPIView,MessageListCreateView,
    MessageDetailView,UserMessagesView,PlatformAPIView,ApproverTicketView,AdminTicketView,
    DeleteTicketDocumentView, TicketSLAsWithNestedView,AdminTicketMessagesView
    # HodUserAPIView
    
)
# from Approval.analyse import GlpiUsers
# from Helpdesk.analyse import CeoApprovalDashboard,HODApprovalDashboardAPI

urlpatterns = [
     path('configurations/', TicketsMasterConfigurationView.as_view(), name='tickets-master-configuration'),

    path('entities/', EntityAPIView.as_view(), name='entity-list-create'),

    path('ticket-categories/', TicketCategoryListCreateView.as_view(), name='ticket-category-list-create'),
    path('ticket-categories/<int:pk>/', TicketCategoryRetrieveUpdateView.as_view(), name='ticket-category-retrieve-update'),

    path('subcategories/', TicketSubcategoryListCreateView.as_view(), name='ticket-subcategory-list-create'),
    path('subcategories/<int:pk>/', TicketSubcategoryRetrieveUpdateView.as_view(), name='ticket-subcategory-retrieve-update'),
    
    path('tickets/', CreateTicketView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', CreateTicketView.as_view(), name='ticket-update'),
    path('tickets/<str:pk>/', CreateTicketView.as_view(), name='ticket-update'),

    path('tickets/documents/<int:pk>/', DeleteTicketDocumentView.as_view(), name='delete-document'),

    path('locations/', LocationByCountryAPIView.as_view(), name='locations-by-country'),
    path('locations/<int:pk>/', LocationByCountryAPIView.as_view(), name='location-detail'),

    path('ticket-slas/', TicketSLAListCreateView.as_view(), name='ticket-sla-list-create'),
    path('ticket-slas/<int:pk>/', TicketSLADetailView.as_view(), name='ticket-sla-detail'),
    path('slas/home/', TicketSLAHomeScreenView.as_view(), name='sla-home'),
    path('slas/<int:sla_id>/', TicketSLAByIdView.as_view(), name='ticket-sla-by-id'),
    path("watcher-groups/", WatcherGroupListCreateView.as_view(), name="watcher-groups"),
    path("watcher-groups/<int:pk>/", WatcherGroupDetailView.as_view(), name="watcher-group-detail"),
    path("watcher-users/", WatcherUserListView.as_view(), name="watcher-users"),

    path('holidays/', HolidayAPIView.as_view(), name='holiday-list-create'),
    path('holidays/<int:pk>/', HolidayAPIView.as_view(), name='holiday-detail'),
    path('holidays/upcoming/', UpcomingHolidayAPIView.as_view(), name='holiday-upcoming'),
    path('roles/', RoleAPIView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleAPIView.as_view(), name='role-update-delete'),
    path('categories-full/', TicketSLAsWithNestedView.as_view(), name='ticket-categories-full'),
 
    path('ticket/count/',TicketView.as_view(), name='ticket'),
    path('approver/count/',ApproverTicketView.as_view(), name='approver-ticket'),
    path('admin/count/',AdminTicketView.as_view(), name='admin-ticketview'),
    # path('sla/', SLAByEntityCategoryAPIView.as_view(), name='sla-by-entity'),
    path('entities/<int:pk>/', EntityAPIView.as_view()),
    path('hod-users/', HodUserAPIView.as_view(), name='hod-users'),
    path('ceo-dashboard/', CEODashboardAPIView.as_view(), name='ceo-dashboard'),
    

    path('departments/', DepartmentAPIView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentAPIView.as_view(), name='department-update-delete'),

    path('users/', UserManagementAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserManagementAPIView.as_view(), name='user-update-delete'),
    

    path('tickets/<int:ticket_no>/action/', TicketActionView.as_view(), name='ticket-action'),

    path('ticket-email-templates/', TicketEmailTemplateListCreateView.as_view(), name='ticket-email-templates'),
    path('ticket-email-templates/<int:pk>/', TicketEmailTemplateDetailView.as_view(), name='ticket-email-template-detail'),
    
    path('user-role-mappings/', UserRoleMappingAPIView.as_view(), name='user-role-mapping-list-create'),
    path('user-role-mappings/<int:pk>/', UserRoleMappingAPIView.as_view(), name='user-role-mapping-detail'),
    
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
   
    # Retrieve/update/delete single message by ID
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
   
    # Custom: User-specific messages (GET/POST for userid)
    path('users/<int:userid>/messages/', UserMessagesView.as_view(), name='user-messages'),
    path('users/<int:userid>/messages/<int:ticket_id>/', UserMessagesView.as_view(), name='user-ticket-messages'),
    
    path('admin/ticket-messages/<str:ticket_no>/', AdminTicketMessagesView.as_view(), name='admin-ticket-messages'),
    # path('admin/ticket-messages/<int:ticket_no>/', AdminTicketMessagesView.as_view(), name='admin-ticket-messages'),
    # path('role-permissions/', RolePermissionMappingAPIView.as_view(), name='role-permission-list-create'),
    # path('role-permissions/<int:pk>/', RolePermissionMappingAPIView.as_view(), name='role-permission-update-delete'),
    # Ticket/urls.py  → CORRECT LINE
#    path('ceo-approval/', CeoApprovalDashboard.as_view(), name='CeoApprovalDashboard'),
#    path('hod-dashboard/', HODApprovalDashboardAPI.as_view(), name='hod_dashboard'),
   path("platform/", PlatformAPIView.as_view()),
   path("platform/<int:pk>/", PlatformAPIView.as_view()),
   
]  

# from django.urls import path
# from .views import (
#     TicketsMasterConfigurationView,
#     TicketCategoryListCreateView,
#     TicketCategoryRetrieveUpdateView,
#     TicketSubcategoryListCreateView,
#     TicketSubcategoryRetrieveUpdateView,
#     CreateTicketView,EntityAPIView,ApproveTicketView
# )

# urlpatterns = [
#     path('configurations/', TicketsMasterConfigurationView.as_view(), name='tickets-master-configuration'),
#     path('ticket-categories/', TicketCategoryListCreateView.as_view(), name='ticket-category-list-create'),
#     path('ticket-categories/<int:pk>/', TicketCategoryRetrieveUpdateView.as_view(), name='ticket-category-retrieve-update'),
#     path('subcategories/', TicketSubcategoryListCreateView.as_view(), name='ticket-subcategory-list-create'),
#     path('subcategories/<int:pk>/', TicketSubcategoryRetrieveUpdateView.as_view(), name='ticket-subcategory-retrieve-update'),
#     path('tickets/', CreateTicketView.as_view(), name='ticket-list'),
#     path('tickets/<int:pk>/', CreateTicketView.as_view(), name='ticket-detail'),
#     path('tickets/approve/', ApproveTicketView.as_view(), name='ticket-approve'),
#     path('entity/', EntityAPIView.as_view(), name='entity-api'),
# ]
