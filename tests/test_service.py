from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from models import ProductCreate, ProductUpdate
from service import ProductNotFoundError, ProductService


def make(name="Mouse", price=9.9, quantity=3):
    return ProductCreate(name=name, price=price, quantity=quantity)


def test_create_returns_product_with_id():
    product = ProductService().create(make())
    assert product.id == 1
    assert (product.name, product.price, product.quantity) == ("Mouse", 9.9, 3)


def test_create_assigns_distinct_ids():
    service = ProductService()
    assert service.create(make()).id != service.create(make("Tastiera")).id


def test_list_empty_catalog():
    assert ProductService().list() == []


def test_list_contains_created_products():
    service = ProductService()
    first = service.create(make())
    second = service.create(make("Tastiera"))
    assert service.list() == [first, second]


def test_list_returns_copy_of_catalog():
    service = ProductService()
    service.create(make())
    service.list().clear()
    assert len(service.list()) == 1


def test_list_products_are_immutable():
    service = ProductService()
    service.create(make())
    with pytest.raises(ValidationError):
        service.list()[0].quantity = 99


def test_create_instances_are_isolated():
    first, second = ProductService(), ProductService()
    first.create(make())
    assert second.list() == []


def test_update_changes_only_sent_fields():
    service = ProductService()
    created = service.create(make())
    updated = service.update(created.id, ProductUpdate(quantity=10))
    assert updated.quantity == 10
    assert (updated.id, updated.name, updated.price) == (
        created.id,
        created.name,
        created.price,
    )
    assert service.list() == [updated]


def test_update_empty_changes_returns_existing_product():
    service = ProductService()
    created = service.create(make())
    assert service.update(created.id, ProductUpdate()) == created


def test_update_missing_product_raises_and_creates_nothing():
    service = ProductService()
    with pytest.raises(ProductNotFoundError):
        service.update(42, ProductUpdate(quantity=1))
    assert service.list() == []


def test_concurrent_creates_assign_distinct_ids():
    service = ProductService()
    with ThreadPoolExecutor(max_workers=16) as pool:
        created = list(pool.map(lambda _: service.create(make()), range(200)))
    ids = [product.id for product in created]
    assert len(set(ids)) == 200
    assert len(service.list()) == 200
