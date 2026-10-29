# API FastAPI

L'API expose les marts dbt de `public_marts`. Elle ne lit ni les tables RAW ni les vues de staging, afin de fournir des donnees preparees et controlees.

## Demarrage

```bash
docker-compose up -d api
```

- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`
- Health check : `http://localhost:8000/health`

L'API est en lecture seule. Les modifications de donnees passent par les sources CSV,
le pipeline Airflow et dbt ; les applications clientes, dont Streamlit, utilisent les `GET` JSON.

Executer le DAG Airflow complet ou `dbt run` avant de consulter les endpoints, car les marts doivent etre materialises.

## Produits

| Route | Description |
| --- | --- |
| `GET /products` | Liste paginee. Filtres : `family`, `limit`, `offset`. |
| `GET /products/{product_id}` | Produit et cout theorique de BOM. |
| `GET /products/{product_id}/components` | Composants, quantites et couts du produit. |

```text
GET /products?family=HPC-CLUSTER&limit=20
GET /products/HPC-CLUSTER-001/components
```

## Stock

| Route | Description |
| --- | --- |
| `GET /inventory` | Stock exploitable par entrepot. Filtres : `warehouse`, `only_below_reorder_level`, `limit`, `offset`. |
| `GET /inventory/replenishment` | Materiaux sous le seuil de reapprovisionnement. |
| `GET /inventory/{material_id}` | Stock agrege et statut d'alerte d'un materiau. |

Les stocks negatifs intentionnels restent dans le staging pour les tests Data Quality, mais ne sont pas exposes par l'API.

## Fournisseurs

| Route | Description |
| --- | --- |
| `GET /suppliers` | Liste paginee. Filtre : `active_only`. |
| `GET /suppliers/{supplier_id}` | Fournisseur et liste de ses materiaux. |

## Qualite

| Route | Description |
| --- | --- |
| `GET /quality/conformity` | Taux de conformite par produit et machine. |
| `GET /quality/top-defects` | Defauts les plus frequents. |

## Dashboard

| Route | Description |
| --- | --- |
| `GET /dashboard/overview` | Compteurs consolides pour les cartes du dashboard Streamlit. |

## Codes de reponse

- `200` : requete reussie.
- `404` : identifiant inexistant.
- `422` : parametre de pagination ou filtre invalide.
- `503` : PostgreSQL ou les marts ne sont pas disponibles.

## Couches exposees

```text
public (RAW) -> public_staging -> public_intermediate -> public_marts -> FastAPI
```

Marts consommes par l'API :

- `dim_products`, `dim_product_components`, `fact_product_bom_cost`
- `dim_suppliers`, `dim_materials`
- `fact_inventory_status`, `kpi_inventory_replenishment`
- `kpi_quality_by_product_machine`, `kpi_top_defects`
