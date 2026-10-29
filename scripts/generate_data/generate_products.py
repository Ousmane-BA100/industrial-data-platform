"""
Génération des produits PLM - Produits finis réalistes
"""
import csv
import random
from config import PRODUCTS_FILE, NUM_PRODUCTS, RANDOM_SEED, PRODUCT_FAMILIES

random.seed(RANDOM_SEED)


def generate_products():
    """
    Génère les produits RÉALISTES avec familles cohérentes
    Ces produits seront produits par les événements de production
    """
    products = []
    
    # Pour chaque famille de produits
    family_index = 0
    for family_code, family_data in PRODUCT_FAMILIES.items():
        # Générer 4 variantes par famille
        for variant in range(1, 5):
            if len(products) >= NUM_PRODUCTS:
                break
            
            product = {
                "product_id": f"{family_code}-{variant:03d}",
                "name": f"{family_data['name']} - Model {variant}",
                "family": family_code,
                "description": f"High-performance {family_data['name']} with advanced capabilities",
                "unit_price": round(family_data["price"] * random.uniform(0.8, 1.2), 2),
                "weight_kg": round(family_data["weight"] * random.uniform(0.9, 1.1), 2),
                "active": True,
            }
            products.append(product)
        
        family_index += 1
        if len(products) >= NUM_PRODUCTS:
            break
    
    # Compléter si nécessaire
    while len(products) < NUM_PRODUCTS:
        family_code = random.choice(list(PRODUCT_FAMILIES.keys()))
        family_data = PRODUCT_FAMILIES[family_code]
        product = {
            "product_id": f"{family_code}-{random.randint(100, 999):03d}",
            "name": f"{family_data['name']} Custom",
            "family": family_code,
            "description": f"Customized {family_data['name']}",
            "unit_price": round(family_data["price"] * random.uniform(0.8, 1.5), 2),
            "weight_kg": round(family_data["weight"] * random.uniform(0.9, 1.2), 2),
            "active": random.choice([True, True, True, False]),  # 75% actifs
        }
        products.append(product)
    
    products = products[:NUM_PRODUCTS]
    
    with open(PRODUCTS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)
    
    print(f"✓ {len(products)} produits RÉALISTES générés → {PRODUCTS_FILE}")
    return products


if __name__ == "__main__":
    generate_products()
