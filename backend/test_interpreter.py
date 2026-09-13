"""
Script de prueba aislado para ai_interpreter.py

Por que un script separado en vez de probar todo el servidor?
Porque queremos probar UNA sola pieza a la vez. Si algo falla aqui,
sabes con certeza que el problema esta en la logica de interpretacion,
no en FastAPI, ni en el conector de Arbeitnow, ni en nada mas. Esto se
llama "prueba unitaria" (aunque esta version es informal, sin un
framework de testing todavia) -- aislar la pieza que quieres validar.

Como correrlo:
    cd backend
    python test_interpreter.py "diseno grafico remoto en Latam, junior, salario minimo 1500 USD"
"""

import sys

from app.services.ai_interpreter import interpret_query

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "desarrollador python remoto senior"
    print(f"Consulta enviada: {query}\n")

    result = interpret_query(query)

    print("Resultado interpretado por la IA:")
    print(result.model_dump_json(indent=2))