import pytest
from users.models import CustomUser

pytestmark = pytest.mark.django_db


def test_register_success(api_client):
    url = '/api/auth/register/'
    data = {
        "email": "register@example.com",
        "username": "register_user",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "Test",
        "last_name": "Reg"
    }
    response = api_client.post(url, data)

    assert response.status_code == 201
    assert CustomUser.objects.filter(email=data['email']).exists()
    user = CustomUser.objects.get(email=data['email'])
    assert user.profile.first_name == "Test"


def test_register_duplicate_email(api_client, user):
    url = '/api/auth/register/'
    data = {
        "email": user.email,
        "username": "new_user",
        "password": "password123",
        "password_confirm": "password123",
        "first_name": "Test",
        "last_name": "Reg"
    }
    response = api_client.post(url, data)

    assert response.status_code == 400
    assert 'email' in response.data


def test_login_success(api_client, user):
    url = '/api/auth/login/'
    data = {"email": user.email, "password": "strongpass123"}
    response = api_client.post(url, data)

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_login_fail(api_client, user):
    url = '/api/auth/login/'
    data = {"email": user.email, "password": "wrongpassword"}
    response = api_client.post(url, data)

    assert response.status_code == 400


def test_get_user_me(authenticated_client, user):
    url = '/api/auth/user/'
    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert response.data['email'] == user.email
    assert 'profile' in response.data


def test_patch_user_me_profile(authenticated_client, user):
    url = '/api/auth/user/'
    data = {
        "profile": {
            "first_name": "Updated Name",
            "contact_details": "My Telegram"
        }
    }
    response = authenticated_client.patch(url, data, format='json')

    assert response.status_code == 200
    assert response.data['profile']['first_name'] == "Updated Name"

    user.profile.refresh_from_db()
    assert user.profile.first_name == "Updated Name"
