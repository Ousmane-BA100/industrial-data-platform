"""
Génération des résultats de contrôle qualité
**ULTRA-CRITIQUE**: Cohérence ABSOLUE avec production_events
- Inspect uniquement des productions existantes
- Défauts cohérents avec le statut de production
- Chronologie respectée (inspection ≥ production)
"""
import csv
import random
from datetime import datetime, timedelta
from config import (
    QUALITY_FILE, PRODUCTION_FILE, NUM_QUALITY_INSPECTIONS,
    QUALITY_DEFECTS, RANDOM_SEED, QUALITY_TESTS
)

random.seed(RANDOM_SEED)


def load_production_events():
    """
    Charge les événements de production
    Retourne: liste de dicts {id, status, timestamp}
    """
    production_events = []
    try:
        with open(PRODUCTION_FILE, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 0:
                    parts = line.strip().split(",")
                    # Parsing CSV: production_event_id,product_id,machine_id,quantity_produced,event_timestamp,shift,operator_id,status
                    event = {
                        "id": parts[0],
                        "status": parts[7],  # Index du statut
                        "timestamp": parts[4],  # Index du timestamp
                    }
                    production_events.append(event)
    except (FileNotFoundError, IndexError) as e:
        print(f"⚠️  Erreur lecture production_events.csv: {e}")
    
    return production_events


def get_defects_for_status(prod_status):
    """
    Retourne les défauts COHÉRENTS avec le statut de production
    """
    defects = []
    for defect_code, allowed_statuses in QUALITY_DEFECTS.items():
        if prod_status in allowed_statuses:
            defects.append(defect_code)
    return defects if defects else ["NO_DEFECT"]


def generate_quality():
    """
    Génère les inspections qualité avec COHÉRENCE ABSOLUE:
    1. Chaque inspection référence une production réelle
    2. Les défauts correspondent au statut de production
    3. La chronologie est respectée
    4. Peut y avoir 0, 1 ou plusieurs inspections par production
    """
    production_events = load_production_events()
    
    if not production_events:
        print("⚠️  Événements de production manquants")
        return
    
    quality_inspections = []
    insp_index = 1
    
    # Pour chaque événement de production
    for prod_event in production_events:
        prod_id = prod_event["id"]
        prod_status = prod_event["status"]
        
        # Décider du nombre d'inspections pour cette production
        # PASSED: 70% → 1 inspection
        # FAILED: 100% → 1-2 inspections
        # REWORK: 80% → 1-2 inspections
        
        should_inspect = True
        if prod_status == "PASSED":
            should_inspect = random.random() < 0.95  # 95% sont inspectés
            num_inspections = 1 if should_inspect else 0
        elif prod_status == "FAILED":
            should_inspect = True
            num_inspections = random.randint(1, 2)  # 1-2 inspections
        elif prod_status == "REWORK":
            should_inspect = random.random() < 0.9  # 90% sont inspectés
            num_inspections = random.randint(1, 2) if should_inspect else 0
        else:
            num_inspections = 0
        
        # Créer les inspections
        for insp_num in range(num_inspections):
            # Sélectionner un défaut cohérent avec le statut de production
            available_defects = get_defects_for_status(prod_status)
            defect_code = random.choice(available_defects)
            
            # Déterminer le statut de l'inspection basé sur la production
            if prod_status == "PASSED":
                inspection_status = "PASSED"
                defect_code = "NO_DEFECT"
            elif prod_status == "FAILED":
                inspection_status = "FAILED"
                # Forcer un défaut pour FAILED
                non_no_defect = [d for d in available_defects if d != "NO_DEFECT"]
                defect_code = random.choice(non_no_defect) if non_no_defect else random.choice(available_defects)
            else:  # REWORK
                # Pour REWORK: résultat variable
                inspection_status = random.choice(["PASSED", "FAILED"])
                if inspection_status == "FAILED":
                    non_no_defect = [d for d in available_defects if d != "NO_DEFECT"]
                    defect_code = random.choice(non_no_defect) if non_no_defect else defect_code
                else:
                    defect_code = "NO_DEFECT"
            
            # Parser la date de production pour la chronologie
            try:
                prod_timestamp = datetime.fromisoformat(prod_event["timestamp"])
                # Inspection quelques jours après la production
                inspection_date = prod_timestamp + timedelta(days=random.randint(0, 3))
            except:
                inspection_date = datetime.now()
            
            inspection = {
                "inspection_id": f"QI-{insp_index:07d}",
                "production_event_id": prod_id,
                "inspection_date": inspection_date.strftime("%Y-%m-%d"),
                "inspector_id": f"INS-{random.randint(1, 30):03d}",
                "test_type": random.choice(QUALITY_TESTS),
                "defect_code": defect_code,
                "status": inspection_status,
                "comments": f"Inspection completed - {defect_code}",
            }
            quality_inspections.append(inspection)
            insp_index += 1
            
            # Limite du nombre total d'inspections
            if len(quality_inspections) >= NUM_QUALITY_INSPECTIONS:
                break
        
        if len(quality_inspections) >= NUM_QUALITY_INSPECTIONS:
            break
    
    # Tronquer si dépassement
    quality_inspections = quality_inspections[:NUM_QUALITY_INSPECTIONS]
    
    if not quality_inspections:
        print("⚠️  Aucune inspection qualité générée!")
        return
    
    with open(QUALITY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=quality_inspections[0].keys())
        writer.writeheader()
        writer.writerows(quality_inspections)
    
    # Afficher les statistiques de cohérence
    passed_inspections = sum(1 for i in quality_inspections if i["status"] == "PASSED")
    failed_inspections = sum(1 for i in quality_inspections if i["status"] == "FAILED")
    
    print(f"✓ {len(quality_inspections)} inspections qualité COHÉRENTES générées → {QUALITY_FILE}")
    print(f"  ├─ PASSED: {passed_inspections}")
    print(f"  └─ FAILED: {failed_inspections}")
    
    return quality_inspections


if __name__ == "__main__":
    generate_quality()
