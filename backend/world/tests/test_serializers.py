import pytest
from rest_framework import serializers
from django.contrib.auth import get_user_model
from world.serializers import AdventureSerializer, LocationSerializer, ChoiceSerializer
from world.models import Adventure, Location, Choice
from users.models import CustomUser

def create_user():
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.mark.django_db
def test_adventure_serializer():
    """ Test the serialization of an Adventure instance. """

    user = create_user()

    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    serializer = AdventureSerializer(adventure)

    assert serializer.data['title'] == 'Test Adventure'
    assert serializer.data['description'] == 'Test Description'
    assert serializer.data['creator'] == user.id

@pytest.mark.django_db
def test_location_serializer():
    """ Test the serialization of a Location instance. """

    user = create_user()

    adventure = Adventure.objects.create(title='Test Title', description='Test Description', creator=user)
    location = Location.objects.create(adventure=adventure, title='Test Title', description='Test Description')
    serialized_location = LocationSerializer(location)

    assert serialized_location.data['title'] == location.title
    assert serialized_location.data['description'] == location.description
    assert serialized_location.data['adventure'] == location.adventure.id


@pytest.mark.django_db
def test_choice_serializer():
    """ Test the serialization of a Choice instance. """
    user = create_user()

    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    location = Location.objects.create(adventure=adventure, title='Test Location', description='Test Description')
    choice = Choice.objects.create(location=location, title='Test Choice', description='Test Description')
    serializer = ChoiceSerializer(choice)

    assert serializer.data['title'] == choice.title
    assert serializer.data['description'] == choice.description
    assert serializer.data['location'] == location.id


@pytest.mark.django_db
def test_adventure_serializer_create():
    """ Test the creation of an Adventure instance through AdventureSerializer. """
    user = create_user()

    data = {'title': 'Test Adventure', 'description': 'Test Description'}
    
    serializer = AdventureSerializer(data=data)
    
    assert serializer.is_valid()
    
    adventure = serializer.save(creator=user)
    
    assert adventure.title == 'Test Adventure'
    assert adventure.description == 'Test Description'


@pytest.mark.django_db
def test_location_serializer_create():
    """ Test the creation of a Location instance through LocationSerializer. """
    user = create_user()

    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    
    data = {'title': 'Test Location', 'description': 'Test Description', 'adventure': adventure.id}
    
    serializer = LocationSerializer(data=data)
    
    assert serializer.is_valid()
    
    location = serializer.save()
    
    assert location.title == 'Test Location'
    assert location.description == 'Test Description'
    assert location.adventure == adventure


@pytest.mark.django_db
def test_choice_serializer_create():
    """ Test the creation of a Choice instance through ChoiceSerializer. """

    user = create_user()
    
    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    
    location = Location.objects.create(adventure=adventure, title='Test Location', description='Test Description')
    
    data = {'title': 'Test Choice', 'description': 'Test Description', 'location': location.id}
    
    serializer = ChoiceSerializer(data=data)
    
    assert serializer.is_valid()
    
    choice = serializer.save()
   
    assert choice.title == 'Test Choice'
    assert choice.description == 'Test Description'
    assert choice.location == location
