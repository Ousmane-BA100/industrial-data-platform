# 🔧 Scripts de Génération des Données

## Vue d'ensemble

Les scripts de ce répertoire génèrent **des données synthétiques réalistes** pour la plateforme data industrielle.

**Point clé:** Les données respectent les **relations métier cohérentes** entre SAP → PLM → Production → Quality.

---

## Structure

```
scripts/generate_data/
├── config.py                    # Configuration centralisée
├── generate_suppliers.py        # Phase 1: Fournisseurs SAP
├── generate_materials.py        # Phase 1: Matériaux SAP (noms réalistes)
├── generate_products.py         # Phase 2: Produits PLM
├── generate_bom.py              # Phase 2: Nomenclatures (BOM)
├── generate_inventory.py        # Phase 1: Stock multi-entrepôts
├── generate_orders.py           # Phase 1: Commandes d'approvisionnement
├── generate_production.py       # Phase 3: Événements de production
├── generate_quality.py          # Phase 4: Inspections qualité
└── generate_all.py              # Orchestrateur maître
```

---

## 🚀 Démarrage rapide

### Générer toutes les données (recommandé)

```bash
cd scripts/generate_data
python generate_all.py
```

**Output:**
```
======================================================================
  🏭 GÉNÉRATION DES DONNÉES SYNTHÉTIQUES
======================================================================

✨ Les données respectent les relations métier:
   SAP/ERP → PLM → Production → Quality
   avec cohérence absolue

────────────────────────────────────────────────────────────────────
📍 PHASE 1: SAP / ERP - Données d'approvisionnement et matériaux
────────────────────────────────────────────────────────────────────

Génération des fournisseurs...
✓ 15 fournisseurs générés → data/sap/suppliers.csv
...
```

---

## 🔄 Phases de génération

### Phase 1: SAP/ERP

**Dépendances:** Aucune (données maître)

```
1. generate_suppliers.py    → 15 fournisseurs
2. generate_materials.py    → 50 matériaux (avec fournisseurs)
3. generate_inventory.py    → 100 lignes de stock (anomalies incluses)
4. generate_orders.py       → 250 commandes (matériaux & fournisseurs)
```

### Phase 2: PLM

**Dépendances:** Phase 1 (matériaux SAP)

```
1. generate_products.py     → 20 produits (familles réalistes)
2. generate_bom.py          → ~100 lignes BOM
   └─ Référence les matériaux SAP de Phase 1
```

### Phase 3: Production

**Dépendances:** Phase 2 (produits PLM)

```
1. generate_production.py   → 400 événements de production
   └─ Référence les produits PLM de Phase 2
```

### Phase 4: Quality

**Dépendances:** Phase 3 (production)

```
1. generate_quality.py      → 500 inspections
   └─ Référence les productions de Phase 3
   └─ Défauts cohérents avec le statut de production
```

---

## 📝 Configuration

Éditer `config.py` pour personnaliser:

```python
# Nombre de records
NUM_SUPPLIERS = 15
NUM_MATERIALS = 50
NUM_PRODUCTS = 20
NUM_INVENTORY_RECORDS = 100
NUM_ORDERS = 250
NUM_PRODUCTION_EVENTS = 400
NUM_QUALITY_INSPECTIONS = 500

# Reproductibilité
RANDOM_SEED = 42  # Changer pour nouvelles données
```

### Familles de produits

Défini dans `config.py`:

```python
PRODUCT_FAMILIES = {
    "HPC-CLUSTER": {
        "name": "High Performance Computing Cluster",
        "price": 50000,
        "components": ["CPU", "MEMORY", "STORAGE", "PSU", "FAN"]
    },
    "SERVER-RACK": { ... },
    "STORAGE-UNIT": { ... },
    ...
}
```

### Matériaux par catégorie

```python
MATERIALS_BY_CATEGORY = {
    "CPU": ["CPU-X86-64-I9", "CPU-X86-64-I7", ...],
    "MEMORY": ["MEMORY-DDR5-64GB", "MEMORY-DDR5-32GB", ...],
    "STORAGE": ["SSD-NVME-3.84TB", "SSD-SATA-2TB", ...],
    ...
}
```

---

## ✨ Caractéristiques des données générées

### Relations métier garanties

- ✅ Matériaux dans BOM existent réellement dans SAP
- ✅ Produits en production existent réellement dans PLM
- ✅ Inspections qualité réferencent des productions réelles
- ✅ Défauts cohérents avec le statut de production

### Réalisme

