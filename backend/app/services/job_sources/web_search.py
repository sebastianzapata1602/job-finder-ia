"""
Fuente de ofertas via busqueda web en vivo (Gemini + Google Search).

A diferencia de arbeitnow.py (que llama a una API de datos ya
estructurados), aqui NO existe una API que nos de "ofertas de empleo en
formato JSON de toda la web". En su lugar, usamos la funcion de Google
Search integrada en Gemini para que la IA busque en internet en el
momento, y despues convertimos lo que encontro a nuestro formato interno.

Por que dos llamadas a la IA en vez de una?
La API de Gemini no permite combinar "usar herramientas como Google
Search" con "forzar salida en JSON estricto" en la misma peticion -- son
mutuamente excluyentes por una limitacion actual de la API, no una
decision nuestra. Por eso dividimos el trabajo:

  1. _search_raw(): Gemini busca en Google y devuelve texto libre con
     lo que encontro (hallazgos + enlaces reales).
  2. _structure_results(): una SEGUNDA llamada, esta vez sin
     herramientas, que convierte ese texto libre a JSON valido.

Decision de diseno critica: le pedimos EXPLICITAMENTE a la IA que nunca
invente ofertas que no encontro en la busqueda real. Esto es importante
porque, a diferencia de Arbeitnow (datos verificados por una API), aqui
dependemos de que la IA sea honesta sobre lo que realmente encontro.
"""

import json

from google import genai
from google.genai import types

from app.config import settings
from app.models.schemas import JobOffer, ParsedQuery

client = genai.Client(api_key=settings.gemini_api_key)

SEARCH_SYSTEM_PROMPT = """Eres un asistente de busqueda de empleo. Usa Google Search para \
encontrar oportunidades REALES y ACTUALES (empleo fijo y tambien freelance/contratos) que \
coincidan con el perfil dado.

Reglas estrictas:
- SOLO reporta oportunidades que hayas encontrado de verdad en la busqueda. Nunca inventes \
una oferta, empresa o enlace que no provenga de un resultado real de busqueda.
- Si no encuentras nada relevante, dilo explicitamente en vez de forzar resultados.
- Para cada hallazgo, incluye: titulo del puesto, empresa o cliente, si es freelance o \
empleo fijo, el enlace real a la publicacion, y cualquier dato de salario o experiencia \
que hayas visto.
- Prioriza resultados de los ultimos dias/semanas sobre publicaciones antiguas.
"""

STRUCTURE_SYSTEM_PROMPT = """Convierte el siguiente texto (hallazgos de una busqueda de \
empleo) en un arreglo JSON. Cada elemento debe tener esta forma exacta:

{
  "title": string,
  "company": string,
  "url": string,
  "description": string,
  "is_freelance": boolean,
  "salary_range": string o null,
  "experience_required": string o null
}

Reglas estrictas:
- Un elemento por cada oportunidad distinta mencionada en el texto.
- Si el texto dice explicitamente que no encontro nada, responde con un arreglo vacio: []
- NUNCA agregues una oportunidad que no este mencionada en el texto de entrada.
- Responde UNICAMENTE con el arreglo JSON, sin texto adicional ni marcadores de markdown.
"""


def _search_raw(query: str, parsed_params: ParsedQuery) -> str:
    """
    Paso 1: le pide a Gemini que busque en Google Search en vivo.
    Devuelve texto libre (no JSON) con lo que haya encontrado.
    """
    user_message = (
        f"Perfil buscado: {parsed_params.model_dump_json()}\n"
        f"Busqueda original del usuario: {query}"
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SEARCH_SYSTEM_PROMPT,
            temperature=0,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return response.text or ""


def _structure_results(raw_text: str) -> list[dict]:
    """
    Paso 2: convierte el texto libre del paso 1 en una lista de dicts,
    usando una llamada SIN herramientas (para poder forzar JSON).
    """
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=raw_text,
        config=types.GenerateContentConfig(
            system_instruction=STRUCTURE_SYSTEM_PROMPT,
            temperature=0,
            max_output_tokens=3000,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    raw_json = response.text.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.strip("`")
        raw_json = raw_json.removeprefix("json").strip()
    return json.loads(raw_json)


async def search_web(query: str, parsed_params: ParsedQuery) -> list[JobOffer]:
    """
    Punto de entrada de esta fuente: busca en la web en vivo, y devuelve
    una lista de JobOffer, igual que search_arbeitnow.

    Igual que en el resto del proyecto: si algo falla, devolvemos una
    lista vacia en vez de romper toda la busqueda. Esta fuente es un
    "extra" -- si falla, el usuario igual deberia ver los resultados de
    Arbeitnow.
    """
    try:
        raw_text = _search_raw(query, parsed_params)
        items = _structure_results(raw_text)
    except Exception:
        return []

    offers: list[JobOffer] = []
    for item in items:
        offers.append(
            JobOffer(
                title=item.get("title", "Sin titulo"),
                company=item.get("company", "No especificado"),
                location="Freelance" if item.get("is_freelance") else None,
                source="Busqueda web",
                url=item.get("url", ""),
                description=item.get("description", ""),
                experience_required=item.get("experience_required"),
                salary_range=item.get("salary_range"),
                salary_disclosed=bool(item.get("salary_range")),
            )
        )
    return offers