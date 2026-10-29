"""
Génération du stock (Inventory) SAP/ERP
Réaliste: multi-entrepôts, niveaux cohérents, anomalies intentionnelles
"""
import csv
import random
from datetime import datetime, timedelta
from config import (
    INVENTORY_FILE, MATERIALS_FILE, NUM_INVENTORY_RECORDS, RANDOM_SEED,
    WAREHOUSES
)

random.seed(RANDOM_SEED)


def load_materials():
    """Charge les IDs des matériaux"""
    materials = []
    try:
        with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    material_id = line.split(",")[0]
                    materials.append(material_id)
    except FileNotFoundError:
        print("⚠️  materials.csv non trouvé")
    return materials


def generate_inventory():
    """
    Génère les niveaux de stock RÉALISTES:
    - Multi-entrepôts
    - Quantités cohérentes
    - Quelques anomalies intentionnelles (stocks négatifs)
    """
    materials = load_materials()
    
    if not materials:
        print("⚠️  Matériaux manquants")
        return
    
    inventory = []
    
    # Répartir les matériaux sur les entrepôts
    for _ in range(NUM_INVENTORY_RECORDS):
        material_id = random.choice(materials)
        warehouse = random.choice(WAREHOUSES)
        
        # Quantités réalistes
        quantity_on_hand = random.randint(0, 1500)
        quantity_reserved = random.randint(0, min(500, quantity_on_hand))
        quantity_available = quantity_on_hand - quantity_reserved
        
        # Introduire volontairement quelques anomalies de qualité
        # 5% de chance d'anomalie
        if random.random() < 0.05:
            # Stock négatif intentionnel (pour démontrer data quality)
            quantity_available = -random.randint(1, 100)
        
        reorder_level = random.randint(100, 500)
        
        record = {
            "inventory_id": f"INV-{len(inventory)+1:07d}",
            "material_id": material_id,
            "warehouse": warehouse,
            "quantity_on_hand": quantity_on_hand,
            "quantity_reserved": quantity_reserved,
            "quantity_available": quantity_available,
            "last_movement": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            "reorder_level": reorder_level,
        }
        inventory.append(record)
    
    with open(INVENTORY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=inventory[0].keys())
        writer.writeheader()
        writer.writerows(inventory)
    
    # Statistiques
    negative_stocks = sum(1 for inv in inventory if inv["quantity_available"] < 0)
    print(f"✓ {len(inventory)} lignes de stock générées → {INVENTORY_FILE}")
    if negative_stocks > 0:
        print(f"  ⚠️  Anomalies intentionnelles: {negative_stocks} stocks négatifs (pour data quality)")
    
    return inventory


if __name__ == "__main__":
    generate_inventory()
