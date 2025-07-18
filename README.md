# Request Catcher

## ¿Qué es?

Request Catcher es una herramienta moderna para capturar, visualizar y simular respuestas HTTP. Permite a desarrolladores y testers inspeccionar fácilmente las solicitudes que envían sus aplicaciones, configurar respuestas personalizadas y depurar integraciones web de forma sencilla.

Inspirado en herramientas como ngrok o webhook.site, este proyecto incluye:
- **Backend**: API en FastAPI (Python) con SQLite y SQLAlchemy para almacenar logs y configuraciones.
- **Frontend**: Interfaz web en React (Vite + Material UI) para visualizar y gestionar solicitudes y respuestas.

---

## Novedades: Autenticación y Panel de Admin

- **Autenticación JWT**: El backend ahora utiliza autenticación basada en tokens JWT para proteger las rutas de administración (configuración de respuestas, creación de usuarios, etc.).
- **Página de Login dedicada**: El frontend muestra una página de login moderna y responsiva para acceder a las funciones de administración.
- **Logout**: Puedes cerrar sesión desde el panel superior derecho.
- **Dependencias nuevas**: Asegúrate de tener `PyJWT` y `python-multipart` en tu `requirements.txt`.

### Flujo de autenticación

1. Accede a la página de configuración ("Configurations") en la UI.
2. Si no has iniciado sesión, verás la página de login.
3. Ingresa tus credenciales de admin. Si son correctas, recibirás un token JWT y podrás acceder a las funciones protegidas.
4. El token se almacena localmente y se envía automáticamente en las peticiones protegidas.
5. Puedes cerrar sesión con el botón "Logout".

---

## ¿Cómo funciona?

1. **Captura de solicitudes**: El backend expone un endpoint catch-all que registra cualquier solicitud HTTP recibida (método, ruta, headers, body, timestamp, etc.).
2. **Configuración de respuestas**: Puedes definir respuestas personalizadas por método y ruta (status, headers, body, delay) desde la UI. El backend responde según esa configuración.
3. **Visualización**: El frontend muestra una lista de solicitudes en tiempo real, con detalles completos de cada request y response, incluyendo tiempos y headers.
4. **Persistencia**: Todas las configuraciones y logs se guardan en SQLite.

---

## Proceso de uso

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd request-catcher
```

### 2. Levantar el entorno de desarrollo

Usa Docker Compose para iniciar tanto el backend como el frontend en modo desarrollo (hot reload):

```bash
docker-compose up --build
```

- El **backend** estará en: `http://localhost:8086`
- El **frontend** estará en: `http://localhost:5173`

### 3. Probar la captura de requests

Envía cualquier request HTTP al backend, por ejemplo:

```bash
curl -X POST http://localhost:8086/mi/prueba -d '{"foo": "bar"}' -H 'Content-Type: application/json'
```

Verás la solicitud reflejada en la UI del frontend.

### 4. Configurar respuestas personalizadas (requiere login)

Desde la UI, accede a "Configurations". Si no has iniciado sesión, se mostrará la página de login. Tras autenticarte:
- Agrega una nueva configuración para una ruta y método.
- Define código de estado, headers, body y delay.
- Las siguientes solicitudes a esa ruta/método recibirán la respuesta configurada.

### 5. Visualizar y filtrar

- Usa la barra lateral para ver todas las solicitudes capturadas.
- Filtra por método, ruta o body.
- Haz clic en una solicitud para ver todos los detalles (request y response).

---

## ¿Para qué sirve?

- Simular APIs durante el desarrollo frontend.
- Depurar webhooks y callbacks de servicios externos.
- Probar integraciones sin depender de un backend real.
- Analizar y guardar tráfico HTTP para debugging.

---

## Tecnologías principales

- **Backend**: FastAPI, SQLAlchemy, SQLite, Uvicorn, PyJWT, python-multipart
- **Frontend**: React, Vite, Material UI
- **DevOps**: Docker, Docker Compose

---

## Notas

- El proyecto está pensado para desarrollo local y pruebas.
- Puedes borrar la base de datos SQLite (`request-catcher/request-catcher/app/app.db`) si cambias el modelo.
- No incluye WebSockets ni exportación/importación avanzada (pero es extensible).
- **IMPORTANTE:** Para que la autenticación funcione, asegúrate de tener en `request-catcher/requirements.txt`:
  - `PyJWT`
  - `python-multipart`

---

¡Contribuciones y sugerencias son bienvenidas! 