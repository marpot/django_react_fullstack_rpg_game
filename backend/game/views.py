from django.shortcuts import render
from rest_framework import viewsets, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GameSession, GameEvent
from .serializers import GameSessionSerializer, GameEventSerializer

class GameSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet do zarządzania sesjami gry.
    ModelViewSet automatycznie tworzy wszystkie endpointy CRUD:
    - GET /api/sessions/ - lista wszystkich sesji
    - POST /api/sessions/ - tworzenie nowej sesji
    - GET /api/sessions/{id}/ - szczegóły sesji
    - PUT/PATCH /api/sessions/{id}/ - aktualizacja sesji
    - DELETE /api/sessions/{id}/ - usunięcie sesji
    """
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

class GameEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet do zarządzania zdarzeniami w grze.
    Rozszerza ModelViewSet o dodatkowe funkcje filtrowania i wyszukiwania.
    """
    queryset = GameEvent.objects.all()
    serializer_class = GameEventSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'event_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        """
        Nadpisuje domyślną metodę do pobierania danych.
        Pozwala na filtrowanie zdarzeń po różnych parametrach.

        Przykłady użycia:
        - /api/events/?player=1 - zdarzenia dla konkretnego gracza
        - /api/events/?adventure=1 - zdarzenia dla konkretnej przygody
        - /api/events/?event_type=story - zdarzenia określonego typu
        """
        queryset = GameEvent.objects.all()
        player_id = self.request.query_params.get('player', None)
        adventure_id = self.request.query_params.get('adventure', None)
        event_type = self.request.query_params.get('event_type', None)

        if player_id and not player_id.isdigit():
            raise serializers.ValidationError('Player ID must be an integer')
        if adventure_id and not adventure_id.isdigit():
            raise serializers.ValidationError('Adventure ID must be an integer')

        if player_id:
            queryset = queryset.filter(player_id=player_id)
        if adventure_id:
            queryset = queryset.filter(adventure_id=adventure_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        location_id = request.query_params.get('location_id')

        if location_id:
            events = GameEvent.objects.filter(location_id=location_id).order_by('-timestamp')
        else:
            events = GameEvent.objects.none()

        serializer = GameEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_choice(self, request, pk=None):
        """
        Dodatkowa akcja do dodawania wyborów do zdarzenia.
        Tworzy nowy endpoint: /api/events/{id}/add_choice/
        
        Przykład użycia:
        POST /api/events/1/add_choice/
        {
            "text": "Wybierz tę opcję",
            "next_location": 2,
            "consequences": {"health": -10}
        }
        """
        event = self.get_object()
        serializer = self.get_serializer(event)
        choice_data = request.data
        serializer.add_choice(choice_data)
        return Response(serializer.data)