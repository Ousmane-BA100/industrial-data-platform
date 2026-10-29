# 🚀 Pipeline d'ingestion avec Airflow

## Vue d'ensemble

Il y a **2 façons** d'exécuter le pipeline:

### Option 1️⃣: **Airflow** (RECOMMANDÉ - Production-ready) ⭐⭐⭐
- ✅ Interface web pour visualiser
- ✅ Logs centralisés
- ✅ Peut être programmé ou déclenché manuellement
- ✅ Meilleur pour le portfolio

### Option 2️⃣: **Script Python simple** (Fallback)
- ✅ Rapide et simple
- ✅ Pas besoin de configuration Airflow
- ⚠️ Moins professionnel

---

## 🎯 Option 1: Utiliser Airflow (RECOMMANDÉ)

### Étape 1️⃣: Docker tourne?

```bash
docker-compose ps
# Vérifier que postgres et api tournent
```

### Étape 2️⃣: Accéder à Airflow

```
http://localhost:8080
# login: admin / admin
```

### Étape 3️⃣: Déclencher le DAG

1. Aller dans l'interface Airflow
2. Chercher le DAG `industrial_data_pipeline`
3. Cliquer sur le DAG
4. Cliquer sur le bouton **"Trigger DAG"** (en haut à droite)
5. Cliquer sur **"Trigger"**

### Étape 4️⃣: Suivre l'exécution

- Voir les tâches en cours dans le **Graph View**
- Voir les logs en cliquant sur chaque tâche
- Attendre que tout soit **green** (succès)

### Étape 5️⃣: Vérifier les données

```bash
# Via PostgreSQL
docker exec industrial-postgres psql -U industrial_user -d industrial_db -c "SELECT COUNT(*) FROM products;"

# Via l'API
curl http://localhost:8000/products
```

---

## 🎯 Option 2: Script Python simple

### Exécuter le pipeline

```bash
# À partir de la racine du projet
python ingestion/run_ingestion.py
```

### Output attendu

```
======================================================================
🏭 INDUSTRIAL DATA PLATFORM - Data Pipeline
======================================================================

📊 PHASE 1: Génération des données
------
✓ 15 fournisseurs RÉALISTES générés → data/sap/suppliers.csv
✓ 50 matériaux générés → data/sap/materials.csv
...

📊 PHASE 2: Création du schéma PostgreSQL
------
✓ Schéma créé avec succès

📊 PHASE 3: Chargement des données
------
Loading suppliers.csv...
Loading materials.csv...
...

📊 PHASE 4: Validation des données
------
✅ Données chargées avec succès:
   • Suppliers: 15
   • Materials: 50
   • Products: 20
   • BOM: ~100
   • Production: 400
   • Quality: 500

📊 TOTAL: ~1,080 lignes

======================================================================
✨ Pipeline complété avec succès!
======================================================================
```

---

## 📊 Architecture du DAG Airflow

```
PHASE 1: GÉNÉRATION (Parallèle)
├─ generate_suppliers
├─ generate_materials
├─ generate_products
├─ generate_inventory
└─ generate_orders
   ↓
├─ generate_bom (dépend de suppliers, materials, products)
├─ generate_production (dépend de products)
└─ generate_quality (dépend de production)

PHASE 2: SCHÉMA
└─ create_schema (dépend de Phase 1)

PHASE 3: CHARGEMENT
└─ load_data (dépend de create_schema)

PHASE 4: VALIDATION
└─ validate_data (dépend de load_data)
```

---

## 🔧 Avantages Airflow

| Aspect | Script simple | Airflow |
|--------|---------------|---------|
| Exécution | Une fois | Programmable |
| Monitoring | Logs terminal | UI web + logs |
| Parallélisation | Séquentielle | Parallèle |
| Retry | Manuel | Automatique |
| Portfolio | ⚠️ Basique | ✅ Production-ready |
| SLA/Alertes | ❌ | ✅ |

---

## 🐛 Troubleshooting

### Airflow ne démarre pas?

```bash
# Vérifier que Docker est lancé
docker-compose ps

# Vérifier les logs Airflow
docker-compose logs airflow | tail -100

# Restart Airflow
docker-compose restart
```

### DAG n'apparaît pas dans Airflow?

```bash
# Vérifier que le fichier DAG est bien placé
ls -la dags/data_pipeline.py

# Attendre 30 secondes (Airflow scan les DAGs toutes les 30s)
sleep 30

# Rafraîchir la page web
# http://localhost:8080
```

### Erreurs de dépendances?

```bash
# Vérifier que les modules sont importables
python -c "from scripts.generate_data.generate_all import main; print('OK')"

# Vérifier les chemins
python -c "import sys; print('\n'.join(sys.path))"
```

---

## 📈 Prochaines étapes

Une fois le pipeline exécuté:

### 1. dbt (Transformations)
```bash
cd dbt
dbt debug
dbt run
dbt test
```

### 2. Ajouter des tests au DAG
```python
# Dans dags/data_pipeline.py
from airflow.operators.sql import SQLCheckOperator

check_suppliers = SQLCheckOperator(
    task_id='check_suppliers_count',
    sql="SELECT COUNT(*) FROM suppliers",
    ...
)
```

### 3. Programmer le DAG
```python
# Dans dags/data_pipeline.py
schedule_interval='0 2 * * *'  # 2 AM tous les jours
```

### 4. Ajouter des alertes
```python
email=['admin@industrial-platform.com']
email_on_failure=True
```

---

## ✅ Résumé

**Pour lancer le pipeline:**

### Avec Airflow (recommandé):
1. Aller sur http://localhost:8080
2. Chercher `industrial_data_pipeline`
3. Cliquer "Trigger DAG"
4. Suivre les logs

### Sans Airflow:
```bash
python ingestion/run_ingestion.py
```

**Les deux font la même chose - utilisez Airflow pour plus de profesionnalisme!** 🚀
