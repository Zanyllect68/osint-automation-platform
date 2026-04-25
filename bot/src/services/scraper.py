import re
import httpx
from bs4 import BeautifulSoup
from services.database import save_texto


async def scrape_google(query: str, limit: int = 10) -> list:
    """Busca en Google y extrae resultados"""
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    url = f"https://www.google.com/search?q={query}&num={limit}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for div in soup.select("div.g"):
                title = div.select_one("h3")
                link = div.select_one("a")
                snippet = div.select_one("div.VwiC3b")
                
                if title and link:
                    href = link.get("href", "")
                    if href.startswith("/url?"):
                        continue
                    results.append({
                        "title": title.text,
                        "url": href,
                        "snippet": snippet.text if snippet else ""
                    })
    except Exception as e:
        return [{"error": str(e)}]
    
    return results


async def scrape_social(query: str) -> dict:
    """Busca en redes sociales comunes"""
    results = {"twitter": [], "linkedin": [], "facebook": [], "instagram": []}
    
    query_encoded = query.replace(" ", "%20")
    
    urls = [
        ("twitter", f"https://twitter.com/search?q={query_encoded}"),
        ("linkedin", f"https://www.linkedin.com/search/results/all/?keywords={query_encoded}"),
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        for platform, url in urls:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                results[platform] = {"status": response.status_code, "url": url}
            except Exception as e:
                results[platform] = {"error": str(e)}
    
    return results


def scrape_directorio_publico(url: str, tipo: str = "rnc") -> list:
    """ scrapea directorio público (RNC, etc.)"""
    results = []
    
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = httpx.get(url, headers=header, timeout=30.0)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all(["td", "th"])
                data = [col.text.strip() for col in cols]
                
                if tipo == "rnc" and len(data) >= 4:
                    results.append({
                        "nombre": data[0] if len(data) > 0 else "",
                        "documento": data[1] if len(data) > 1 else "",
                        "estado": data[2] if len(data) > 2 else "",
                    })
    except Exception as e:
        return [{"error": str(e)}]
    
    return results


def extract_emails(texto: str) -> list:
    """Extrae emails de un texto"""
    patron = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(patron, texto)


def extract_phones(texto: str) -> list:
    """Extrae teléfonos de un texto"""
    patron = r'\+?\d{1,3}[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}'
    return re.findall(patron, texto)


def extract_documents(texto: str) -> list:
    """Extrae números de documento de un texto"""
    results = []
    
    patrones = [
        r'\d{8,10}',
        r'[A-Z]{1,2}\d{6,10}',
    ]
    
    for patron in patrones:
        results.extend(re.findall(patron, texto))
    
    return list(set(results))


def extract_nombres(texto: str) -> list:
    """Extrae nombres propios del texto"""
    nombres = []
    palabras = texto.split()
    
    for palabra in palabras:
        palabra_limpia = palabra.strip(".,;:()")
        if palabra_limpia and palabra_limpia[0].isupper() and len(palabra_limpia) >= 3:
            if not palabra_limpia in ["Colombia", "Bogota", "Ciudad", "Fecha", "Documento", "Tipo", "Numero", "Direccion", "Telefono", "Email"]:
                nombres.append(palabra_limpia)
    
    return list(set(nombres))[:20]


async def scrape_person(query: str) -> dict:
    """Ejecuta scraping completo de una persona"""
    resultados = {
        "query": query,
        "google": [],
        "directorios": [],
        "emails": [],
        "telefonos": [],
        "documentos": []
    }
    
    resultados["google"] = await scrape_google(query)
    
    texto_combinado = ""
    for r in resultados["google"]:
        texto_combinado += r.get("snippet", "")
    
    resultados["emails"] = extract_emails(texto_combinado)
    resultados["telefonos"] = extract_phones(texto_combinado)
    resultados["documentos"] = extract_documents(texto_combinado)
    
    save_texto(0, f"Scraping: {query} - {resultados}")
    
    return resultados