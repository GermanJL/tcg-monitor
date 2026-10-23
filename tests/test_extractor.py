"""
tests/test_extractor.py
Pruebas unitarias offline usando fixtures locales.
"""
from pathlib import Path
import pytest
from app.extractor import extract_item, parse_price

FIXTURES_DIR = Path(__file__).parent / "fixtures"

def load_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("£51.77", 51.77),
        ("54,99 €", 54.99),
        ("1.250,00 €", 1250.00),
        ("Agotado", None),
        ("", None),
    ],
)
def test_price_normalization(raw, expected):
    assert parse_price(raw) == expected

def test_extract_in_stock():
    html = load_fixture("book_in_stock.html")
    obs = extract_item(html)
    assert obs.title == "A Light in the Attic"
    assert obs.status == "in_stock"
    assert obs.price == 51.77

def test_extract_out_of_stock():
    html = load_fixture("book_out_of_stock.html")
    obs = extract_item(html)
    assert obs.title == "Tipping the Velvet"
    assert obs.status == "out_of_stock"
    assert obs.price == 53.74

def test_broken_dom_returns_unknown_never_out_of_stock():
    html = load_fixture("broken_page.html")
    obs = extract_item(html)
    assert obs.status == "unknown"
    assert "selector no encontrado" in obs.detail
