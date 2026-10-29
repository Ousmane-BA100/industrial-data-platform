"""
Génération des matériaux SAP/ERP
Crée des matériaux RÉELS qui seront référencés dans les BOMs
"""
import csv
import random
from config import (
    MATERIALS_FILE, NUM_MATERIALS, RANDOM_SEED, SUPPLIERS_FILE,
    MATERIALS_BY_CATEGORY
)

random.seed(RANDOM_SEED)


def load_suppliers():
    """Charge les IDs des fournisseurs"""
    suppliers = []
    try:
        with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:  # Skip header
                    supplier_id = line.split(",")[0]
                    suppliers.append(supplier_id)
    except FileNotFoundError:
        print("⚠️  suppliers.csv non trouvé - génération des fournisseurs d'abord")
    return suppliers


def generate_materials():
    """
    Génère les matériaux avec noms RÉALISTES
    Crée des composants qui seront vraiment utilisés dans les BOMs
    """
    suppliers = load_suppliers()
    
    if not suppliers:
        print("⚠️  Impossible de générer les matériaux sans fournisseurs")
        return
    
    material_catalog = [
        (material_name, category)
        for category, material_names in MATERIALS_BY_CATEGORY.items()
        for material_name in material_names
    ]
    material_definitions = list(material_catalog)

    variant = 1
    while len(material_definitions) < NUM_MATERIALS:
        for material_name, category in material_catalog:
            if len(material_definitions) >= NUM_MATERIALS:
                break
            material_definitions.append((f"{material_name}-V{variant}", category))
        variant += 1

    materials = []
    for material_id, category in material_definitions[:NUM_MATERIALS]:
        material = {
            "material_id": material_id,
            "description": f"{material_id} - High performance component",
            "category": category,
            "unit": random.choice(["PCS", "KG"]),
            "supplier_id": random.choice(suppliers),
            "unit_price": round(random.uniform(50, 5000), 2),
            "lead_time_days": random.randint(5, 60),
            "active": True,
        }
        materials.append(material)
    
    with open(MATERIALS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=materials[0].keys())
        writer.writeheader()
        writer.writerows(materials)
    
    print(f"✓ {len(materials)} matériaux RÉALISTES générés → {MATERIALS_FILE}")
    return materials


if __name__ == "__main__":
    generate_materials()
