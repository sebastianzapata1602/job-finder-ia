"""
Rankeador y resumidor de ofertas con IA -- version Gemini (gratis).

Misma logica que la version con Claude: le enviamos TODAS las ofertas
de una vez (para que la IA pueda compararlas entre si), y pedimos un
arreglo JSON con la evaluacion de cada una, referenciada por su
"index" en la lista original (mas barato y confiable que repetir el
titulo completo).

Igual que en el interprete, usamos response_mime_type="application/json"
para que Gemini garantice una salida parseable.
"""

import json

from google import genai
from google.genai import types

from app.config import settings
from app.models.schemas import JobOffer, ParsedQuery

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """Eres un asistente que evalua ofertas de empleo contra el perfil de \
busqueda de un usuario. Para cada oferta debes devolver:

{
  "index": number,               # la posicion de la oferta en la lista recibida, empezando en 0
  "relevance_score": number,     # de 0.0 a 1.0, que tan bien calza con el perfil buscado
  "ai_summary": string,          # resumen de 1-2 frases, en espanol, de por que calza (o no)
  "salary_range": string o null, # solo si logras inferirlo del texto de la descripcion
  "experience_required": string o null  # solo si logras inferirlo del texto de la descripcion
}

Responde UNICAMENTE con un arreglo JSON de estos objetos, uno por cada \
oferta recibida, sin texto adicional ni marcadores de markdown.
"""


def _build_user_message(offers: list[JobOffer], parsed_params: ParsedQuery) -> str:
    """
    Arma el mensaje que se le envia a la IA: el perfil buscado, y cada
    oferta numerada con su informacion relevante (recortando la
    descripcion para no gastar tokens de mas en texto que no aporta).
    """
    offers_text = "\n\n".join(
        f"[{i}] Titulo: {o.title}\n"
        f"Empresa: {o.company}\n"
        f"Ubicacion: {o.location}\n"
        f"Descripcion: {(o.description or '')[:500]}"
        for i, o in enumerate(offers)
    )
    return (
        f"Perfil buscado: {parsed_params.model_dump_json()}\n\n"
        f"Ofertas a evaluar:\n\n{offers_text}"
    )


async def rank_and_summarize(
    offers: list[JobOffer], parsed_params: ParsedQuery
) -> list[JobOffer]:
    """
    Devuelve las mismas ofertas, enriquecidas con ai_summary y
    relevance_score, ordenadas de mayor a menor relevancia.

    Si algo falla, devolvemos las ofertas SIN enriquecer en vez de
    romper la busqueda completa -- el usuario prefiere ver resultados
    sin resumen que no ver nada.
    """
    if not offers:
        return offers

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=_build_user_message(offers, parsed_params),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=2000,
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.removeprefix("json").strip()

        evaluations = json.loads(raw_text)

        for evaluation in evaluations:
            i = evaluation.get("index")
            if i is None or not (0 <= i < len(offers)):
                continue
            offers[i].relevance_score = evaluation.get("relevance_score")
            offers[i].ai_summary = evaluation.get("ai_summary")
            if not offers[i].salary_range and evaluation.get("salary_range"):
                offers[i].salary_range = evaluation["salary_range"]
                offers[i].salary_disclosed = True
            if not offers[i].experience_required and evaluation.get("experience_required"):
                offers[i].experience_required = evaluation["experience_required"]

        offers.sort(key=lambda o: o.relevance_score or 0, reverse=True)
        return offers

    except Exception:
        return offers