- ✅ Noms explicites (CPU-X86-64-I9, MEMORY-DDR5-64GB, etc.)
- ✅ Quantités réalistes par type de composant
- ✅ Chronologie progressive (dates cohérentes)
- ✅ Distribution réaliste des statuts (70% PASSED, 15% FAILED, 15% REWORK)

### Anomalies intentionnelles

- ✅ ~5% des stocks sont négatifs (pour data quality testing)
- ✅ ~2% des inspections qualité ont des défauts incohérents
- ✅ Toutes les anomalies sont documentées

---

## 🧪 Tests de cohérence

Après génération, vérifier la cohérence:

```bash
# Vérifier que les matériaux de BOM existent
cd ../../ingestion
python create_schema.py
python load_data.py

# Vérifier les relations
psql -U industrial_user -d industrial_db -c "
SELECT COUNT(*) as orphan_bom_lines
FROM bom b
WHERE NOT EXISTS (SELECT 1 FROM materials m WHERE m.material_id = b.component_id);
"
# Devrait retourner: 0
```

---

## 📊 Statistiques des données

Affichées après génération:

```
📊 STATISTIQUES DE COHÉRENCE:

  SAP/ERP:
    ├─ Fournisseurs: 15
    ├─ Matériaux: 50
    ├─ Lignes d'inventaire: 100
    └─ Commandes: 250

  PLM:
    ├─ Produits: 20
    └─ Lignes BOM: ~100

  Production:
    └─ Événements: 400

  Quality:
    └─ Inspections: 500
```

---

## 🔍 Exemples de données

### Fournisseur
```
supplier_id: SUP-00001
name: TechSupply Inc. 1
country: DE
city: Berlin
active: True
payment_terms: 45
```

### Matériau (réaliste!)
```
material_id: CPU-X86-64-I9
description: CPU-X86-64-I9 - High performance component
category: CPU
unit_price: 1250.50
supplier_id: SUP-00003
```

### Produit
```
product_id: HPC-CLUSTER-001
name: High Performance Computing Cluster - Model 1
family: HPC-CLUSTER
unit_price: 55000.00
```

### BOM (cohérent avec produit)
```
product_id: HPC-CLUSTER-001
component_id: CPU-X86-64-I9
quantity: 2

product_id: HPC-CLUSTER-001
component_id: MEMORY-DDR5-64GB
quantity: 16

product_id: HPC-CLUSTER-001
component_id: SSD-NVME-3.84TB
quantity: 4
```

### Production
```
production_event_id: PROD-0000001
product_id: HPC-CLUSTER-001
machine_id: ASM-LINE-01
quantity_produced: 5
status: PASSED
```

### Quality (cohérent)
```
inspection_id: QI-0000001
production_event_id: PROD-0000001
defect_code: NO_DEFECT
status: PASSED
```

---

## 🛠️ Utilisation en développement

### Régénérer les données

```bash
# Changer le seed dans config.py
RANDOM_SEED = 123

# Régénérer
python generate_all.py
```

### Ajouter des matériaux

```python
# Dans config.py, ajouter une catégorie:
MATERIALS_BY_CATEGORY = {
    ...
    "NEW_CATEGORY": [
        "NEW-COMPONENT-01",
        "NEW-COMPONENT-02",
    ]
}
```

### Augmenter le volume de données

```python
# Dans config.py:
NUM_PRODUCTION_EVENTS = 1000  # Au lieu de 400
NUM_QUALITY_INSPECTIONS = 1500  # Au lieu de 500
```

---

## 📖 Documentation complète

- [docs/data/data-generation.md](../../docs/data/data-generation.md) - Guide génération
- [docs/data/data-model.md](../../docs/data/data-model.md) - Schéma PostgreSQL
- [docs/data/data-quality-anomalies.md](../../docs/data/data-quality-anomalies.md) - Anomalies intentionnelles

---

## ✅ Checklist avant utilisation

- [ ] Python 3.11+ installé
- [ ] Dépendances: `pip install pandas`
- [ ] Répertoire `data/` créé
- [ ] Seed configuré dans `config.py`
- [ ] Espace disque suffisant (~10MB)

---

## 🚀 Prochaines étapes

1. **Générer les données:**
   ```bash
   python generate_all.py
   ```

2. **Charger dans PostgreSQL:**
   ```bash
   cd ../../ingestion
   python run_ingestion.py
   ```

3. **Implémenter dbt:**
   ```bash
   cd ../../dbt
   dbt debug
   dbt run
   dbt test
   ```

4. **Utiliser dans l'API:**
   ```bash
   uvicorn api.main:app --reload
   ```

---

**Les données synthétiques générées sont adaptées pour une démo ou un portfolio technique! 🎉**
