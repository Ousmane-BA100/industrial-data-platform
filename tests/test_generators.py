"""
Tests pytest pour les générateurs de données
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "generate_data"))

from scripts.generate_data.generate_suppliers import generate_suppliers
from scripts.generate_data.generate_materials import generate_materials
from scripts.generate_data.generate_products import generate_products


def test_generate_suppliers():
    """Test la génération de fournisseurs"""
    suppliers = generate_suppliers()
    assert len(suppliers) > 0
    assert "supplier_id" in suppliers[0]
    assert "name" in suppliers[0]


def test_generate_products():
    """Test la génération de produits"""
    products = generate_products()
    assert len(products) > 0
    assert "product_id" in products[0]
    assert "name" in products[0]
