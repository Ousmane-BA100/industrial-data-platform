"""API FastAPI exposee sur les marts dbt de la plateforme industrielle."""
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="Industrial Data Platform API",
    description="API REST pour la plateforme data engineering industrielle",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database_url = os.getenv("DATABASE_URL")
if database_url:
    engine = create_engine(database_url, pool_pre_ping=True)
else:
    engine = create_engine(
        URL.create(
            "postgresql+psycopg2",
            username=os.getenv("DB_USER", os.getenv("POSTGRES_USER")),
            password=os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD")),
            host=os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost")),
            port=int(os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))),
            database=os.getenv("DB_NAME", os.getenv("POSTGRES_DB")),
        ),
        pool_pre_ping=True,
    )


def read_many(statement, parameters=None):
    """Execute une requete de lecture et renvoie des dictionnaires JSON."""
    try:
        with engine.connect() as connection:
            return [dict(row) for row in connection.execute(text(statement), parameters or {}).mappings()]
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Database unavailable") from error


def read_one(statement, parameters=None):
    rows = read_many(statement, parameters)
    if not rows:
        raise HTTPException(status_code=404, detail="Resource not found")
    return rows[0]


@app.get("/")
async def root():
    """Point d'entree de l'API."""
    return {
        "message": "Industrial Data Platform API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Verifie la disponibilite de PostgreSQL."""
    read_one("select 'healthy' as status")
    return {"status": "healthy"}


@app.get("/products")
async def list_products(
    family: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Liste les produits exposes par le mart produits."""
    return read_many(
        """
        select product_id, name, family, description, unit_price, weight_kg, active
        from public_marts.dim_products
        where (:family is null or family = :family)
        order by product_id
        limit :limit offset :offset
        """,
        {"family": family, "limit": limit, "offset": offset},
    )


@app.get("/products/costs")
async def product_costs():
    """Expose les couts de BOM et prix pour les graphiques produits."""
    return read_many(
        """
        select p.product_id, p.name, p.family, p.unit_price,
               b.nb_components, b.total_components_qty, b.total_bom_cost,
               p.unit_price - b.total_bom_cost as estimated_margin
        from public_marts.dim_products p
        left join public_marts.fact_product_bom_cost b using (product_id)
        order by p.family, p.product_id
        """
    )


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """Recupere les details et le cout theorique de BOM d'un produit."""
    return read_one(
        """
        select p.*, b.nb_components, b.total_components_qty, b.total_bom_cost
        from public_marts.dim_products p
        left join public_marts.fact_product_bom_cost b using (product_id)
        where p.product_id = :product_id
        """,
        {"product_id": product_id},
    )


@app.get("/products/{product_id}/components")
async def get_product_components(product_id: str):
    """Liste les composants et couts du mart de nomenclature produit."""
    product = read_one(
        "select product_id from public_marts.dim_products where product_id = :product_id",
        {"product_id": product_id},
    )
    return {
        "product_id": product["product_id"],
        "components": read_many(
            """
            select component_id, component_description, component_category, quantity,
                   unit, component_unit_price, component_total_cost
            from public_marts.dim_product_components
            where product_id = :product_id
            order by component_category, component_id
            """,
            {"product_id": product_id},
        ),
    }


@app.get("/inventory")
async def list_inventory(
    warehouse: str | None = None,
    only_below_reorder_level: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Liste le stock exploitable, hors anomalies negatives intentionnelles."""
    return read_many(
        """
        select * from public_marts.fact_inventory_status
        where (:warehouse is null or warehouse = :warehouse)
          and (:only_below_reorder_level = false or is_below_reorder_level)
        order by material_id, warehouse
        limit :limit offset :offset
        """,
        {
            "warehouse": warehouse,
            "only_below_reorder_level": only_below_reorder_level,
            "limit": limit,
            "offset": offset,
        },
    )


@app.get("/inventory/replenishment")
async def inventory_replenishment():
    """Expose les materiaux dont le stock doit etre reapprovisionne."""
    return read_many(
        """
        select * from public_marts.kpi_inventory_replenishment
        where needs_replenishment
        order by total_available_quantity, material_id
        """
    )


@app.get("/inventory/{material_id}")
async def get_inventory(material_id: str):
    """Agrege le stock exploitable par materiau."""
    return read_one(
        """
        select material_id, material_description, material_category,
               sum(quantity_available) as total_available_quantity,
               sum(reorder_level) as total_reorder_level,
               bool_or(is_below_reorder_level) as has_reorder_alert
        from public_marts.fact_inventory_status
        where material_id = :material_id
        group by material_id, material_description, material_category
        """,
        {"material_id": material_id},
    )


@app.get("/suppliers")
async def list_suppliers(
    active_only: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Liste les fournisseurs du mart fournisseurs."""
    return read_many(
        """
        select * from public_marts.dim_suppliers
        where (:active_only = false or active)
        order by supplier_id
        limit :limit offset :offset
        """,
        {"active_only": active_only, "limit": limit, "offset": offset},
    )


@app.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: str):
    """Recupere un fournisseur et ses materiaux actifs."""
    supplier = read_one(
        "select * from public_marts.dim_suppliers where supplier_id = :supplier_id",
        {"supplier_id": supplier_id},
    )
    supplier["materials"] = read_many(
        """
        select material_id, description, category, unit, unit_price, lead_time_days, active
        from public_marts.dim_materials
        where supplier_id = :supplier_id
        order by material_id
        """,
        {"supplier_id": supplier_id},
    )
    return supplier


@app.get("/quality/conformity")
async def quality_conformity():
    """Expose le taux de conformite par produit et machine."""
    return read_many(
        "select * from public_marts.kpi_quality_by_product_machine order by conformity_rate_pct nulls last"
    )


@app.get("/quality/top-defects")
async def top_defects():
    """Expose les defauts les plus frequents."""
    return read_many("select * from public_marts.kpi_top_defects")


@app.get("/dashboard/overview")
async def dashboard_overview():
    """Expose les compteurs principaux pour les applications de visualisation."""
    return read_one(
        """
        select
            (select count(*) from public_marts.dim_products where active) as active_products,
            (select coalesce(sum(quantity_produced), 0) from public_marts.fact_production) as quantity_produced,
            (select count(*) from public_marts.kpi_inventory_replenishment where needs_replenishment) as materials_to_replenish,
            (
                select coalesce(
                    round(100.0 * count(*) filter (where quality_status = 'PASSED') / nullif(count(*), 0), 2),
                    0
                )
                from public_marts.fact_quality
            ) as conformity_rate_pct
        """
    )




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
