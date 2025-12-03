import pytest
import factory
from rest_framework.test import APIClient
from users.models import CustomUser
from transactions.models import Category


@pytest.fixture
def user_factory(db):
    class UserFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = CustomUser

        email = factory.Sequence(lambda n: f'user{n}@example.com')
        username = factory.Sequence(lambda n: f'user{n}')
        password = factory.PostGenerationMethodCall('set_password', 'strongpass123')

    return UserFactory


@pytest.fixture
def category_factory(db):
    class CategoryFactory(factory.django.DjangoModelFactory):
        class Meta:
            model = Category

        name = factory.Sequence(lambda n: f'Category {n}')
        type = Category.CategoryType.EXPENSE

    return CategoryFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def user2(user_factory):
    return user_factory()


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def standard_category(category_factory):
    return category_factory(owner=None, name="Products")
