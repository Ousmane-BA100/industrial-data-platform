"""
Génération des nomenclatures (BOM - Bill of Materials)
**CRITIQUE**: Doit référencer les produits ET matériaux RÉELS
Relations: Produit → Composants existants avec quantités réalistes
"""
import csv
import random
from config import (
    PRODUCTS_FILE, MATERIALS_FILE, BOM_FILE, RANDOM_SEED,
    PRODUCT_FAMILIES, MATERIALS_BY_CATEGORY
)

random.seed(RANDOM_SEED)


def load_products():
    """Charge les IDs et familles des produits"""
    products = {}
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    parts = line.strip().split(",")
                    product_id = parts[0]
                    family = parts[2]  # Index de 'family' dans CSV
                    products[product_id] = family
    except FileNotFoundError:
        print("⚠️  products.csv non trouvé")
    return products


def load_materials_by_category():
    """Charge les matériaux groupés par catégorie"""
    materials_by_cat = {}
    try:
        with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    parts = line.strip().split(",")
                    material_id = parts[0]
                    category = parts[2]  # Index de 'category' dans CSV
                    
                    if category not in materials_by_cat:
                        materials_by_cat[category] = []
                    materials_by_cat[category].append(material_id)
    except FileNotFoundError:
        print("⚠️  materials.csv non trouvé")
    return materials_by_cat


def get_components_for_family(family_code, materials_by_cat):
    """
    Retourne les catégories de composants pour une famille de produits
    Garantit que chaque produit a des composants cohérents
    """
    if family_code not in PRODUCT_FAMILIES:
        return random.choice(list(PRODUCT_FAMILIES.values()))["components"]
    
    return PRODUCT_FAMILIES[family_code]["components"]


def generate_bom():
    """
    Génère les BOMs avec relations COHÉRENTES:
    - Chaque produit a des composants existants
    - Quantités réalistes selon le type de produit
    - Chaque ligne BOM référence un matériau réel
    """
    products = load_products()
    materials_by_cat = load_materials_by_category()
    
    if not products or not materials_by_cat:
        print("⚠️  Produits ou matériaux manquants")
        return
    
    bom_lines = []
    bom_index = 1
    
    # Pour chaque produit, créer ses composants
    for product_id, family in products.items():
        # Récupérer les catégories de composants pour cette famille
        component_categories = get_components_for_family(family, materials_by_cat)
        
        # Mélanger les catégories pour plus de variété
        selected_categories = random.sample(
            component_categories, 
            min(len(component_categories), random.randint(2, len(component_categories)))
        )
        
        # Créer une ligne BOM pour chaque catégorie sélectionnée
        for category in selected_categories:
            # Vérifier que cette catégorie a des matériaux
            if category not in materials_by_cat or not materials_by_cat[category]:
                continue
            
            # Sélectionner un matériau réel de cette catégorie
            component_id = random.choice(materials_by_cat[category])
            
            # Quantité réaliste selon le type de composant
            quantity_map = {
                "CPU": random.randint(1, 4),
                "MEMORY": random.randint(4, 32),
                "STORAGE": random.randint(1, 8),
                "PSU": random.randint(1, 3),
                "FAN": random.randint(4, 12),
                "GPU": random.randint(1, 4),
                "NETWORK": random.randint(1, 4),
                "CONTROLLER": random.randint(1, 2),
                "PROCESSOR": random.randint(1, 2),
            }
            
            quantity = quantity_map.get(category, random.randint(1, 10))
            
            bom_line = {
                "bom_id": f"BOM-{bom_index:06d}",
                "product_id": product_id,
                "component_id": component_id,
                "quantity": quantity,
                "unit": "PCS",
                "lead_time_days": random.randint(5, 30),
            }
            bom_lines.append(bom_line)
            bom_index += 1
    
    # Écrire les BOMs
    if not bom_lines:
        print("⚠️  Aucune ligne BOM générée!")
        return
    
    with open(BOM_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=bom_lines[0].keys())
        writer.writeheader()
        writer.writerows(bom_lines)
    
    print(f"✓ {len(bom_lines)} lignes BOM COHÉRENTES générées → {BOM_FILE}")
    return bom_lines


if __name__ == "__main__":
    generate_bom()
