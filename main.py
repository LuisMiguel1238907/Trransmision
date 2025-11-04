from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from database import engine
from models import Base

# ✅ Importar Routers
from routers.auth_routes import router as auth_router
from routers import clients, loans, payments, dashboard_routes
# from routers import reports  # <-- Si tienes reports, descomenta

# ✅ Crear la app
app = FastAPI(
    title="API de Clientes",
    version="1.0"
)

# ✅ Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Crear tablas
Base.metadata.create_all(bind=engine)

# ✅ Swagger + JWT
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API de Clientes",
        version="1.0.0",
        description="API con autenticación JWT",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ✅ REGISTRO DE RUTAS
app.include_router(auth_router)
app.include_router(clients.router)
app.include_router(loans.router)
app.include_router(payments.router)
app.include_router(dashboard_routes.router)

# ✅ Si tienes reports, solo así:
# app.include_router(reports.router)

# ✅ Ruta principal
@app.get("/")
def inicio():
    return {"mensaje": "API funcionando ✅"}
