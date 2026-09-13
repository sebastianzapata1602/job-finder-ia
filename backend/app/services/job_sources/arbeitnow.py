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

import httpx

from app.models.schemas import JobOffer

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


async def search_arbeitnow(query: str) -> list[JobOffer]:
    """
    Busca ofertas en Arbeitnow que coincidan (de forma simple) con la query.

    Nota: la API de Arbeitnow no permite filtrar por texto en el request,
    asi que traemos la primera pagina de resultados y filtramos nosotros
    mismos por titulo. Esto es una limitacion real de trabajar con APIs
    externas gratuitas -- parte de aprender a integrar sistemas es
    aceptar estas limitaciones y disenar alrededor de ellas.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(ARBEITNOW_URL)
        response.raise_for_status()  # lanza una excepcion si el status no es 2xx
        data = response.json()

    query_lower = query.lower()
    offers: list[JobOffer] = []

    for job in data.get("data", []):
        title = job.get("title", "")
        if query_lower and query_lower not in title.lower():
            continue

        offers.append(
            JobOffer(
                title=title,
                company=job.get("company_name", "Empresa no especificada"),
                location=job.get("location") or "Remoto",
                posted_at=str(job.get("created_at", "")),
                source="Arbeitnow",
                url=job.get("url", ""),
                description=job.get("description", ""),
                salary_disclosed=False,  # Arbeitnow no expone salario estructurado
            )
        )

    return offers
