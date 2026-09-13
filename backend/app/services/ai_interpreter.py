"""
Interprete de busquedas con IA -- version Gemini (gratis).

La logica es identica a la version con Claude: convertir lenguaje
natural en datos estructurados. Lo unico que cambia es el SDK y la
forma de llamar al modelo. Fijate que el "contrato" de esta funcion
(recibe un string, devuelve un ParsedQuery) no cambio -- por eso el
resto de la app (main.py) no necesita modificarse en absoluto.

Por que Gemini 3.6 Flash? Es el modelo actual con tier gratuito de Google
(rate-limited, pero sin costo ni tarjeta de credito), suficiente para un
proyecto de aprendizaje que estas probando tu mismo.

Usamos response_mime_type="application/json" en la configuracion --
esto le pide a Gemini que garantice una salida JSON valida, reduciendo
(aunque no eliminando del todo) el riesgo de que devuelva texto extra.
"""

import json

from google import genai
from google.genai import types

from app.config import settings
from app.models.schemas import ParsedQuery

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """Eres un extractor de datos. Tu unica tarea es convertir una busqueda de \
empleo en lenguaje natural a un objeto JSON con esta forma exacta:

{
  "role": string o null,
  "modality": "remoto" | "presencial" | "hibrido" | null,
  "region": string o null,
  "seniority": "junior" | "semi-senior" | "senior" | null,
  "experience_years": string o null,
  "salary_min": number o null,
  "salary_currency": string o null
}

Reglas estrictas:
- Responde UNICAMENTE con el JSON. Sin texto antes, sin texto despues, \
sin marcadores de codigo markdown.
- Si el usuario no menciona un campo, usa null. NUNCA inventes un valor \
para rellenar un campo que no fue mencionado.
- salary_min siempre en numero, sin simbolos de moneda ni comas.
"""


def interpret_query(query: str) -> ParsedQuery:
    """
    Envia la busqueda del usuario a Gemini y devuelve un ParsedQuery.

    Igual que en la version anterior: si algo falla, devolvemos un
    ParsedQuery de respaldo en vez de romper la busqueda completa.
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=800,
                response_mime_type="application/json",
                # Gemini 3 "piensa" antes de responder por defecto, y ese
                # razonamiento consume parte de max_output_tokens -- para
                # una tarea simple de extraccion no lo necesitamos, y sin
                # esto el JSON puede quedar cortado a la mitad.
                thinking_config=types.ThinkingConfig(thinking_level="minimal"),

            ),
        )
        raw_text = response.text.strip()

        # Salvaguarda por si acaso, aunque pedimos JSON explicito.
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.removeprefix("json").strip()

        data = json.loads(raw_text)
        return ParsedQuery(**data)

    except Exception as e:
        print(f"ERROR EN INTERPRETER: {e}")
        return ParsedQuery(role=query)