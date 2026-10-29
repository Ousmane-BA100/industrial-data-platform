"""
Génération des commandes SAP/ERP
Référence les matériaux ET fournisseurs RÉELS avec relations cohérentes
"""
import csv
import random
from datetime import datetime, timedelta
from config import (
    ORDERS_FILE, MATERIALS_FILE, SUPPLIERS_FILE, NUM_ORDERS, RANDOM_SEED
)

random.seed(RANDOM_SEED)


def load_materials_with_suppliers():
    """
    Charge les matériaux avec leurs fournisseurs respectifs
    Retourne: {material_id: supplier_id}
    """
    material_suppliers = {}
    try:
        with open(MATERIALS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    parts = line.strip().split(",")
                    material_id = parts[0]
                    supplier_id = parts[4]  # Index du supplier_id dans materials.csv
                    material_suppliers[material_id] = supplier_id
    except (FileNotFoundError, IndexError) as e:
        print(f"⚠️  Erreur lecture materials.csv: {e}")
    
    return material_suppliers


def load_suppliers():
    """Charge les IDs des fournisseurs"""
    suppliers = []
    try:
        with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    supplier_id = line.split(",")[0]
                    suppliers.append(supplier_id)
    except FileNotFoundError:
        print("⚠️  suppliers.csv non trouvé")
    
    return suppliers


def generate_orders():
    """
    Génère les commandes d'approvisionnement avec cohérence:
    - Chaque commande référence un matériau réel
    - Le fournisseur est celui associé au matériau
    - Chronologie réaliste
    """
    material_suppliers = load_materials_with_suppliers()
    suppliers = load_suppliers()
    
    if not material_suppliers or not suppliers:
        print("⚠️  Matériaux ou fournisseurs manquants")
        return
    
    orders = []
    base_date = datetime(2026, 3, 1)  # Commandes des 6 derniers mois
    
    for i in range(NUM_ORDERS):
        # Sélectionner un matériau RÉEL
        material_id = random.choice(list(material_suppliers.keys()))
        
        # Récupérer son fournisseur RÉEL
        supplier_id = material_suppliers[material_id]
        
        # Dates réalistes
        order_date = base_date + timedelta(days=random.randint(0, 180))
        delivery_date = order_date + timedelta(days=random.randint(5, 60))
        
        # Déterminer le statut de la commande
        # Plus la date est proche, plus il y a de chances que ce soit RECEIVED
        days_ago = (datetime.now() - order_date).days
        if days_ago > 90:
            status = random.choices(
                ["OPEN", "IN_TRANSIT", "RECEIVED", "CANCELLED"],
                weights=[5, 10, 80, 5]
            )[0]
        elif days_ago > 30:
            status = random.choices(
                ["OPEN", "IN_TRANSIT", "RECEIVED", "CANCELLED"],
                weights=[10, 30, 50, 10]
            )[0]
        else:
            status = random.choices(
                ["OPEN", "IN_TRANSIT", "RECEIVED", "CANCELLED"],
                weights=[30, 40, 20, 10]
            )[0]
        
        unit_price = round(random.uniform(50, 5000), 2)
        quantity = random.randint(10, 1000)
        total_amount = round(unit_price * quantity, 2)
        
        order = {
            "order_id": f"PO-{i+1:07d}",
            "supplier_id": supplier_id,
            "material_id": material_id,
            "quantity": quantity,
            "unit": "PCS",
            "order_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "status": status,
            "unit_price": unit_price,
            "total_amount": total_amount,
        }
        orders.append(order)
    
    with open(ORDERS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=orders[0].keys())
        writer.writeheader()
        writer.writerows(orders)
    
    # Statistiques de cohérence
    status_counts = {}
    for order in orders:
        status = order["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"✓ {len(orders)} commandes COHÉRENTES générées → {ORDERS_FILE}")
    for status, count in status_counts.items():
        print(f"  ├─ {status}: {count}")
    
    return orders


if __name__ == "__main__":
    generate_orders()
