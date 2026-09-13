"""
Conector de Arbeitnow.

Por que empezar por aqui?
Arbeitnow tiene una API publica que NO requiere registro ni API key,
asi que es la forma mas rapida de probar que el flujo completo funciona,
antes de meternos en el papeleo de registrar cuentas en Adzuna, etc.

Patron importante: esta funcion SOLO sabe hablar con Arbeitnow y devolver
JobOffer. No sabe nada de IA, ni de ranking, ni de otras fuentes. Eso es
lo que en ingenieria se llama "single responsibility": si Arbeitnow
cambia su API manana, solo tocas este archivo, nada mas.
"""

import html
import re
from datetime import datetime, timezone

import httpx

from app.models.schemas import JobOffer

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _clean_description(raw_html: str) -> str:
    """
    Arbeitnow devuelve la descripcion como HTML crudo (a veces con
    entidades escapadas dos veces, como '&lt;p&gt;' en vez de '<p>').
    Esto la convierte en texto plano legible.

    Por que nos importa esto mas alla de que "se vea feo"? Porque esa
    descripcion se la enviamos directo a la IA rankeadora -- si esta
    llena de etiquetas HTML, le estamos gastando tokens (y por lo tanto
    parte del limite gratuito de Gemini) en basura que no aporta
    significado, en vez de en el texto real que la IA necesita leer.
    """
    if not raw_html:
        return ""
    # Arbeitnow a veces escapa el HTML dos veces (&lt;p&gt; en vez de <p>).
    # Des-escapamos dos veces para cubrir ambos casos sin romper texto normal.
    text = html.unescape(html.unescape(raw_html))
    text = _HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _format_posted_at(raw_value) -> str:
    """
    Arbeitnow devuelve 'created_at' como timestamp Unix (segundos desde
    1970), poco legible para un humano. Lo convertimos a fecha ISO.

    Si el valor no se puede convertir (formato inesperado, vacio, etc),
    devolvemos un string vacio en vez de romper toda la busqueda por un
    solo campo secundario -- el titulo y la empresa son la informacion
    critica, la fecha es un extra.
    """
    try:
        timestamp = int(raw_value)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return ""


async def search_arbeitnow(query: str) -> list[JobOffer]:
    """
    Busca ofertas en Arbeitnow que coincidan con la query.

    Nota: la API de Arbeitnow no permite filtrar por texto en el request,
    asi que traemos la primera pagina de resultados y filtramos nosotros
    mismos por titulo. Esto es una limitacion real de trabajar con APIs
    externas gratuitas -- parte de aprender a integrar sistemas es
    aceptar estas limitaciones y disenar alrededor de ellas.

    Decision de diseno importante (corregida): el filtro compara PALABRA
    POR PALABRA, no la frase completa. Si buscaramos el texto exacto
    "python developer", nunca coincidiria con un titulo real como
    "Senior Backend Engineer (Python)" -- los titulos de empleo casi
    nunca repiten la frase exacta que alguien escribiria en una busqueda.

    En vez de eso, aceptamos una oferta si CUALQUIERA de las palabras
    del rol aparece en el titulo. Esto trae mas resultados de los
    estrictamente necesarios (mayor cobertura), y es una decision
    deliberada: es el ranker de IA (rank_and_summarize) el que despues
    decide, con mas contexto, cuales de esos resultados son realmente
    relevantes. El buscador prioriza no perderse ofertas validas; el
    ranker prioriza precision.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(ARBEITNOW_URL)
        response.raise_for_status()  # lanza una excepcion si el status no es 2xx
        data = response.json()

    # Palabras muy genericas no ayudan a filtrar (aparecerian en casi
    # cualquier titulo o en ninguno) -- las ignoramos al buscar coincidencias.
    stopwords = {"remoto", "remote", "presencial", "hibrido", "junior",
                 "senior", "semi-senior", "de", "en", "el", "la", "y"}
    keywords = [w for w in query.lower().split() if w not in stopwords and len(w) > 1]

    offers: list[JobOffer] = []

    for job in data.get("data", []):
        title = job.get("title", "")
        title_lower = title.lower()

        # Si no logramos extraer ninguna palabra util del rol, no filtramos
        # (mejor mostrar de mas que no mostrar nada por un query vacio).
        if keywords and not any(kw in title_lower for kw in keywords):
            continue

        offers.append(
            JobOffer(
                title=title,
                company=job.get("company_name", "Empresa no especificada"),
                location=job.get("location") or "Remoto",
                posted_at=_format_posted_at(job.get("created_at")),
                source="Arbeitnow",
                url=job.get("url", ""),
                description=_clean_description(job.get("description", "")),
                salary_disclosed=False,  # Arbeitnow no expone salario estructurado
            )
        )

    return offers