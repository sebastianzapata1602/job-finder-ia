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


class SearchRequest(BaseModel):
    """Lo que el usuario envia desde el frontend."""

    query: str


class SearchResponse(BaseModel):
    """Lo que el backend responde al frontend."""

    results: list[JobOffer]
    total_found: int
