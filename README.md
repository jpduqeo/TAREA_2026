# GameStore AI — Tienda de Videojuegos con Asistente Inteligente

API REST para una tienda de videojuegos con **GameBot**, un asistente de IA conversacional experto en videojuegos, potenciado por **Google Gemini AI** y construida con **Clean Architecture**.

---

## Autor

**Juan Pablo Duque Osorio**  
Universidad EAFIT  
Taller: Construcción de E-commerce con Chat IA

---

## Características

- **Catálogo de Videojuegos** — Gestión completa con filtros por género y plataforma
- **Compra de Juegos** — Endpoint de compra que reduce el stock automáticamente
- **Chat con GameBot** — Asistente IA con memoria conversacional usando Google Gemini
- **Clean Architecture** — 3 capas bien separadas (Domain, Application, Infrastructure)
- **Documentación Automática** — Swagger UI en `/docs`
- **Docker** — Containerización lista para usar
- **Base de Datos** — SQLite con 10 videojuegos precargados

---

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| FastAPI | 0.104.1 | Framework web REST |
| SQLAlchemy | 2.0.23 | ORM y base de datos |
| SQLite | — | Base de datos |
| Google Gemini | 0.3.2 | IA conversacional |
| Pydantic | 2.5.0 | Validación de datos |
| Docker | — | Containerización |
| Pytest | 7.4.3 | Tests unitarios |

---

## Arquitectura

El proyecto sigue los principios de **Clean Architecture**, separando las responsabilidades en tres capas:

```
INFRASTRUCTURE LAYER
  main.py (FastAPI)
  repositorio_videojuegos.py / repositorio_chat.py
  gemini_service.py (Google Gemini AI)
        |
        v  Inyección de Dependencias
APPLICATION LAYER
  servicio_videojuegos.py
  servicio_chat.py
  dtos.py
        |
        v  Entidades del Dominio
DOMAIN LAYER (Lógica de Negocio Pura)
  entidades.py (Videojuego, MensajeChat, ContextoChat)
  repositorios.py (IRepositorioVideojuegos, IRepositorioChat)
  excepciones.py
```

---

## Estructura del Proyecto

```
gamestore-ai/
├── src/
│   ├── config.py
│   ├── domain/
│   │   ├── entidades.py            # Videojuego, MensajeChat, ContextoChat
│   │   ├── repositorios.py         # IRepositorioVideojuegos, IRepositorioChat
│   │   └── excepciones.py          # VideojuegoNoEncontrado, StockInsuficiente...
│   ├── application/
│   │   ├── dtos.py                 # VideojuegoDTO, SolicitudChatDTO, VentaDTO...
│   │   ├── servicio_videojuegos.py
│   │   └── servicio_chat.py
│   └── infrastructure/
│       ├── api/main.py             # Endpoints FastAPI
│       ├── db/
│       │   ├── base_datos.py       # Configuración SQLAlchemy
│       │   ├── modelos.py          # Modelos ORM
│       │   └── datos_iniciales.py  # Seed de 10 videojuegos
│       ├── repositories/
│       │   ├── repositorio_videojuegos.py
│       │   └── repositorio_chat.py
│       └── llm_providers/
│           └── gemini_service.py
├── tests/
│   ├── conftest.py
│   ├── test_entidades.py
│   └── test_servicios.py
├── evidencias/
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Instalación y Uso

### Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- API Key de Google Gemini — gratis en https://aistudio.google.com/app/apikey

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/gamestore-ai.git
cd gamestore-ai
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y agregar tu API Key:

```env
GEMINI_API_KEY=AIzaSy...tu_key_real...
DATABASE_URL=sqlite:///./data/gamestore.db
ENVIRONMENT=development
```

### 3. Ejecutar con Docker (recomendado)

```bash
docker-compose up --build
```

Una vez levantado:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### 4. Ejecutar sin Docker

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
uvicorn src.infrastructure.api.main:app --reload
```

---

## Endpoints

### Videojuegos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/games` | Catálogo completo |
| GET | `/games?genero=RPG` | Filtrar por género |
| GET | `/games?plataforma=PS5` | Filtrar por plataforma |
| GET | `/games/disponibles` | Solo juegos con stock |
| GET | `/games/{id}` | Detalle de un juego |
| POST | `/games/{id}/comprar` | Comprar (reduce stock) |

### Chat con GameBot

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/chat` | Enviar mensaje a GameBot |
| GET | `/chat/historial/{sesion_id}` | Ver historial de conversación |
| DELETE | `/chat/historial/{sesion_id}` | Limpiar historial |

### General

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Info de la API |
| GET | `/health` | Estado del servicio |

---

## Ejemplos de Uso

### Listar catálogo

```bash
curl http://localhost:8000/games
curl http://localhost:8000/games?genero=RPG
curl http://localhost:8000/games?plataforma=PS5
```

### Comprar un videojuego

```bash
curl -X POST http://localhost:8000/games/1/comprar \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 1}'
```

Respuesta:

```json
{
  "juego_id": 1,
  "titulo": "Elden Ring",
  "cantidad_vendida": 1,
  "stock_restante": 14,
  "mensaje": "Compra exitosa. Se vendieron 1 unidad(es) de 'Elden Ring'. Stock restante: 14."
}
```

### Chatear con GameBot

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"sesion_id": "jugador_001", "mensaje": "Busco juegos de RPG para PC"}'
```

### Ver historial de conversación

```bash
curl http://localhost:8000/chat/historial/jugador_001
```

---

## Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=term-missing

# Tests específicos
pytest tests/test_entidades.py -v
pytest tests/test_servicios.py -v
```

---

## Comandos Docker

```bash
docker-compose up --build    # Construir y levantar
docker-compose up -d         # En segundo plano (detached)
docker-compose logs -f       # Ver logs en tiempo real
docker-compose down          # Detener y eliminar contenedores
docker-compose down -v       # Detener y eliminar volúmenes
```

---

## Catálogo Inicial

La base de datos se inicializa automáticamente con 10 videojuegos:

| Título | Desarrollador | Género | Plataforma | Precio |
|---|---|---|---|---|
| Elden Ring | FromSoftware | RPG | PC | $59.99 |
| God of War Ragnarök | Santa Monica Studio | Acción | PS5 | $69.99 |
| Zelda: Tears of the Kingdom | Nintendo | Aventura | Switch | $59.99 |
| Cyberpunk 2077: Phantom Liberty | CD Projekt Red | RPG | PC | $29.99 |
| FIFA 24 | EA Sports | Deportes | Xbox | $49.99 |
| Hollow Knight: Silksong | Team Cherry | Plataformas | PC | $19.99 |
| Spider-Man 2 | Insomniac Games | Acción | PS5 | $69.99 |
| Baldur's Gate 3 | Larian Studios | RPG | PC | $59.99 |
| Forza Horizon 5 | Playground Games | Carreras | Xbox | $39.99 |
| Hades II | Supergiant Games | Roguelike | PC | $24.99 |

## Nota:

En la imagen del POST desde postman, sale error 429 debido a que no pude pagar gemini, aun asi es completamente funcional con una clave de API con tokens.
