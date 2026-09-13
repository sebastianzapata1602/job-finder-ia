"""
Configuracion centralizada de la app.

Por que un archivo separado para esto?
Porque en vez de escribir os.environ["ALGO"] regado por todo el codigo
(propenso a errores de tipeo y sin validacion), definimos UNA sola fuente
de verdad. Si falta una variable de entorno, la app falla al arrancar
con un mensaje claro, en vez de fallar a mitad de una peticion de un usuario.

pydantic-settings valida los tipos automaticamente: si ANTHROPIC_API_KEY
no existe, Python te avisa apenas inicias el servidor, no cuando ya
tienes usuarios usando la app.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Se crea UNA sola instancia y se reutiliza en toda la app (patron singleton).
# Esto evita releer el archivo .env cada vez que se necesita una variable.
settings = Settings()
