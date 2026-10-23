"""
app/client.py
Cliente de consulta educado contra sitio de práctica.
"""
import asyncio
import httpx
from app.extractor import extract_item

TARGET_URL = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
USER_AGENT = "PokemonStockMonitor/1.0 (laboratorio formativo; contact: german@homelab.local)"

async def main() -> None:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
        response = await client.get(TARGET_URL)
        if response.status_code == 200:
            obs = extract_item(response.text)
            print("--- Resultado de Extracción ---")
            print(f"Producto: {obs.title}")
            print(f"Estado:   {obs.status}")
            print(f"Precio:   {obs.price} £")
            print(f"Detalle:  {obs.detail}")
        else:
            print(f"Error HTTP {response.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
