# 📋 Génération des données synthétiques

## Vue d'ensemble

Les données synthétiques de ce projet sont générées par une suite de scripts Python qui créent des relations métier **cohérentes et réalistes** entre 4 systèmes industriels distincts : SAP/ERP, PLM, Production et Quality.

## Architecture de la génération

```
Phase 1: SAP/ERP
├── Fournisseurs (suppliers.csv)
├── Matériaux (materials.csv)
├── Stock (inventory.csv)
└── Commandes (orders.csv)

Phase 2: PLM
├── Produits (products.csv)
└── BOM - Nomenclature (bom.csv)

Phase 3: Production
└── Événements (production_events.csv)

Phase 4: Quality
└── Inspections (quality_inspections.csv)
```

## Relations métier

### Cohérence SAP → PLM
- Chaque **matériau SAP** peut être composant d'une **BOM PLM**
- Chaque **produit PLM** est composé de **matériaux SAP**

### Cohérence PLM → Production
- Chaque **événement de production** fabrique un **produit existant**
- Les quantités produites sont réalistes

### Cohérence Production → Quality
- Chaque **inspection qualité** référence une **production réelle**
- Les **statuts de qualité** sont cohérents avec le **statut de production**:
  - Production PASSED → Qualité généralement NO_DEFECT
  - Production FAILED → Qualité généralement FAILED avec défaut cohérent
  - Production REWORK → Qualité variable

## Exécution

### Génération complète (recommandé)

```bash
python scripts/generate_data/generate_all.py
```

Cela exécute tous les générateurs dans le bon ordre avec dépendances.

### Génération partielle

```bash
# Régénérer uniquement les fournisseurs
python scripts/generate_data/generate_suppliers.py

# Régénérer matériaux + stock + commandes (après suppliers)
python scripts/generate_data/generate_materials.py
python scripts/generate_data/generate_inventory.py
python scripts/generate_data/generate_orders.py

# Régénérer produits + BOM (indépendant)
python scripts/generate_data/generate_products.py
python scripts/generate_data/generate_bom.py

# Régénérer production
python scripts/generate_data/generate_production.py

# Régénérer qualité (dernière phase)
python scripts/generate_data/generate_quality.py
```

## Fichiers générés

Tous les fichiers CSV sont générés dans le répertoire `data/`:

| Fichier | Lignes | Données |
|---------|--------|---------|
| `data/sap/suppliers.csv` | 15 | Fournisseurs actifs/inactifs |
| `data/sap/materials.csv` | 50 | Catégories, prix, délais |
| `data/sap/inventory.csv` | 200 | Multi-entrepôts, niveaux de stock |
| `data/sap/orders.csv` | 300 | Commandes d'approvisionnement |
| `data/plm/products.csv` | 20 | Produits finis et familles |
| `data/plm/bom.csv` | Variable | Relations produits↔composants |
| `data/production/production_events.csv` | 500 | Événements de fabrication |
| `data/quality/quality_inspections.csv` | 500 | Résultats d'inspection |

## Configuration

Modifiez `scripts/generate_data/config.py` pour ajuster:

- `NUM_SUPPLIERS`, `NUM_MATERIALS`, `NUM_PRODUCTS`, etc. → Nombre d'enregistrements
- `PRODUCTION_MACHINES` → Machines disponibles
- `PRODUCTION_STATUS` → Statuts possibles
- `QUALITY_DEFECTS` → Types de défauts

## Exemple de données générées

### Fournisseur (SAP)
```
supplier_id: SUP-00001
name: TechSupply Inc. 1
country: DE
city: Berlin
payment_terms: 45
active: True
```

### Matériau (SAP)
```
material_id: CPU-X86-64-01
description: CPU-X86-64 Variant 1
category: CPU
supplier_id: SUP-00005
unit_price: 250.42
lead_time_days: 15
```

### Produit (PLM)
```
product_id: HPC-CLUSTER-001
name: HPC-CLUSTER Model 1
unit_price: 25000.00
weight_kg: 45.32
```

### BOM (PLM)
```
bom_id: BOM-00001
product_id: HPC-CLUSTER-001
component_id: CPU-X86-64-01
quantity: 2
```

### Production
```
production_event_id: PROD-0000001
product_id: HPC-CLUSTER-001
machine_id: ASM-LINE-01
quantity_produced: 5
status: PASSED
timestamp: 2026-09-12T14:30:00
```

### Quality
```
inspection_id: QI-0000001
production_event_id: PROD-0000001
test_type: ELECTRICAL
status: PASSED
defect_code: NO_DEFECT
```

## Anomalies intentionnelles

Le générateur peut introduire des **anomalies contrôlées** pour tester la **Data Quality**:

- ❌ Stocks négatifs (ingestion incorrecte)
- ❌ Matériaux manquants dans les BOM
- ❌ Références circulaires
- ❌ Dates incohérentes

Ces anomalies sont **documentées** et servent à valider les tests dbt.

## Reproductibilité

Tous les générateurs utilisent `RANDOM_SEED = 42` pour garantir la reproductibilité des données.

Pour obtenir des données différentes, modifiez `config.py`:

```python
RANDOM_SEED = 123  # Nouveau seed = données différentes
```
