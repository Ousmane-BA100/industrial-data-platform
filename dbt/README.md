# 🔄 dbt - Transformations

## 3 couches (simples, pas de logique complexe pour l'instant)

```
models/
├── staging/        # 1:1 avec les tables RAW (renommage/nettoyage minimal)
│   ├── stg_suppliers.sql
│   ├── stg_materials.sql
│   ├── stg_products.sql
│   ├── stg_bom.sql
│   ├── stg_inventory.sql
│   ├── stg_orders.sql
│   ├── stg_production_events.sql
│   └── stg_quality_inspections.sql
│
├── intermediate/   # Jointures simples
│   ├── int_product_components.sql   (BOM + products + materials)
│   └── int_production_quality.sql   (production + quality)
│
├── marts/          # Tables finales exploitables
    ├── dim_products.sql
    ├── dim_materials.sql
    ├── dim_suppliers.sql
    ├── fact_production.sql
    ├── fact_quality.sql
    └── fact_product_bom_cost.sql

└── docs/            # Page d'accueil, blocs Markdown et expositions aval
    ├── overview.md
    ├── documentation_blocks.md
    └── exposures.yml
```

Le logo de la page d'accueil est dans `assets/` et est copie dans les artefacts dbt grace a `asset-paths` dans `dbt_project.yml`.

## Lancer via Docker

```bash
docker-compose up -d dbt

# Vérifier la connexion
docker-compose exec dbt dbt debug

# Exécuter les modèles
docker-compose exec dbt dbt run

# Lancer les tests (not_null, unique, relationships)
docker-compose exec dbt dbt test

# Generer le catalogue avec descriptions et lineage
docker-compose exec dbt dbt docs generate

# Le site dbt docs est servi localement sur http://localhost:8081
```

## Lancer sans Docker (depuis la machine hôte)

```bash
cd dbt
pip install dbt-postgres
export DBT_POSTGRES_HOST=localhost   # PowerShell: $env:DBT_POSTGRES_HOST="localhost"
dbt debug
dbt run
dbt test
```

Pré-requis: les données doivent déjà être chargées dans PostgreSQL (`python ingestion/run_ingestion.py` ou le DAG Airflow).
