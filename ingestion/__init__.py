"""
Script principal d'ingestion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.db import test_connection
from ingestion.create_schema import create_schema
from ingestion.load_data import load_all_data


def main():
    """Orchestration complète de l'ingestion"""
    print()
    print("🏭 INDUSTRIAL DATA PLATFORM - INGESTION")
    print()
    
    # Étape 1 : Tester la connexion
    print("1️⃣  Test de connexion PostgreSQL...")
    if not test_connection():
        print("❌ Impossible de se connecter à PostgreSQL")
        sys.exit(1)
    print()
    
    # Étape 2 : Créer le schéma
    print("2️⃣  Création du schéma...")
    if not create_schema():
        print("❌ Erreur lors de la création du schéma")
        sys.exit(1)
    print()
    
    # Étape 3 : Charger les données
    print("3️⃣  Chargement des données...")
    load_all_data()
    print()
    
    print("=" * 60)
    print("✅ Ingestion terminée!")
    print("=" * 60)


if __name__ == "__main__":
    main()
