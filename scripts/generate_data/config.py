"""
Configuration pour la génération des données synthétiques
Respecte les relations métier SAP → PLM → Production → Quality
"""
import os
from pathlib import Path

# Nombre de records
NUM_SUPPLIERS = 15
NUM_MATERIALS = 50
NUM_PRODUCTS = 20
NUM_BOM_LINES_PER_PRODUCT = 5  # Chaque produit a ~5 composants
NUM_INVENTORY_RECORDS = 100  # Multi-entrepôts
NUM_ORDERS = 250
NUM_PRODUCTION_EVENTS = 400
NUM_QUALITY_INSPECTIONS = 500  # Peut être > que production (multi-inspections)

# Répertoires
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SAP_DIR = DATA_DIR / "sap"
PLM_DIR = DATA_DIR / "plm"
PRODUCTION_DIR = DATA_DIR / "production"
QUALITY_DIR = DATA_DIR / "quality"

# Créer les répertoires s'ils n'existent pas
for d in [SAP_DIR, PLM_DIR, PRODUCTION_DIR, QUALITY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Fichiers de sortie
SUPPLIERS_FILE = SAP_DIR / "suppliers.csv"
MATERIALS_FILE = SAP_DIR / "materials.csv"
PRODUCTS_FILE = PLM_DIR / "products.csv"
BOM_FILE = PLM_DIR / "bom.csv"
INVENTORY_FILE = SAP_DIR / "inventory.csv"
ORDERS_FILE = SAP_DIR / "orders.csv"
PRODUCTION_FILE = PRODUCTION_DIR / "production_events.csv"
QUALITY_FILE = QUALITY_DIR / "quality_inspections.csv"

# Seed pour la reproductibilité
RANDOM_SEED = 42

# Machines de production
PRODUCTION_MACHINES = [
    "ASM-LINE-01",      # Assemblage ligne 1
    "ASM-LINE-02",      # Assemblage ligne 2
    "ASM-LINE-03",      # Assemblage ligne 3
    "PACK-UNIT-01",     # Unité d'empaquetage
    "TEST-BENCH-01",    # Banc de test
]

# Statuts de production (distribution: 70% PASSED, 15% FAILED, 15% REWORK)
PRODUCTION_STATUS = ["PASSED", "FAILED", "REWORK"]
PRODUCTION_STATUS_WEIGHTS = [70, 15, 15]

# Défauts qualité possibles (cohérents avec statuts production)
QUALITY_DEFECTS = {
    "NO_DEFECT": ["PASSED"],  # Seulement pour productions PASSED
    "SURFACE_SCRATCH": ["FAILED", "REWORK"],
    "ASSEMBLY_ERROR": ["FAILED", "REWORK"],
    "MISSING_COMPONENT": ["FAILED"],
    "DIMENSION_OUT_OF_SPEC": ["FAILED", "REWORK"],
    "ELECTRICAL_FAILURE": ["FAILED"],
    "MEMORY_DETECTED_ERROR": ["FAILED", "REWORK"],
    "POWER_SUPPLY_FAILURE": ["FAILED"],
}

# Tests de qualité possibles
QUALITY_TESTS = ["VISUAL", "DIMENSIONAL", "ELECTRICAL", "FUNCTIONAL"]

# Familles de produits réalistes (hardware/serveurs industriels)
PRODUCT_FAMILIES = {
    "HPC-CLUSTER": {
        "name": "High Performance Computing Cluster",
        "price": 50000,
        "weight": 80,
        "components": ["CPU", "MEMORY", "STORAGE", "PSU", "FAN"]
    },
    "SERVER-RACK": {
        "name": "Server Rack Unit",
        "price": 30000,
        "weight": 60,
        "components": ["CPU", "MEMORY", "STORAGE", "PSU", "NETWORK"]
    },
    "STORAGE-UNIT": {
        "name": "Storage Array",
        "price": 25000,
        "weight": 50,
        "components": ["STORAGE", "CONTROLLER", "PSU", "FAN"]
    },
    "NETWORK-SWITCH": {
        "name": "Network Switch Unit",
        "price": 15000,
        "weight": 20,
        "components": ["PROCESSOR", "MEMORY", "NETWORK", "PSU"]
    },
    "WORKSTATION": {
        "name": "Industrial Workstation",
        "price": 12000,
        "weight": 30,
        "components": ["CPU", "MEMORY", "STORAGE", "GPU", "PSU"]
    },
}

# Matériaux disponibles (mapping par catégorie)
MATERIALS_BY_CATEGORY = {
    "CPU": [
        "CPU-X86-64-I9",
        "CPU-X86-64-I7",
        "CPU-ARM-64",
        "CPU-INTEL-XEON",
    ],
    "MEMORY": [
        "MEMORY-DDR5-64GB",
        "MEMORY-DDR5-32GB",
        "MEMORY-DDR4-16GB",
        "MEMORY-DDR4-8GB",
    ],
    "STORAGE": [
        "SSD-NVME-3.84TB",
        "SSD-NVME-1.92TB",
        "SSD-SATA-2TB",
        "HDD-SAS-8TB",
        "HDD-SAS-4TB",
    ],
    "PSU": [
        "PSU-1600W",
        "PSU-1200W",
        "PSU-750W",
        "PSU-500W",
    ],
    "FAN": [
        "FAN-120MM-PWM",
        "FAN-140MM-PWM",
        "FAN-200MM-PWM",
    ],
    "GPU": [
        "GPU-NVIDIA-A100",
        "GPU-NVIDIA-V100",
    ],
    "NETWORK": [
        "NIC-10GBE-DUAL",
        "NIC-10GBE-SINGLE",
    ],
    "CONTROLLER": [
        "CTRL-STORAGE-RAID",
        "CTRL-STORAGE-SAS",
    ],
    "PROCESSOR": [
        "PROC-ARM-CORTEX",
    ],
}

# Entrepôts disponibles
WAREHOUSES = ["WH-01", "WH-02", "WH-03"]

# Shifts de production
SHIFTS = ["MORNING", "AFTERNOON", "NIGHT"]
