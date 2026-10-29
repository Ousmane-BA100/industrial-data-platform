#!/usr/bin/env python
"""
Script maître pour générer toutes les données synthétiques
Exécute tous les générateurs dans le bon ordre en respectant les dépendances
Démontre les relations métier cohérentes entre SAP → PLM → Production → Quality
"""
import sys
import time
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from generate_suppliers import generate_suppliers
from generate_materials import generate_materials
from generate_products import generate_products
from generate_bom import generate_bom
from generate_inventory import generate_inventory
from generate_orders import generate_orders
from generate_production import generate_production
from generate_quality import generate_quality


def print_banner(title):
    """Affiche un bannière"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def print_phase(phase_num, phase_name):
    """Affiche le début d'une phase"""
    print(f"\n{'─' * 70}")
    print(f"📍 PHASE {phase_num}: {phase_name}")
    print(f"{'─' * 70}\n")


def main():
    """Orchestration complète de la génération"""
    start_time = time.time()
    
    print_banner("🏭 GÉNÉRATION DES DONNÉES SYNTHÉTIQUES")
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("✨ Les données respectent les relations métier:")
    print("   SAP/ERP → PLM → Production → Quality")
    print("   avec cohérence absolue")
    print()
    
    try:
        # Phase 1 : Données SAP/ERP
        print_phase(1, "SAP / ERP - Données d'approvisionnement et matériaux")
        print("Génération des fournisseurs...")
        suppliers = generate_suppliers()
        
        print("\nGénération des matériaux RÉALISTES...")
        materials = generate_materials()
        
        print("\nGénération du stock multi-entrepôts...")
        print("(incluant quelques anomalies intentionnelles)")
        inventory = generate_inventory()
        
        print("\nGénération des commandes d'approvisionnement...")
        print("(fournisseurs et matériaux cohérents)")
        orders = generate_orders()
        
        # Phase 2 : Données PLM
        print_phase(2, "PLM - Produits et nomenclatures")
        print("Génération des produits réalistes...")
        products = generate_products()
        
        print("\nGénération des BOMs (nomenclatures)...")
        print("(référençant des matériaux réels)")
        bom_lines = generate_bom()
        
        # Phase 3 : Données Production
        print_phase(3, "PRODUCTION - Événements de fabrication")
        print("Génération des événements de production...")
        print("(référençant des produits réels)")
        production_events = generate_production()
        
        # Phase 4 : Données Quality
        print_phase(4, "QUALITY - Inspections et contrôles")
        print("Génération des inspections qualité...")
        print("(COHÉRENTES avec les productions)")
        quality_inspections = generate_quality()
        
        # Résumé final
        print_banner("✨ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
        
        print("📊 STATISTIQUES DE COHÉRENCE:\n")
        print(f"  SAP/ERP:")
        print(f"    ├─ Fournisseurs: {len(suppliers)}")
        print(f"    ├─ Matériaux: {len(materials)}")
        print(f"    ├─ Lignes d'inventaire: {len(inventory)}")
        print(f"    └─ Commandes: {len(orders)}")
        
        print(f"\n  PLM:")
        print(f"    ├─ Produits: {len(products)}")
        print(f"    └─ Lignes BOM: {len(bom_lines) if bom_lines else 0}")
        
        print(f"\n  Production:")
        print(f"    └─ Événements: {len(production_events)}")
        
        print(f"\n  Quality:")
        print(f"    └─ Inspections: {len(quality_inspections)}")
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Temps écoulé: {elapsed_time:.2f} secondes")
        
        print("\n✅ Les données synthétiques ont été générées avec:")
        print("   ✓ Relations métier cohérentes")
        print("   ✓ Matériaux réalistes (CPU, MEMORY, STORAGE, etc.)")
        print("   ✓ BOMs référençant des matériaux réels")
        print("   ✓ Productions référençant des produits réels")
        print("   ✓ Inspections qualité cohérentes avec productions")
        print("   ✓ Quelques anomalies intentionnelles (pour Data Quality)")
        print()
        print("📁 Fichiers générés dans: data/")
        print("   └─ sap/")
        print("      ├─ suppliers.csv")
        print("      ├─ materials.csv")
        print("      ├─ inventory.csv")
        print("      └─ orders.csv")
        print("   └─ plm/")
        print("      ├─ products.csv")
        print("      └─ bom.csv")
        print("   └─ production/")
        print("      └─ production_events.csv")
        print("   └─ quality/")
        print("      └─ quality_inspections.csv")
        print()
        print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERREUR lors de la génération: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
