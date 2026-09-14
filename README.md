# Job Finder AI

> Buscador de empleo que usa IA para interpretar busquedas en lenguaje
> natural y rankear ofertas por relevancia real, combinando multiples
> fuentes de empleo en tiempo real.

**Estado:** en desarrollo activo (proyecto de aprendizaje)

## Sobre este proyecto

Este es mi primer proyecto a nivel profesional integrando IA en una
aplicacion real. Estudio administracion de sistemas y queria un proyecto
que me obligara a aprender arquitectura de backend, integracion de APIs
externas, y uso practico (no superficial) de modelos de lenguaje.

El objetivo funcional: escribes algo como *"diseno grafico remoto en
Latam, junior, salario minimo 1500 USD"* y la app entiende esa frase,
la traduce en parametros de busqueda, consulta varias fuentes de empleo,
y te devuelve las ofertas mas relevantes y recientes, ya resumidas.

## Como funciona

Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para el diagrama completo
y las decisiones de diseno.

## Stack tecnico

- **Backend:** Python, FastAPI, httpx
- **IA:** API de Google Gemini (tier gratuito) para interpretacion de lenguaje natural y ranking
- **Fuentes de empleo:** Arbeitnow (activo), Adzuna y RemoteOK (planeados)
- **Base de datos:** SQLite (planeado)
- **Frontend:** React + Vite (proximamente)

## Como correrlo localmente

### Requisitos
- Python 3.11+
- Una API key gratuita de [Google AI Studio](https://aistudio.google.com/apikey) (no requiere tarjeta de credito)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # y completa tu GEMINI_API_KEY
uvicorn app.main:app --reload
```

Prueba en el navegador:
- `http://127.0.0.1:8000/` — health check
- `http://127.0.0.1:8000/docs` — documentacion interactiva autogenerada por FastAPI, para probar los endpoints de abajo sin necesidad de Postman

Endpoints disponibles:
- `POST /api/search` — el endpoint real: recibe una busqueda en lenguaje natural (`{"query": "diseno grafico remoto junior"}`), la interpreta con IA, busca ofertas, y las devuelve rankeadas y resumidas
- `GET /api/search-test?q=developer` — endpoint simple sin IA, solo para probar el conector de Arbeitnow de forma aislada

## Roadmap

- [x] Estructura base del backend
- [x] Conector a Arbeitnow (sin API key)
- [x] Manejo de errores para fallos de APIs externas
- [x] Interpretacion de busqueda en lenguaje natural con IA (Gemini)
- [x] Ranking y resumen de ofertas con IA
- [x] Extraccion de experiencia/salario desde texto no estructurado
- [x] Limpieza de datos crudos de la fuente (HTML, fechas)
- [ ] Busqueda web en vivo como fuente adicional (mas alla de portales de empleo estructurados)
- [ ] Conectores a Adzuna y RemoteOK
- [ ] Frontend en React
- [ ] Cache local con SQLite

## Que estoy aprendiendo con este proyecto

- Diseno de arquitectura backend con separacion de responsabilidades
- Integracion de multiples APIs externas con manejo de errores real
- Prompt engineering aplicado (no solo "chatear" con un modelo, sino usarlo como pieza de un pipeline)
- Manejo seguro de credenciales (variables de entorno, `.gitignore`)
- Buenas practicas de documentacion de proyectos
- Depuracion de fallos silenciosos en integraciones con IA (excepciones atrapadas que ocultaban el error real, modelos descontinuados, tokens de "thinking" consumiendo el limite de salida)
- Diseno de filtros de busqueda: priorizar cobertura en la busqueda y dejar que la IA aporte precision despues, en vez de un filtro rigido que descarta resultados validos

## Licencia

Este proyecto usa la licencia MIT. Ver [LICENSE](LICENSE).
