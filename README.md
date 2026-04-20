# Directorio Gaymers

App en Streamlit para registrar miembros de un grupo, guardar sus gustos, datos generales, foto e Instagram, y consultar cada perfil de forma individual.

## Que incluye

- Alta de nuevos miembros mediante formulario.
- Tabla general con filtros por texto, sistema de juego y perfiles con foto.
- Vista individual de perfil con foto, datos personales, gustos y contacto.
- Edicion y eliminacion de perfiles.
- Persistencia en `SQLite` para uso local.
- Compatibilidad con `PostgreSQL` usando `DATABASE_URL`, ideal para Streamlit Cloud.

## Archivos principales

- `streamlit_app.py`: interfaz principal de la app.
- `database.py`: modelo, inicializacion y operaciones CRUD.
- `requirements.txt`: dependencias para local y despliegue.

## Ejecutar en local

1. Crea y activa un entorno virtual.
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la app:

```bash
streamlit run streamlit_app.py
```

Si no configuras ninguna variable adicional, la app crea y usa una base local llamada `group_members.db`.

## Base de datos para Streamlit Cloud

Para que los datos no se pierdan en la nube, usa una base PostgreSQL externa, por ejemplo en Neon, Supabase o Railway.

En los secretos de Streamlit Cloud agrega algo como esto:

```toml
DATABASE_URL = "postgresql://usuario:password@host:5432/base_de_datos"
```

La app detecta automaticamente:

- `SQLite` si no existe `DATABASE_URL`
- `PostgreSQL` si `DATABASE_URL` esta configurada

No necesitas crear tablas manualmente; la app las genera al iniciar.

## Despliegue en Streamlit Cloud

1. Sube esta carpeta a GitHub.
2. En Streamlit Cloud crea una nueva app.
3. Selecciona el archivo principal `streamlit_app.py`.
4. En `App settings > Secrets`, agrega `DATABASE_URL`.
5. Despliega.

## Notas

- Las fotos se guardan dentro de la base de datos para no depender de archivos locales.
- Si el grupo crece mucho y suben fotos muy pesadas, conviene migrar las imagenes a un storage externo mas adelante.
