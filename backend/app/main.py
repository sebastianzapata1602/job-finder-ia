"""
Punto de entrada de la aplicacion.

Este archivo es intencionalmente pequeno. Su unico trabajo es:
1. Crear la app de FastAPI.
2. Registrar las rutas.
3. Configurar CORS (para que el frontend en otro puerto pueda hablarle).

Toda la logica real vive en services/ y routes/ -- main.py NUNCA deberia
crecer mucho. Si ves un main.py de 500 lineas en un proyecto real, es
una senal de alerta (a esto se le llama "God object" / archivo que hace
demasiado).
"""

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import JobOffer, SearchResponse
from app.services.job_sources.arbeitnow import search_arbeitnow

app = FastAPI(title="Job Finder AI")

# CORS: por defecto, un navegador bloquea que tu frontend (ej. localhost:5173)
# llame a tu backend (localhost:8000) por seguridad, ya que son "origenes"
# distintos. Esto le dice al navegador: "confia en peticiones desde estos
# origenes". En produccion, aqui pondrias tu dominio real, no "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    """
    Endpoint de salud. Sirve para confirmar que el servidor esta vivo,
    sin depender de logica de negocio. Es lo primero que pruebas siempre
    al levantar un servicio nuevo.
    """
    return {"status": "ok", "service": "job-finder-ai"}


@app.get("/api/search-test", response_model=SearchResponse)
async def search_test(q: str = "developer"):
    """
    Endpoint temporal de la Fase 1: sin IA todavia.
    Solo prueba que el conector de Arbeitnow funciona de punta a punta.

    Se reemplazara pronto por /api/search, que agregara interpretacion
    y ranking con IA. Por ahora, "q" es una palabra clave simple.

    Por que el try/except? Porque una API externa (Arbeitnow, Adzuna, etc.)
    puede fallar por razones que no controlas: esta caida, cambio su
    formato, tardo demasiado. Un backend profesional NUNCA deja que ese
    error crudo (con traceback y todo) llegue al usuario final -- eso es
    un riesgo de seguridad (revela detalles internos) y una mala
    experiencia. En vez de eso, lo atrapamos y devolvemos un error
    entendible con el codigo HTTP correcto.
    """
    try:
        offers: list[JobOffer] = await search_arbeitnow(q)
    except httpx.HTTPStatusError as exc:
        # La fuente externa respondio, pero con un error (403, 500, etc.)
        raise HTTPException(
            status_code=502,  # 502 = "Bad Gateway": el problema es de un servicio externo, no del tuyo
            detail=f"La fuente de empleos no respondio correctamente: {exc.response.status_code}",
        )
    except httpx.RequestError:
        # No se pudo ni siquiera conectar (sin internet, DNS, timeout, etc.)
        raise HTTPException(
            status_code=503,  # 503 = "Service Unavailable"
            detail="No se pudo conectar con la fuente de empleos. Intenta de nuevo.",
        )

    return SearchResponse(results=offers, total_found=len(offers))
