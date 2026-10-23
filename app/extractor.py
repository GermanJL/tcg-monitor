"""
app/extractor.py
Extracción de stock y precio desacoplada de la red.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Literal
from bs4 import BeautifulSoup

Status = Literal["in_stock", "out_of_stock", "unknown"]

@dataclass(frozen=True)
class ItemObservation:
    title: str | None
    status: Status
    price: float | None
    detail: str

def parse_price(text: str | None) -> float | None:
    """Extrae y normaliza formatos numéricos: '£51.77' -> 51.77 | '49,99 €' -> 49.99"""
    if not text:
        return None
    match = re.search(r"\d[\d.,]*", text)
    if not match:
        return None
    raw = match.group(0).rstrip(".,")
    if "," in raw and "." in raw:
        decimal = "," if raw.rfind(",") > raw.rfind(".") else "."
        thousands = "." if decimal == "," else ","
        raw = raw.replace(thousands, "").replace(decimal, ".")
    elif "," in raw:
        head, _, tail = raw.rpartition(",")
        raw = f"{head.replace(',', '')}.{tail}" if len(tail) <= 2 else raw.replace(",", "")
    elif raw.count(".") > 1:
        raw = raw.replace(".", "")
    try:
        return float(raw)
    except ValueError:
        return None

def extract_item(
    html: str,
    title_selector: str = "h1",
    price_selector: str = "p.price_color",
    stock_selector: str = "p.availability",
    in_stock_regex: str = r"in stock|disponible|en stock",
    out_of_stock_regex: str = r"out of stock|agotado|sin stock|no disponible",
) -> ItemObservation:
    """Parsea el HTML estático de una ficha."""
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Título
    title_el = soup.select_one(title_selector)
    title = title_el.get_text(strip=True) if title_el else None

    # 2. Precio
    price_el = soup.select_one(price_selector)
    price = parse_price(price_el.get_text(strip=True)) if price_el else None

    # 3. Disponibilidad
    stock_el = soup.select_one(stock_selector)
    if stock_el is None:
        return ItemObservation(
            title=title,
            status="unknown",
            price=price,
            detail=f"selector no encontrado ({stock_selector})",
        )

    text = " ".join(stock_el.get_text(" ", strip=True).split())

    # Agotado prevalece sobre en stock
    if re.search(out_of_stock_regex, text, re.IGNORECASE):
        return ItemObservation(title=title, status="out_of_stock", price=price, detail=text[:40])
    if re.search(in_stock_regex, text, re.IGNORECASE):
        return ItemObservation(title=title, status="in_stock", price=price, detail=text[:40])

    return ItemObservation(
        title=title,
        status="unknown",
        price=price,
        detail=f"texto no concluyente ({text[:40]})",
    )
