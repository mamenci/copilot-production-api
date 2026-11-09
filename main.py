from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request

from models import Product, ProductCreate, ProductUpdate
from service import ProductNotFoundError, ProductService


def get_service(request: Request) -> ProductService:
    return request.app.state.service


Service = Annotated[ProductService, Depends(get_service)]


def create_app() -> FastAPI:
    app = FastAPI(title="Product API")
    app.state.service = ProductService()

    @app.post("/products", response_model=Product, status_code=201)
    def create_product(data: ProductCreate, service: Service) -> Product:
        return service.create(data)

    @app.get("/products", response_model=list[Product])
    def list_products(service: Service) -> list[Product]:
        return service.list()

    @app.patch("/products/{product_id}", response_model=Product)
    def update_product(
        product_id: int, data: ProductUpdate, service: Service
    ) -> Product:
        try:
            return service.update(product_id, data)
        except ProductNotFoundError:
            raise HTTPException(status_code=404, detail="Product not found") from None

    return app


app = create_app()
