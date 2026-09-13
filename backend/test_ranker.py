"""
Script de prueba aislado para ai_ranker.py

Por que ofertas inventadas en vez de traerlas de Arbeitnow?
Porque queremos probar SOLO la logica de ranking, sin depender de que
una API externa este disponible en este momento. Esto es una tecnica
real de testing: usar datos de ejemplo ("fixtures") para aislar la
pieza que estas probando de todo lo demas.

Como correrlo:
    cd backend
    python test_ranker.py
"""

import asyncio

from app.models.schemas import JobOffer, ParsedQuery
from app.services.ai_ranker import rank_and_summarize

FAKE_OFFERS = [
    JobOffer(
        title="Disenador Grafico Junior",
        company="Estudio Creativo LatAm",
        location="Remoto",
        source="Ejemplo",
        url="https://ejemplo.com/1",
        description="Buscamos disenador junior con 1 ano de experiencia en Figma "
        "y Adobe Illustrator. Salario: 1600 USD mensual. Modalidad remota.",
    ),
    JobOffer(
        title="Desarrollador Backend Senior",
        company="Tech Corp",
        location="Bogota, Colombia (presencial)",
        source="Ejemplo",
        url="https://ejemplo.com/2",
        description="Se requiere desarrollador con 5+ anos de experiencia en Python "
        "y bases de datos. Trabajo presencial en oficina.",
    ),
    JobOffer(
        title="Disenador UX/UI Semi-Senior",
        company="Startup Remota SAS",
        location="Remoto",
        source="Ejemplo",
        url="https://ejemplo.com/3",
        description="2-3 anos de experiencia en diseno de producto. Rango salarial "
        "1800-2200 USD. Equipo 100% remoto en Latam.",
    ),
]

FAKE_PROFILE = ParsedQuery(
    role="diseno grafico",
    modality="remoto",
    region="Latam",
    seniority="junior",
    salary_min=1500,
    salary_currency="USD",
)


async def main():
    print("Perfil buscado:")
    print(FAKE_PROFILE.model_dump_json(indent=2))
    print(f"\nEvaluando {len(FAKE_OFFERS)} ofertas de ejemplo...\n")

    ranked = await rank_and_summarize(FAKE_OFFERS, FAKE_PROFILE)

    for offer in ranked:
        print(f"[{offer.relevance_score}] {offer.title} - {offer.company}")
        print(f"   Resumen IA: {offer.ai_summary}")
        print(f"   Salario: {offer.salary_range} (disclosed={offer.salary_disclosed})")
        print()


if __name__ == "__main__":
    asyncio.run(main())