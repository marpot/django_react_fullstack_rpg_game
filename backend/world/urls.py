from django.urls import path
from .views import  (
    AdventureListCreateView, AdventureDetailView,
    LocationListCreateView, LocationDetailView,
    ChoiceListCreateView, ChoiceDetailView
)

urlpatterns = [
    path('', AdventureListCreateView.as_view(), name='adventure-list-create'),
    path('<int:pk>/', AdventureDetailView.as_view(), name='adventure-detail'),
    
    path('locations/', LocationListCreateView.as_view(), name='location-list-create'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location-detail'),
    
    path('choices/', ChoiceListCreateView.as_view(), name='choice-list-create'),
    path('choices/<int:pk>/', ChoiceDetailView.as_view(), name='choice-detail'),
]