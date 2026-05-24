from __future__ import annotations

from .models import Product


CATALOG: tuple[Product, ...] = (
    Product(
        sku="OFF-A4-80",
        name="Everyday Office A4 80gsm",
        use_case="office",
        sustainability="standard",
        unit_price=4.20,
        minimum_order_units=100,
        margin=0.28,
    ),
    Product(
        sku="OFF-REC-75",
        name="Recycled Office A4 75gsm",
        use_case="office",
        sustainability="recycled",
        unit_price=4.85,
        minimum_order_units=100,
        margin=0.31,
    ),
    Product(
        sku="PRT-SILK-150",
        name="Silk Coated Printing Paper 150gsm",
        use_case="printing",
        sustainability="certified",
        unit_price=8.90,
        minimum_order_units=80,
        margin=0.34,
    ),
    Product(
        sku="PKG-KRAFT-120",
        name="Kraft Packaging Paper 120gsm",
        use_case="packaging",
        sustainability="recycled",
        unit_price=6.75,
        minimum_order_units=120,
        margin=0.30,
    ),
    Product(
        sku="EDU-COPY-70",
        name="School Copy Paper 70gsm",
        use_case="education",
        sustainability="standard",
        unit_price=3.95,
        minimum_order_units=150,
        margin=0.24,
    ),
    Product(
        sku="RTL-BAG-100",
        name="Retail Bag Paper 100gsm",
        use_case="retail",
        sustainability="certified",
        unit_price=7.10,
        minimum_order_units=100,
        margin=0.32,
    ),
)
