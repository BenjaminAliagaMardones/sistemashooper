# Guía de Despliegue en Render (SaaS Shopper Management)

El proyecto está diseñado con **Clean Architecture** y separado en dos partes claras: Backend (FastAPI) y Frontend (React SPA). A continuación, se detallan los pasos para ponerlo en producción en [Render.com](https://render.com).

## 1. Base de Datos (PostgreSQL)
1. En el Dashboard de Render, haz clic en **New +** y selecciona **PostgreSQL**.
2. Dale un nombre (ej. `shopper-db`).
3. Selecciona la región más cercana a tus usuarios.
4. Elige el plan (Free o Starter).
5. Haz clic en **Create Database**.
6. Una vez creada, copia el valor de **Internal Database URL** (o External si usas otra plataforma).

## 2. Backend (FastAPI Web Service)
El backend utiliza Docker para instalar dependencias complejas del sistema requeridas por WeasyPrint (generador de PDF).

1. En Render, haz clic en **New +** y selecciona **Web Service**.
2. Conecta tu repositorio de GitHub.
3. Configura el servicio:
   - **Name**: `shopper-backend`
   - **Root Directory**: `backend` (Muy importante)
   - **Environment**: `Docker`
4. Variables de Entorno (Environment Variables):
   - `DATABASE_URL`: Pega la URL obtenida en el paso 1 (Si es en Render usa la Internal, si empieza con `postgres://` cámbiala a `postgresql://`).
   - `SECRET_KEY`: Una cadena de texto larga y aleatoria (ej. `openssl rand -hex 32`).
   - `CORS_ORIGINS`: La URL que tendrá tu frontend en Render (ej. `https://shopper-front.onrender.com`).
5. Haz clic en **Create Web Service**. 
6. *Nota: El Dockerfile ejecuta automáticamente `alembic upgrade head` para crear las tablas en la BD antes de iniciar el servidor.*

## 3. Frontend (React Static Site)
1. En Render, haz clic en **New +** y selecciona **Static Site**.
2. Conecta el mismo repositorio de GitHub.
3. Configura el servicio:
   - **Name**: `shopper-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Variables de Entorno (Environment Variables):
   - `VITE_API_URL`: Pega la URL del backend creado en el Paso 2 añadiendo `/api/v1` al final. (Ej: `https://shopper-backend.onrender.com/api/v1`).
5. **Regla Crítica para SPA (React Router):**
   - Ve a la pestaña **Redirects/Rewrites**.
   - Añade una regla:
     - **Source**: `/*`
     - **Destination**: `/index.html`
     - **Action**: `Rewrite`
   - Esto evita errores 404 al recargar páginas directamente (ej. `/orders`).
6. Haz clic en **Create Static Site**.

## ¡Listo! 🎉
Tu SaaS estará corriendo y conectándose de forma segura. El backend maneja su propia base de datos, y el frontend es servido a gran velocidad por el CDN global estático de Render.
