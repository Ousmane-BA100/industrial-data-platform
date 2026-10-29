"""
Industrial Data Platform - Main DAG
Orchestre le pipeline complet:
1. Générer les données (CSV)
2. Créer le schéma PostgreSQL
3. Charger les données
4. Valider les données

Exécution manuelle ou programmée.
"""

from datetime import datetime, timedelta
import os
import subprocess
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# Ajouter les répertoires au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "generate_data"))
sys.path.insert(0, str(project_root / "ingestion"))

# Importer les fonctions de génération et d'ingestion
from generate_all import main as generate_data_main
from generate_suppliers import generate_suppliers
from generate_materials import generate_materials
from generate_products import generate_products
from generate_bom import generate_bom
from generate_inventory import generate_inventory
from generate_orders import generate_orders
from generate_production import generate_production
from generate_quality import generate_quality

# Importer les fonctions d'ingestion
from create_schema import create_schema
from load_data import load_all_data

# Configuration du DAG
default_args = {
    'owner': 'industrial-platform',
    'depends_on_past': False,
    'start_date': datetime(2026, 9, 17),
    'email': [os.getenv('AIRFLOW_ADMIN_EMAIL', 'admin@example.invalid')],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'industrial_data_pipeline',
    default_args=default_args,
    description='Industrial Data Platform - Complete Data Pipeline',
    schedule_interval=None,  # Manuel trigger
    catchup=False,
    tags=['industrial', 'data-pipeline', 'production'],
)

# ============================================================================
# PHASE 1: GÉNÉRATION DES DONNÉES (CSV)
# ============================================================================

def task_generate_suppliers():
    """Générer les fournisseurs SAP"""
    print("🏭 Génération des fournisseurs...")
    generate_suppliers()
    print("✅ Fournisseurs générés")

def task_generate_materials():
    """Générer les matériaux SAP"""
    print("📦 Génération des matériaux...")
    generate_materials()
    print("✅ Matériaux générés")

def task_generate_products():
    """Générer les produits PLM"""
    print("🛠️ Génération des produits...")
    generate_products()
    print("✅ Produits générés")

def task_generate_bom():
    """Générer les BOMs"""
    print("📋 Génération des BOMs...")
    generate_bom()
    print("✅ BOMs générées")

def task_generate_inventory():
    """Générer le stock"""
    print("📊 Génération de l'inventaire...")
    generate_inventory()
    print("✅ Inventaire généré")

def task_generate_orders():
    """Générer les commandes"""
    print("📬 Génération des commandes...")
    generate_orders()
    print("✅ Commandes générées")

def task_generate_production():
    """Générer les événements de production"""
    print("🏭 Génération de la production...")
    generate_production()
    print("✅ Production générée")

def task_generate_quality():
    """Générer les inspections qualité"""
    print("✅ Génération de la qualité...")
    generate_quality()
    print("✅ Qualité générée")

# ============================================================================
# PHASE 2: CRÉATION DU SCHÉMA
# ============================================================================

def task_create_schema():
    """Créer le schéma PostgreSQL"""
    print("🗄️ Création du schéma PostgreSQL...")
    if not create_schema():
        raise RuntimeError("La création du schéma a échoué")
    print("✅ Schéma créé")

# ============================================================================
# PHASE 3: CHARGEMENT DES DONNÉES
# ============================================================================

def task_load_data():
    """Charger les données dans PostgreSQL"""
    print("📥 Chargement des données...")
    load_all_data()
    print("✅ Données chargées")

# ============================================================================
# PHASE 4: TRANSFORMATIONS DBT
# ============================================================================

def run_dbt(command):
    """Exécute dbt dans le projet monté dans le conteneur Airflow."""
    dbt_project_dir = project_root / "dbt"
    dbt_runtime_dir = Path("/opt/airflow/logs/dbt")
    dbt_runtime_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["/home/airflow/.local/bin/dbt", command],
        cwd=dbt_project_dir,
        env={
            **os.environ,
            "DBT_PROFILES_DIR": str(dbt_project_dir),
            "DBT_LOG_PATH": str(dbt_runtime_dir),
            "DBT_TARGET_PATH": str(dbt_runtime_dir / "target"),
        },
        check=True,
    )


def task_dbt_run():
    print("🔄 Exécution des modèles dbt...")
    run_dbt("run")
    print("✅ Modèles dbt créés")


def task_dbt_test():
    print("🧪 Exécution des tests dbt...")
    run_dbt("test")
    print("✅ Tests dbt réussis")


