"""
Génération des fournisseurs SAP/ERP
"""
import csv
import random
from config import SUPPLIERS_FILE, NUM_SUPPLIERS, RANDOM_SEED

random.seed(RANDOM_SEED)

SUPPLIER_NAMES = [
    "TechSupply Inc.",
    "Industrial Parts Co.",
    "GlobalComponents Ltd.",
    "ElectroWorld GmbH",
    "MechaParts Corp.",
    "AdvancedMaterials SA",
    "QualityComponents Ltd.",
    "ProSupplies International",
    "SwiftLogistics AG",
    "PrecisionTech Systems",
    "DynamicParts Trading",
    "IntegralComponents AS",
    "FutureTech Solutions",
    "ReliableSupply Ltd.",
    "VisionaryParts Inc.",
]

COUNTRIES = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "PL", "CZ"]


def generate_suppliers():
    """Génère les fournisseurs avec données réalistes"""
    suppliers = []
    
    for i in range(NUM_SUPPLIERS):
        supplier = {
            "supplier_id": f"SUP-{i+1:05d}",
            "name": SUPPLIER_NAMES[i % len(SUPPLIER_NAMES)] + f" {i+1}",
            "country": random.choice(COUNTRIES),
            "city": random.choice(["Berlin", "Paris", "Milan", "Madrid", "Amsterdam", 
                                   "Brussels", "Vienna", "Zurich", "Warsaw", "Prague"]),
            "contact_email": f"contact@supplier{i+1}.com",
            "phone": f"+49 {random.randint(1000, 9999)} {random.randint(100000, 999999)}",
            "active": random.choice([True, True, True, False]),  # 75% actifs
            "payment_terms": random.randint(30, 120),  # jours
        }
        suppliers.append(supplier)
    
    # Écrire les données
    with open(SUPPLIERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=suppliers[0].keys())
        writer.writeheader()
        writer.writerows(suppliers)
    
    print(f"✓ {NUM_SUPPLIERS} fournisseurs générés → {SUPPLIERS_FILE}")
    return suppliers


if __name__ == "__main__":
    generate_suppliers()
