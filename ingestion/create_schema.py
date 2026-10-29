"""
Création du schéma PostgreSQL RAW
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.db import get_engine

# SQL pour créer les tables
SCHEMA_SQL = """
-- Tables SAP/ERP
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country CHAR(2),
    city VARCHAR(100),
    contact_email VARCHAR(255),
    phone VARCHAR(20),
    active BOOLEAN DEFAULT TRUE,
    payment_terms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials (
    material_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(500),
    category VARCHAR(50),
    unit VARCHAR(10),
    supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    unit_price DECIMAL(10, 2),
    lead_time_days INT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id VARCHAR(20) PRIMARY KEY,
    material_id VARCHAR(50) NOT NULL REFERENCES materials(material_id),
    warehouse VARCHAR(20),
    quantity_on_hand INT DEFAULT 0,
    quantity_reserved INT DEFAULT 0,
    quantity_available INT DEFAULT 0,
    last_movement DATE,
    reorder_level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(20) PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL REFERENCES suppliers(supplier_id),
    material_id VARCHAR(50) NOT NULL REFERENCES materials(material_id),
    quantity INT NOT NULL,
    unit VARCHAR(10),
    order_date DATE,
    delivery_date DATE,
    status VARCHAR(20),
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables PLM
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    family VARCHAR(50),
    description TEXT,
    unit_price DECIMAL(12, 2),
    weight_kg DECIMAL(10, 2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bom (
    bom_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    component_id VARCHAR(50) NOT NULL REFERENCES materials(material_id),
    quantity INT NOT NULL,
    unit VARCHAR(10),
    lead_time_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables Production
CREATE TABLE IF NOT EXISTS production_events (
    production_event_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL REFERENCES products(product_id),
    machine_id VARCHAR(20),
    quantity_produced INT,
    event_timestamp TIMESTAMP,
    shift VARCHAR(20),
    operator_id VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tables Quality
CREATE TABLE IF NOT EXISTS quality_inspections (
    inspection_id VARCHAR(20) PRIMARY KEY,
    production_event_id VARCHAR(20) NOT NULL REFERENCES production_events(production_event_id),
    inspection_date DATE,
    inspector_id VARCHAR(20),
    test_type VARCHAR(50),
    defect_code VARCHAR(50),
    status VARCHAR(20),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer les indices
CREATE INDEX IF NOT EXISTS idx_materials_supplier ON materials(supplier_id);
CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
CREATE INDEX IF NOT EXISTS idx_inventory_material ON inventory(material_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory(warehouse);
CREATE INDEX IF NOT EXISTS idx_orders_supplier ON orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_orders_material ON orders(material_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_bom_product ON bom(product_id);
CREATE INDEX IF NOT EXISTS idx_bom_component ON bom(component_id);
CREATE INDEX IF NOT EXISTS idx_production_product ON production_events(product_id);
CREATE INDEX IF NOT EXISTS idx_production_machine ON production_events(machine_id);
CREATE INDEX IF NOT EXISTS idx_production_timestamp ON production_events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_quality_production ON quality_inspections(production_event_id);
CREATE INDEX IF NOT EXISTS idx_quality_status ON quality_inspections(status);
CREATE INDEX IF NOT EXISTS idx_quality_defect ON quality_inspections(defect_code);
"""


def create_schema():
    """Crée le schéma PostgreSQL"""
    engine = get_engine()
    
    if not engine:
        print("❌ Impossible de créer le schéma: pas de connexion DB")
        return False
    
    try:
        with engine.begin() as connection:
            connection.connection.cursor().execute(SCHEMA_SQL)
            print("✓ Schéma PostgreSQL créé avec succès")
            return True
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la création du schéma: {e}") from e


if __name__ == "__main__":
    create_schema()