# ============================================================================
# PHASE 5: VALIDATION FINALE
# ============================================================================

def task_validate_data():
    """Valider les données chargées"""
    print("🔍 Validation des données...")
    
    from db import get_engine
    from sqlalchemy import text
    
    engine = get_engine()
    with engine.connect() as conn:
        # Vérifier les tables
        suppliers_count = conn.execute(text("SELECT COUNT(*) FROM suppliers")).scalar()
        materials_count = conn.execute(text("SELECT COUNT(*) FROM materials")).scalar()
        products_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
        bom_count = conn.execute(text("SELECT COUNT(*) FROM bom")).scalar()
        production_count = conn.execute(text("SELECT COUNT(*) FROM production_events")).scalar()
        quality_count = conn.execute(text("SELECT COUNT(*) FROM quality_inspections")).scalar()
        mart_products_count = conn.execute(text("SELECT COUNT(*) FROM public_marts.dim_products")).scalar()
        quality_kpis_count = conn.execute(text("SELECT COUNT(*) FROM public_marts.kpi_quality_by_product_machine")).scalar()
        
        print(f"✅ Suppliers: {suppliers_count}")
        print(f"✅ Materials: {materials_count}")
        print(f"✅ Products: {products_count}")
        print(f"✅ BOM: {bom_count}")
        print(f"✅ Production: {production_count}")
        print(f"✅ Quality: {quality_count}")
        print(f"✅ Mart products: {mart_products_count}")
        print(f"✅ Quality KPIs: {quality_kpis_count}")
        
        total = suppliers_count + materials_count + products_count + bom_count + production_count + quality_count
        print(f"\n📊 TOTAL: {total} lignes")

# ============================================================================
# DÉFINITION DES TÂCHES
# ============================================================================

# Phase 1: Génération
task_1_suppliers = PythonOperator(
    task_id='generate_suppliers',
    python_callable=task_generate_suppliers,
    dag=dag,
)

task_2_materials = PythonOperator(
    task_id='generate_materials',
    python_callable=task_generate_materials,
    depends_on_past=False,
    dag=dag,
)

task_3_products = PythonOperator(
    task_id='generate_products',
    python_callable=task_generate_products,
    dag=dag,
)

task_4_bom = PythonOperator(
    task_id='generate_bom',
    python_callable=task_generate_bom,
    depends_on_past=False,
    dag=dag,
)

task_5_inventory = PythonOperator(
    task_id='generate_inventory',
    python_callable=task_generate_inventory,
    dag=dag,
)

task_6_orders = PythonOperator(
    task_id='generate_orders',
    python_callable=task_generate_orders,
    depends_on_past=False,
    dag=dag,
)

task_7_production = PythonOperator(
    task_id='generate_production',
    python_callable=task_generate_production,
    dag=dag,
)

task_8_quality = PythonOperator(
    task_id='generate_quality',
    python_callable=task_generate_quality,
    depends_on_past=False,
    dag=dag,
)

# Phase 2: Schéma
task_9_schema = PythonOperator(
    task_id='create_schema',
    python_callable=task_create_schema,
    dag=dag,
)

# Phase 3: Chargement
task_10_load = PythonOperator(
    task_id='load_data',
    python_callable=task_load_data,
    dag=dag,
)

# Phase 4: dbt run
task_11_dbt_run = PythonOperator(
    task_id='dbt_run',
    python_callable=task_dbt_run,
    dag=dag,
)

# Phase 4: dbt test
task_12_dbt_test = PythonOperator(
    task_id='dbt_test',
    python_callable=task_dbt_test,
    dag=dag,
)

# Phase 5: Validation
task_13_validate = PythonOperator(
    task_id='validate_data',
    python_callable=task_validate_data,
    dag=dag,
)

# ============================================================================
# DÉPENDANCES
# ============================================================================

# Phase 1: Générations parallèles avec dépendances métier
task_1_suppliers >> task_2_materials
task_2_materials >> task_5_inventory
task_2_materials >> task_4_bom
task_3_products >> task_4_bom
[task_1_suppliers, task_2_materials] >> task_6_orders
task_3_products >> task_7_production
task_7_production >> task_8_quality

# Phase 2: Attendre la génération avant le schéma
[task_4_bom, task_6_orders, task_8_quality] >> task_9_schema

# Phase 3: Créer le schéma avant le chargement
task_9_schema >> task_10_load

# Phases 4-5: Transformer, tester et valider après le chargement
task_10_load >> task_11_dbt_run >> task_12_dbt_test >> task_13_validate

if __name__ == "__main__":
    dag.cli()
