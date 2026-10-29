# 📊 Modèle de données PostgreSQL

## Vue d'ensemble

Le schéma PostgreSQL **RAW** correspond exactement à la structure des fichiers CSV générés.

```
Schéma: public

Tables SAP/ERP:
├── suppliers
├── materials
├── inventory
└── orders

Tables PLM:
├── products
└── bom

Tables Production:
└── production_events

Tables Quality:
└── quality_inspections
```

## Modèle Entité-Relation

```
suppliers
    ↓
materials ─────┐
    ↓          │
inventory      ├→ bom ← products
    ↓          │          ↓
orders         │     production_events
               │              ↓
               └─────────→ quality_inspections
```

## Définition des tables SAP/ERP

### suppliers

```sql
CREATE TABLE suppliers (
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
```

Clés étrangères:
- Aucune (données maître)

Contraintes:
- `supplier_id` unique et non-nul
- `active` booléen

---

### materials

```sql
CREATE TABLE materials (
    material_id VARCHAR(50) PRIMARY KEY,
    description VARCHAR(500),
    category VARCHAR(50),
    unit VARCHAR(10),
    supplier_id VARCHAR(20) NOT NULL,
    unit_price DECIMAL(10, 2),
    lead_time_days INT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
```

Clés étrangères:
- `supplier_id` → `suppliers.supplier_id`

Contraintes:
- `unit_price >= 0`
- `lead_time_days >= 0`

Indices:
- `CREATE INDEX idx_materials_supplier ON materials(supplier_id);`
- `CREATE INDEX idx_materials_category ON materials(category);`

---

### inventory

```sql
CREATE TABLE inventory (
    inventory_id VARCHAR(20) PRIMARY KEY,
    material_id VARCHAR(50) NOT NULL,
    warehouse VARCHAR(20),
    quantity_on_hand INT DEFAULT 0,
    quantity_reserved INT DEFAULT 0,
    quantity_available INT DEFAULT 0,
    last_movement DATE,
    reorder_level INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);
```

Clés étrangères:
- `material_id` → `materials.material_id`

Contraintes:
- `quantity_available = quantity_on_hand - quantity_reserved`

Indices:
- `CREATE INDEX idx_inventory_material ON inventory(material_id);`
- `CREATE INDEX idx_inventory_warehouse ON inventory(warehouse);`

---

### orders

```sql
CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(10),
    order_date DATE,
    delivery_date DATE,
    status VARCHAR(20),
    unit_price DECIMAL(10, 2),
    total_amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);
```

Clés étrangères:
- `supplier_id` → `suppliers.supplier_id`
- `material_id` → `materials.material_id`

Contraintes:
- `status IN ('OPEN', 'IN_TRANSIT', 'RECEIVED', 'CANCELLED')`
- `delivery_date >= order_date`

Indices:
- `CREATE INDEX idx_orders_supplier ON orders(supplier_id);`
- `CREATE INDEX idx_orders_material ON orders(material_id);`
- `CREATE INDEX idx_orders_status ON orders(status);`

---

## Définition des tables PLM

### products

