from rest_framework import generics, permissions
from .models import Adventure, Location, Choice
from .serializers import AdventureSerializer, LocationSerializer, ChoiceSerializer
from rest_framework.exceptions import PermissionDenied

# PRZYGODY (Adventure)
class AdventureListCreateView(generics.ListCreateAPIView):
    queryset = Adventure.objects.all()
    serializer_class = AdventureSerializer
    permission_classes = [permissions.IsAuthenticated]  # Zalogowani użytkownicy mogą tworzyć

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)  # Automatycznie przypisuje twórcę

class AdventureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Adventure.objects.all()
    serializer_class = AdventureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.creator != self.request.user:
            raise PermissionDenied("You do not have permission to edit this adventure.")
        return obj
    
    def perform_update(self, serializer):
        # Zapobiegamy zmianie twórcy
        if 'creator' in self.request.data:
            raise PermissionDenied("You cannot change the creator of this adventure.")
        super().perform_update(serializer)

# LOKACJE (Location)
class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        adventure_id = self.request.data.get('adventure')
        # Sprawdzamy, czy przygoda istnieje
        if not Adventure.objects.filter(id=adventure_id).exists():
            raise PermissionDenied("The adventure does not exist.")
        try:
            adventure = Adventure.objects.get(id=adventure_id)
        except Adventure.DoesNotExist:
            raise PermissionDenied("The adventure does not exist.")
        serializer.save(adventure=adventure)

class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.adventure.creator != self.request.user:
            raise PermissionDenied("You do not have permission to edit this location.")
        return obj

    def perform_update(self, serializer):
        # Zapobiegamy zmianie przygody (adventure)
        if 'adventure' in self.request.data:
            raise PermissionDenied("You cannot change the associated adventure.")
        super().perform_update(serializer)

# WYBORY (Choice)
class ChoiceListCreateView(generics.ListCreateAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):        
        location_id = self.request.data.get('location')
        # Sprawdzamy, czy lokalizacja istnieje
        if not Location.objects.filter(id=location_id).exists():
            raise PermissionDenied("The location does not exist.")
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise PermissionDenied("The location does not exist.")
        serializer.save(location=location)

class ChoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.location.adventure.creator != self.request.user:
            raise PermissionDenied("You do not have permission to edit this choice.")
        return obj
    
