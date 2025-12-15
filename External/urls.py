# urls.py (Add to your app's urls.py; include in main urls.py as path('api/tickets/', include('yourapp.urls')))
from django.urls import path
from .views import TicketPanelCreateView, TicketPanelListView, TicketPanelRetrieveView



urlpatterns = [
    path('ticket-panel/create/', TicketPanelCreateView.as_view(), name='ticket-panel-create'),
    path('ticket-panel/list/', TicketPanelListView.as_view(), name='ticket-panel-list'),  
    path('ticket-panel/<int:pk>/', TicketPanelRetrieveView.as_view(), name='ticket-panel-detail'),  
]