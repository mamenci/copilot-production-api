from threading import Lock

from models import Product, ProductCreate, ProductUpdate


class ProductNotFoundError(Exception):
    def __init__(self, product_id: int) -> None:
        super().__init__(f"Product {product_id} not found")
        self.product_id = product_id


class ProductService:
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._next_id = 1
        self._lock = Lock()

    def create(self, data: ProductCreate) -> Product:
        with self._lock:
            product = Product(id=self._next_id, **data.model_dump())
            self._products[product.id] = product
            self._next_id += 1
            return product

    def list(self) -> list[Product]:
        with self._lock:
            return list(self._products.values())

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        with self._lock:
            current = self._products.get(product_id)
            if current is None:
                raise ProductNotFoundError(product_id)
            changes = data.model_dump(exclude_unset=True)
            updated = Product(**{**current.model_dump(), **changes})
            self._products[product_id] = updated
            return updated
