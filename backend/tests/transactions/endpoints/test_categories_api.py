import pytest
from transactions.models import Category

pytestmark = pytest.mark.django_db
URL = '/api/categories/'


def test_list_categories_sees_own_and_standard(
        authenticated_client, category_factory, user, standard_category
):
    category_factory(owner=user, name="Salary")

    response = authenticated_client.get(URL)

    assert response.status_code == 200
    assert len(response.data) == 2

    names = {item['name'] for item in response.data}
    assert "Products" in names
    assert "Salary" in names


def test_create_category_is_personal(authenticated_client, user):
    data = {"name": "Gifts", "type": Category.CategoryType.EXPENSE}
    response = authenticated_client.post(URL, data)

    assert response.status_code == 201

    new_category = Category.objects.get(id=response.data['id'])
    assert new_category.owner == user


def test_delete_standard_category_fails(authenticated_client, standard_category):
    response = authenticated_client.delete(f"{URL}{standard_category.id}/")

    assert response.status_code == 403
    assert Category.objects.filter(id=standard_category.id).exists()


def test_delete_personal_category_success(authenticated_client, category_factory, user):
    personal_category = category_factory(owner=user)

    response = authenticated_client.delete(f"{URL}{personal_category.id}/")

    assert response.status_code == 204
    assert not Category.objects.filter(id=personal_category.id).exists()
