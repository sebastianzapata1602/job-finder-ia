"""
Modelos de datos (schemas).

Que es Pydantic y por que lo usamos?
Es una libreria que valida datos automaticamente usando "type hints" de
Python. Si alguien intenta crear un JobOffer sin "title", Pydantic lanza
un error claro en vez de dejar que el bug aparezca despues, en una parte
random del codigo, cuando ya es mas dificil de rastrear.

Este archivo es el "contrato" del que hablamos antes de escribir codigo:
sin importar de que fuente venga una oferta (Adzuna, Arbeitnow, RemoteOK),
dentro de nuestra app SIEMPRE tiene esta misma forma. Eso permite que el
resto del sistema (el ranker de IA, el frontend) no necesite saber nada
sobre las diferencias entre fuentes externas.
"""

from typing import Optional
from pydantic import BaseModel


class JobOffer(BaseModel):
    """Una oferta de empleo ya normalizada, sin importar su fuente original."""

    title: str
    company: str
    location: Optional[str] = None
    posted_at: Optional[str] = None
    source: str
    url: str
    description: Optional[str] = None

    # Estos dos campos casi nunca vienen limpios desde la fuente externa.
    # Por eso son Optional: es honesto modelar que "no sabemos" en vez de
    # inventar un valor por defecto que despues se confunda con un dato real.
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    salary_disclosed: bool = False

    # Estos dos campos los llena la IA rankeadora, no la fuente externa.
    # Por eso empiezan en None: una oferta recien traida de Arbeitnow
    # todavia no ha pasado por el ranking.
    ai_summary: Optional[str] = None
    relevance_score: Optional[float] = None


class ParsedQuery(BaseModel):
    """
    Lo que la IA interprete extrae del texto libre del usuario.

    Todos los campos son Optional porque el usuario puede no mencionar
    todos -- si alguien escribe solo "diseno grafico", no sabemos su
    modalidad ni su salario esperado, y eso esta bien.
    """

    role: Optional[str] = None
    modality: Optional[str] = None  # remoto / presencial / hibrido
    region: Optional[str] = None
    seniority: Optional[str] = None
    experience_years: Optional[str] = None
    salary_min: Optional[float] = None
    salary_currency: Optional[str] = None


class SearchRequest(BaseModel):
    """Lo que el usuario envia desde el frontend."""

    query: str


class SearchResponse(BaseModel):
    """Lo que el backend responde al frontend."""

    parsed_params: ParsedQuery
    results: list[JobOffer]
    total_found: int