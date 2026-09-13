"""
Script de diagnostico: que esta devolviendo realmente Arbeitnow ahora mismo?

Este script NO usa nuestro filtro de busqueda -- trae los datos crudos
directo de la API externa, para que veamos con nuestros propios ojos
cuantas ofertas hay disponibles y como se ven sus titulos. Esto nos dice
si el problema es "no hay ofertas de ese rol en este momento" (limitacion
real de la fuente) o "algo esta roto en como leemos la respuesta" (bug).

Como correrlo:
    cd backend
    python debug_arbeitnow.py
"""

import httpx

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


def main():
    response = httpx.get(ARBEITNOW_URL, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    jobs = data.get("data", [])
    print(f"Total de ofertas recibidas en esta pagina: {len(jobs)}\n")

    print("Primeros 15 titulos disponibles ahora mismo:")
    for job in jobs[:15]:
        print(f"  - {job.get('title')}")

    print("\nBuscando cuantas contienen 'python' (sin distinguir mayusculas):")
    python_matches = [j for j in jobs if "python" in j.get("title", "").lower()]
    print(f"  Coincidencias: {len(python_matches)}")
    for j in python_matches:
        print(f"  - {j.get('title')}")


if __name__ == "__main__":
    main()