"""
Génération des événements de production
Doit référencer les produits PLM RÉELS
"""
import csv
import random
from datetime import datetime, timedelta
from config import (
    PRODUCTION_FILE, PRODUCTS_FILE, NUM_PRODUCTION_EVENTS,
    PRODUCTION_MACHINES, PRODUCTION_STATUS, PRODUCTION_STATUS_WEIGHTS,
    RANDOM_SEED, SHIFTS
)

random.seed(RANDOM_SEED)


def load_products():
    """Charge les IDs des produits RÉELS"""
    products = []
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    product_id = line.split(",")[0]
                    products.append(product_id)
    except FileNotFoundError:
        print("⚠️  products.csv non trouvé")
    return products


def generate_production():
    """
    Génère les événements de production RÉALISTES:
    - Référence des produits existants
    - Distribution réaliste des statuts (70% PASSED, 15% FAILED, 15% REWORK)
    - Chronologie réaliste des dates
    - Quantités réalistes par événement
    """
    products = load_products()
    
    if not products:
        print("⚠️  Produits manquants")
        return
    
    production_events = []
    base_date = datetime(2026, 6, 1)  # Commencer 3 mois avant today
    
    for i in range(NUM_PRODUCTION_EVENTS):
        # Chronologie progressive
        event_date = base_date + timedelta(
            days=random.randint(0, 108),  # 3-4 mois de données
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Sélectionner un produit RÉEL
        product_id = random.choice(products)
        
        event = {
            "production_event_id": f"PROD-{i+1:07d}",
            "product_id": product_id,
            "machine_id": random.choice(PRODUCTION_MACHINES),
            "quantity_produced": random.randint(5, 50),  # Quantités réalistes
            "event_timestamp": event_date.isoformat(),
            "shift": random.choice(SHIFTS),
            "operator_id": f"OPE-{random.randint(1, 50):03d}",
            "status": random.choices(
                PRODUCTION_STATUS,
                weights=PRODUCTION_STATUS_WEIGHTS
            )[0],
        }
        production_events.append(event)
    
    # Trier par date pour plus de réalisme chronologique
    production_events.sort(key=lambda x: x["event_timestamp"])
    
    with open(PRODUCTION_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=production_events[0].keys())
        writer.writeheader()
        writer.writerows(production_events)
    
    print(f"✓ {len(production_events)} événements de production générés → {PRODUCTION_FILE}")
    return production_events


if __name__ == "__main__":
    generate_production()
