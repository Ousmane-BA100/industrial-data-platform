"""
Chargement des données CSV dans PostgreSQL RAW
"""
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.db import get_engine

# Chemins des fichiers CSV
DATA_DIR = Path(__file__).parent.parent / "data"

CSV_FILES = {
    "suppliers": DATA_DIR / "sap" / "suppliers.csv",
    "materials": DATA_DIR / "sap" / "materials.csv",
    "inventory": DATA_DIR / "sap" / "inventory.csv",
    "orders": DATA_DIR / "sap" / "orders.csv",
    "products": DATA_DIR / "plm" / "products.csv",
    "bom": DATA_DIR / "plm" / "bom.csv",
    "production_events": DATA_DIR / "production" / "production_events.csv",
    "quality_inspections": DATA_DIR / "quality" / "quality_inspections.csv",
}


def load_csv_to_postgres(table_name, csv_path):
    """Charge un fichier CSV dans une table PostgreSQL"""
    engine = get_engine()
    
    if not engine:
        return False
    
    if not csv_path.exists():
        print(f"⚠️  Fichier non trouvé: {csv_path}")
        return False
    
    try:
        # Lire le CSV
        df = pd.read_csv(csv_path)
        
        # Insérer dans le schéma existant sans supprimer ses contraintes
        df.to_sql(table_name, engine, if_exists="append", index=False)
        
        print(f"✓ {len(df)} lignes chargées dans {table_name}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement {table_name}: {e}")
        return False


def load_all_data():
    """Charge tous les fichiers CSV"""
    print("=" * 60)
    print("🔄 CHARGEMENT DES DONNÉES CSV → PostgreSQL")
    print("=" * 60)
    print()
    
    success_count = 0

    engine = get_engine()
    if not engine:
        raise RuntimeError("Impossible de charger les données: connexion DB indisponible")

    with engine.begin() as connection:
        connection.execute(text(
            "TRUNCATE TABLE quality_inspections, production_events, bom, "
            "orders, inventory, products, materials, suppliers CASCADE"
        ))
    
    for table_name, csv_path in CSV_FILES.items():
        if load_csv_to_postgres(table_name, csv_path):
            success_count += 1

    if success_count != len(CSV_FILES):
        raise RuntimeError(f"Chargement incomplet: {success_count}/{len(CSV_FILES)} tables chargées")
    
    print()
    print("=" * 60)
    print(f"✨ {success_count}/{len(CSV_FILES)} tables chargées")
    print("=" * 60)


if __name__ == "__main__":
    load_all_data()
