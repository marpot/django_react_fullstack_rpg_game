from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Adventure, Location, Choice
from .serializers import AdventureSerializer, LocationSerializer, ChoiceSerializer

from world.factories.adventure_factory import AdventureFactory


# PRZYGODY (Adventure)
class AdventureListCreateView(generics.ListCreateAPIView):
    queryset = Adventure.objects.all()
    serializer_class = AdventureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


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
        if 'creator' in self.request.data:
            raise PermissionDenied("You cannot change the creator of this adventure.")
        super().perform_update(serializer)


# =========================
# 🎲 GENERATOR PRZYGODY
# =========================

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def generate_adventure(request):
    adventure = AdventureFactory.generate(
        creator=request.user
    )

    serializer = AdventureSerializer(adventure)

    return Response(serializer.data)


# LOKACJE (Location)
class LocationListCreateView(generics.ListCreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        adventure_id = self.request.data.get('adventure')

        if not Adventure.objects.filter(id=adventure_id).exists():
            raise PermissionDenied("The adventure does not exist.")

        adventure = Adventure.objects.get(id=adventure_id)
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

        if not Location.objects.filter(id=location_id).exists():
            raise PermissionDenied("The location does not exist.")

        location = Location.objects.get(id=location_id)
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