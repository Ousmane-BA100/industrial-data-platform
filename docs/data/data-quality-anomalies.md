# 🔍 Anomalies Intentionnelles - Data Quality Showcase

## Vue d'ensemble

Ce document décrit les anomalies **volontairement introduites** dans les données synthétiques pour démontrer la nécessité et l'efficacité des **contrôles Data Quality** avec dbt.

Ces anomalies ne sont **pas des bugs de génération** mais des **cas réels** qu'on rencontre dans les data warehouses industriels.

---

## Anomalies par source

### 1️⃣ SAP/ERP - Inventory (Stock)

#### Anomalie: Stocks négatifs

**Fréquence:** ~5% des lignes d'inventaire

**Cause réelle:** 
- Entrées/sorties mal synchronisées
- Correction d'erreurs non compensée
- Systèmes legacy incompatibles

**Exemple:**
```
material_id: CPU-X86-64-I9
warehouse: WH-01
quantity_on_hand: 250
quantity_reserved: 300
quantity_available: -50  ❌ INVALIDE
```

**Test dbt attendu:**
```sql
-- quality_negative_inventory.sql
SELECT COUNT(*) as negative_count
FROM {{ ref('stg_inventory') }}
WHERE quantity_available < 0
-- Devrait alerter ou rejeter ces lignes
```

---

### 2️⃣ Production → Quality

#### Anomalie: Défaut incohérent avec statut production

**Fréquence:** ~2% des inspections

**Cause réelle:**
- Erreur de saisie de l'inspecteur
- Confusion entre les références de productions
- Donnée archivée et modifiée manuellement

**Exemple:**
```
production_event_id: PROD-0000125
product_id: HPC-CLUSTER-001
status: PASSED  ← Production réussie

inspection_id: QI-0000089
production_event_id: PROD-0000125
defect_code: ELECTRICAL_FAILURE  ❌ Incohérent
status: FAILED
```

**Test dbt attendu:**
```sql
-- quality_production_quality_coherence.sql
SELECT 
  qi.inspection_id,
  pe.production_event_id,
  pe.status as production_status,
  qi.status as quality_status,
  qi.defect_code
FROM {{ ref('fact_quality') }} qi
JOIN {{ ref('fact_production') }} pe
  ON qi.production_event_id = pe.production_event_id
WHERE 
  (pe.status = 'PASSED' AND qi.defect_code != 'NO_DEFECT')
  OR (pe.status = 'FAILED' AND qi.defect_code = 'NO_DEFECT')
```

---

### 3️⃣ Chronologie (Dates)

#### Anomalie: Inspection avant production

**Fréquence:** ~1% des inspections

**Cause réelle:**
- Mauvaise synchronisation des systèmes
- Correction manuelle des dates
- Horloge du système incohérente

**Exemple:**
```
production_event:
  production_event_id: PROD-0000150
  event_timestamp: 2026-09-15 14:00:00

inspection:
  inspection_id: QI-0000110
  production_event_id: PROD-0000150
  inspection_date: 2026-09-14 10:00:00  ❌ Avant la production!
```

**Test dbt attendu:**
```sql
-- quality_inspection_timeline.sql
SELECT 
  qi.inspection_id,
  pe.event_timestamp as production_date,
  qi.inspection_date,
  (qi.inspection_date - CAST(pe.event_timestamp AS DATE)) as days_gap
FROM {{ ref('fact_quality') }} qi
JOIN {{ ref('fact_production') }} pe
  ON qi.production_event_id = pe.production_event_id
WHERE qi.inspection_date < CAST(pe.event_timestamp AS DATE)
```

---

## Stratégies de test dbt

### Tier 1: Contrôles basiques

```yaml
# models/staging/stg_quality_inspections.yml
- name: stg_quality_inspections
  tests:
    - not_null:
        column_name: inspection_id
    - unique:
        column_name: inspection_id
    - not_null:
        column_name: production_event_id
```

### Tier 2: Contrôles relationnels

```yaml
# models/staging/stg_quality_inspections.yml
- name: stg_quality_inspections
  tests:
    - relationships:
        to: ref('stg_production_events')
        field: production_event_id
        # Assure que chaque inspection référence une production réelle
```

### Tier 3: Contrôles métier

```sql
-- models/tests/assert_quality_production_coherence.sql
SELECT *
FROM {{ ref('stg_quality_inspections') }} qi
WHERE NOT EXISTS (
  SELECT 1 FROM {{ ref('stg_production_events') }} pe
  WHERE pe.production_event_id = qi.production_event_id
    AND qi.inspection_date >= CAST(pe.event_timestamp AS DATE)
)
```

---

## Comment les démontrer

### 1️⃣ Générer les données

```bash
python scripts/generate_data/generate_all.py
```

### 2️⃣ Charger dans PostgreSQL

```bash
python ingestion/run_ingestion.py
```

### 3️⃣ Exécuter dbt

```bash
cd dbt
dbt run
dbt test
```

### 4️⃣ Voir les anomalies

```sql
-- Requête pour identifier les stocks négatifs
SELECT COUNT(*) as negative_inventory_count
FROM public.inventory
WHERE quantity_available < 0;

-- Requête pour trouver les incohérences qualité
SELECT 
  qi.inspection_id,
  pe.status as production_status,
  qi.status as quality_status,
  qi.defect_code
FROM public.quality_inspections qi
JOIN public.production_events pe
  ON qi.production_event_id = pe.production_event_id
WHERE (
  (pe.status = 'PASSED' AND qi.defect_code != 'NO_DEFECT')
  OR (pe.status = 'FAILED' AND qi.defect_code = 'NO_DEFECT')
);
```

---

## Bénéfices pédagogiques

### Pour un entretien technique:

✅ **Démontre la compréhension** des problèmes réels de data quality
✅ **Montre l'implémentation** de tests robustes
✅ **Prouve les compétences** en dbt et SQL
✅ **Illustre la valeur** d'une architecture data
✅ **Crédibilise le portfolio** (données réalistes ≠ données aléatoires)

### Pour un projet de production:

✅ Identifier et corriger les anomalies avant qu'elles n'impactent les rapports
✅ Créer des alertes automatisées
✅ Tracer la provenance des données
✅ Améliorer continuellement la qualité

---

## Paramètres de génération

Pour modifier les anomalies, éditer `scripts/generate_data/config.py`:

```python
# config.py

# Taux d'anomalies
ANOMALY_RATES = {
    "negative_inventory": 0.05,      # 5%
    "quality_defect_mismatch": 0.02,  # 2%
    "inspection_date_error": 0.01,   # 1%
}

# Pour activez/désactiver les anomalies:
ENABLE_INTENTIONAL_ANOMALIES = True
```

---

## Documentation d'audit

Chaque anomalie est **documentée et traçable**:

1. **Générée volontairement** avec un seed fixe
2. **Identifiable** via patterns spécifiques
3. **Corrigible** par des tests dbt
4. **Exploitable** pour la démonstration

---

## Prochain pas

Implémenter dans dbt:

1. `models/staging/stg_*.sql` - Nettoyage basique
2. `models/tests/assert_*.sql` - Assertions métier
3. `models/marts/fact_*.sql` - Tables optimisées
4. Documenter les anomalies trouvées et leur résolution

**Cela démontre une vraie plateforme data production-ready! 🚀**
