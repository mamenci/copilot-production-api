import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def payload(**overrides):
    return {"name": "Mouse", "price": 9.9, "quantity": 3, **overrides}


def test_create_returns_201_with_product(client):
    response = client.post("/products", json=payload())
    assert response.status_code == 201
    assert response.json() == {"id": 1, **payload()}


def test_create_assigns_distinct_ids(client):
    first = client.post("/products", json=payload()).json()
    second = client.post("/products", json=payload(name="Tastiera")).json()
    assert first["id"] != second["id"]


def test_list_empty_catalog_returns_empty_array(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == []


def test_list_contains_created_products(client):
    first = client.post("/products", json=payload()).json()
    second = client.post("/products", json=payload(name="Tastiera")).json()
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json() == [first, second]


def test_update_returns_200_and_is_visible_in_list(client):
    created = client.post("/products", json=payload()).json()
    response = client.patch(f"/products/{created['id']}", json={"quantity": 10})
    assert response.status_code == 200
    assert response.json() == {**created, "quantity": 10}
    assert client.get("/products").json() == [response.json()]


def test_update_missing_product_returns_404_without_creating(client):
    response = client.patch("/products/42", json={"quantity": 1})
    assert response.status_code == 404
    assert client.get("/products").json() == []


@pytest.mark.parametrize("missing", ["name", "price", "quantity"])
def test_create_invalid_missing_field_returns_422(client, missing):
    body = payload()
    del body[missing]
    assert client.post("/products", json=body).status_code == 422


INVALID_FIELDS = [
    {"name": ""},
    {"name": "   "},
    {"price": -0.01},
    {"price": "NaN"},
    {"price": "Infinity"},
    {"quantity": -1},
    {"quantity": 1.5},
    {"quantity": True},
    {"price": True},
    {"name": "a" * 201},
    {"price": 9000000.01},
    {"quantity": 1000001},
]


@pytest.mark.parametrize("override", INVALID_FIELDS)
def test_create_invalid_value_returns_422_catalog_unchanged(client, override):
    existing = client.post("/products", json=payload()).json()
    response = client.post("/products", json=payload(**override))
    assert response.status_code == 422
    assert client.get("/products").json() == [existing]


@pytest.mark.parametrize("override", INVALID_FIELDS + [{"name": None}, {"extra": 1}])
def test_update_invalid_value_returns_422_catalog_unchanged(client, override):
    existing = client.post("/products", json=payload()).json()
    response = client.patch(f"/products/{existing['id']}", json=override)
    assert response.status_code == 422
    assert client.get("/products").json() == [existing]


def test_valid_boundary_values_are_accepted(client):
    response = client.post("/products", json=payload(price=0, quantity=0))
    assert response.status_code == 201


def test_valid_upper_limits_are_accepted_on_create_and_update(client):
    limits = {"name": "a" * 200, "price": 9000000, "quantity": 1000000}
    created = client.post("/products", json=limits)
    assert created.status_code == 201
    other = client.post("/products", json=payload()).json()
    assert client.patch(f"/products/{other['id']}", json=limits).status_code == 200