```sql
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    family VARCHAR(50),
    description TEXT,
    unit_price DECIMAL(12, 2),
    weight_kg DECIMAL(10, 2),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Clés étrangères:
- Aucune (données maître)

Contraintes:
- `product_id` unique et non-nul
- `unit_price >= 0`

---

### bom

```sql
CREATE TABLE bom (
    bom_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    component_id VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(10),
    lead_time_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (component_id) REFERENCES materials(material_id),
    UNIQUE(product_id, component_id)
);
```

Clés étrangères:
- `product_id` → `products.product_id`
- `component_id` → `materials.material_id`

Contraintes:
- `quantity > 0`
- Un produit ne peut avoir qu'un seul type de composant (unicité)

Indices:
- `CREATE INDEX idx_bom_product ON bom(product_id);`
- `CREATE INDEX idx_bom_component ON bom(component_id);`

---

## Définition des tables Production

### production_events

```sql
CREATE TABLE production_events (
    production_event_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    machine_id VARCHAR(20),
    quantity_produced INT,
    event_timestamp TIMESTAMP,
    shift VARCHAR(20),
    operator_id VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

Clés étrangères:
- `product_id` → `products.product_id`

Contraintes:
- `status IN ('PASSED', 'FAILED', 'REWORK')`
- `quantity_produced > 0`

Indices:
- `CREATE INDEX idx_production_product ON production_events(product_id);`
- `CREATE INDEX idx_production_machine ON production_events(machine_id);`
- `CREATE INDEX idx_production_timestamp ON production_events(event_timestamp);`

---

## Définition des tables Quality

### quality_inspections

```sql
CREATE TABLE quality_inspections (
    inspection_id VARCHAR(20) PRIMARY KEY,
    production_event_id VARCHAR(20) NOT NULL,
    inspection_date DATE,
    inspector_id VARCHAR(20),
    test_type VARCHAR(50),
    defect_code VARCHAR(50),
    status VARCHAR(20),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (production_event_id) REFERENCES production_events(production_event_id)
);
```

Clés étrangères:
- `production_event_id` → `production_events.production_event_id`

Contraintes:
- `status IN ('PASSED', 'FAILED')`
- `test_type IN ('VISUAL', 'DIMENSIONAL', 'ELECTRICAL', 'FUNCTIONAL')`

Indices:
- `CREATE INDEX idx_quality_production ON quality_inspections(production_event_id);`
- `CREATE INDEX idx_quality_status ON quality_inspections(status);`
- `CREATE INDEX idx_quality_defect ON quality_inspections(defect_code);`

---

## Schéma d'ingestion

### Phase 1 : RAW (données sources brutes)

```
ingestion/
├── load_sap.py          # Charge SAP → PostgreSQL RAW
├── load_plm.py          # Charge PLM → PostgreSQL RAW
├── load_production.py   # Charge Production → PostgreSQL RAW
└── load_quality.py      # Charge Quality → PostgreSQL RAW
```

### Phase 2 : dbt (transformations)

```
dbt/
├── models/
│   ├── staging/         # Nettoyage et validation
│   │   ├── stg_suppliers.sql
│   │   ├── stg_materials.sql
│   │   └── ...
│   │
│   ├── intermediate/    # Transformations intermédiaires
│   │   ├── int_product_components.sql
│   │   ├── int_production_quality.sql
│   │   └── ...
│   │
│   └── marts/           # Tables d'exploitation
│       ├── fact_production.sql
│       ├── fact_quality.sql
│       ├── dim_products.sql
│       └── ...
└── tests/              # Tests de qualité
```

## Gestion des clés étrangères

```sql
-- Activer les contraintes FK
ALTER TABLE materials ADD CONSTRAINT fk_materials_supplier
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT;

ALTER TABLE inventory ADD CONSTRAINT fk_inventory_material
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE;

ALTER TABLE orders ADD CONSTRAINT fk_orders_supplier
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT;

ALTER TABLE orders ADD CONSTRAINT fk_orders_material
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE RESTRICT;

ALTER TABLE bom ADD CONSTRAINT fk_bom_product
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;

ALTER TABLE bom ADD CONSTRAINT fk_bom_component
    FOREIGN KEY (component_id) REFERENCES materials(material_id) ON DELETE RESTRICT;

ALTER TABLE production_events ADD CONSTRAINT fk_production_product
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT;

ALTER TABLE quality_inspections ADD CONSTRAINT fk_quality_production
    FOREIGN KEY (production_event_id) REFERENCES production_events(production_event_id) ON DELETE CASCADE;
```

## Création du schéma RAW

Le DDL des tables RAW est maintenu dans `ingestion/create_schema.py` et exécuté par la tâche `create_schema` du DAG Airflow avant le chargement des CSV.
