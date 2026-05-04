import pytest
from world.models import Adventure, Location, Choice
from users.models import CustomUser

# _ to konwencja, oznaczająca zmienne, których nie zamierzamy używać. W user, adventure, _, _ = 
#create_test_data() pomijamy location i choice, bo nie są nam potrzebne w tym teście. 

def create_test_data():
    
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    location = Location.objects.create(adventure=adventure, title='Test Location', description='Test Description')
    choice = Choice.objects.create(location=location, title='Test Choice', description='Test Description')
    return user, adventure, location, choice

@pytest.mark.django_db
def test_create_adventure():
    user, adventure, _, _ = create_test_data()
    assert adventure.title == 'Test Adventure'
    assert adventure.description == 'Test Description'
    assert adventure.creator.username == 'testuser'

@pytest.mark.django_db
def test_create_location():
    _, adventure, location, _ = create_test_data()
    assert location.adventure.title == 'Test Adventure'
    assert location.title == 'Test Location'
    assert location.description == 'Test Description'

@pytest.mark.django_db
def test_create_choice():
    _, _, location, choice = create_test_data()
    assert choice.location.adventure.title == 'Test Adventure'
    assert choice.location.title == 'Test Location'
    assert choice.title == 'Test Choice'
    assert choice.description == 'Test Description'

@pytest.mark.django_db
def test_location_choices():
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    adventure = Adventure.objects.create(title='Test Adventure', description='Test Description', creator=user)
    location = Location.objects.create(adventure=adventure, title='Test Location', description='Test Description')
    choice1 = Choice.objects.create(location=location, title='Test Choice 1', description='Test Description')
    choice2 = Choice.objects.create(location=location, title='Test Choice 2', description='Test Description')
    
    assert location.choices.count() == 2
    assert location.choices.first().title == 'Test Choice 1'
    assert location.choices.last().title == 'Test Choice 2'