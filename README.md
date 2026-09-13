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
- **IA:** API de Anthropic (Claude) para interpretacion de lenguaje natural y ranking
- **Fuentes de empleo:** Adzuna, Arbeitnow, RemoteOK
- **Base de datos:** SQLite
- **Frontend:** React + Vite (proximamente)

## Como correrlo localmente

### Requisitos
- Python 3.11+
- Una API key de [Anthropic](https://console.anthropic.com/)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # y completa tu ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Prueba en el navegador:
- `http://127.0.0.1:8000/` — health check
- `http://127.0.0.1:8000/api/search-test?q=developer` — busqueda de prueba (Arbeitnow, sin IA todavia)
- `http://127.0.0.1:8000/docs` — documentacion interactiva autogenerada por FastAPI

## Roadmap

- [x] Estructura base del backend
- [x] Conector a Arbeitnow (sin API key)
- [x] Manejo de errores para fallos de APIs externas
- [ ] Interpretacion de busqueda en lenguaje natural con IA
- [ ] Conectores a Adzuna y RemoteOK
- [ ] Ranking y resumen de ofertas con IA
- [ ] Extraccion de salario/experiencia desde texto no estructurado
- [ ] Frontend en React
- [ ] Cache local con SQLite

## Que estoy aprendiendo con este proyecto

- Diseno de arquitectura backend con separacion de responsabilidades
- Integracion de multiples APIs externas con manejo de errores real
- Prompt engineering aplicado (no solo "chatear" con un modelo, sino usarlo como pieza de un pipeline)
- Manejo seguro de credenciales (variables de entorno, `.gitignore`)
- Buenas practicas de documentacion de proyectos

## Licencia

Este proyecto usa la licencia MIT. Ver [LICENSE](LICENSE).
