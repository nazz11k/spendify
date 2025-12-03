import pytest
from users.models import CustomUser, Profile

pytestmark = pytest.mark.django_db


def test_create_user(user_factory):
    user = user_factory(email='test@example.com', username='testuser')
    assert user.email == 'test@example.com'
    assert user.username == 'testuser'
    assert user.check_password('strongpass123')
    assert user.is_staff is False
    assert user.is_superuser is False


def test_create_superuser():
    user = CustomUser.objects.create_superuser(
        email='super@example.com',
        username='super',
        password='superpass'
    )
    assert user.is_staff is True
    assert user.is_superuser is True


def test_create_user_signal_creates_profile(user):
    assert Profile.objects.filter(user=user).exists()
    assert user.profile is not None
    assert user.profile.first_name == 'N/A'
