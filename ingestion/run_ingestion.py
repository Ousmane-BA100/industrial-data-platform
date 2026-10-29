#!/usr/bin/env python
"""
Script d'ingestion simple - Alternative à Airflow
Exécute le pipeline complet:
1. Générer les données
2. Créer le schéma
3. Charger les données

Utilisation:
    python ingestion/run_ingestion.py
"""

import sys
from pathlib import Path

# Ajouter les répertoires au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts" / "generate_data"))
sys.path.insert(0, str(project_root / "ingestion"))

def main():
    print("\n" + "="*70)
    print("🏭 INDUSTRIAL DATA PLATFORM - Data Pipeline")
    print("="*70 + "\n")
    
    try:
        # PHASE 1: Générer les données
        print("📊 PHASE 1: Génération des données")
        print("-"*70)
        
        from generate_all import main as generate_data_main
        generate_data_main()
        
        # PHASE 2: Créer le schéma
        print("\n📊 PHASE 2: Création du schéma PostgreSQL")
        print("-"*70)
        
        from create_schema import create_tables
        create_tables()
        
        # PHASE 3: Charger les données
        print("\n📊 PHASE 3: Chargement des données")
        print("-"*70)
        
        from load_data import load_all_data
        load_all_data()
        
        # PHASE 4: Valider
        print("\n📊 PHASE 4: Validation des données")
        print("-"*70)
        
        from db import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        with engine.connect() as conn:
            suppliers = conn.execute(text("SELECT COUNT(*) FROM suppliers")).scalar()
            materials = conn.execute(text("SELECT COUNT(*) FROM materials")).scalar()
            products = conn.execute(text("SELECT COUNT(*) FROM products")).scalar()
            bom = conn.execute(text("SELECT COUNT(*) FROM bom")).scalar()
            production = conn.execute(text("SELECT COUNT(*) FROM production_events")).scalar()
            quality = conn.execute(text("SELECT COUNT(*) FROM quality_inspections")).scalar()
            
            print(f"\n✅ Données chargées avec succès:")
            print(f"   • Suppliers: {suppliers}")
            print(f"   • Materials: {materials}")
            print(f"   • Products: {products}")
            print(f"   • BOM: {bom}")
            print(f"   • Production: {production}")
            print(f"   • Quality: {quality}")
            print(f"\n📊 TOTAL: {suppliers + materials + products + bom + production + quality} lignes\n")
        
        print("="*70)
        print("✨ Pipeline complété avec succès!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
