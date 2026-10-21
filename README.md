# Network Route Optimization API

A production-grade REST API for modeling network graphs and finding optimal, lowest-latency routes using **Dijkstra's Algorithm**. 

Built with **Django 6**, **Django REST Framework**, and **Python 3.13**, managed with **[uv](https://docs.astral.sh/uv/)**, and strictly developed using **Test-Driven Development (TDD)** with **pytest** achieving **100% test coverage**.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.13 |
| **Framework** | Django 6 + Django REST Framework |
| **API Documentation** | OpenAPI 3.0 via `drf-spectacular` (Swagger & Redoc) |
| **Algorithm** | Dijkstra's Shortest Path (`heapq` Priority Queue) |
| **Environment & Package Manager** | `uv` |
| **Test Suite** | `pytest`, `pytest-django`, `pytest-cov` (**100% coverage**) |
| **Database** | SQLite (dev) |

---

## 🚀 Getting Started

### 1. Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git

### 2. Setup & Installation
```bash
git clone https://github.com/Assassin23/Network-Route-Optimization.git
cd Network-Route-Optimization

# Install dependencies into virtual environment
uv sync

# Apply database migrations
uv run python manage.py migrate
```

### 3. Run the Server
```bash
uv run python manage.py runserver
```
The API is available at `http://127.0.0.1:8000`.

---

## 📖 Interactive API Documentation

Once the server is running, explore and test the endpoints via interactive docs:
- **Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema (JSON/YAML):** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 📡 API Reference

### 1. Nodes
- **`POST /nodes`**: Add a node.
  - Body: `{"name": "ServerA"}`
  - Response (`201`): `{"id": 1, "name": "ServerA"}`
  - Errors: `400` on missing, empty, or duplicate name.
- **`GET /nodes`**: List all nodes.
  - Response (`200`): `[{"id": 1, "name": "ServerA"}]`
- **`DELETE /nodes/{id}`**: Delete a node.
  - Response (`204` No Content). Automatically cascades and cleans up connected edges.

---

### 2. Edges
- **`POST /edges`**: Add a directed weighted edge between two existing nodes.
  - Body: `{"source": "ServerA", "destination": "ServerB", "latency": 12.5}`
  - Response (`201`): `{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}`
  - Errors: `400` if unknown nodes, duplicate edge `(source, destination)`, non-positive latency (`<= 0`), or self-loop (`source == destination`).
- **`GET /edges`**: List all edges.
  - Response (`200`): `[{"id": 1, "source": "ServerA", "destination": "ServerB", "latency": 12.5}]`
- **`DELETE /edges/{id}`**: Delete an edge.
  - Response (`204` No Content).

---

### 3. Route Optimization
- **`POST /routes/shortest`**: Calculate lowest-latency path using Dijkstra's algorithm.
  - Body: `{"source": "ServerA", "destination": "ServerD"}`
  - Response (`200`):
    ```json
    {
      "total_latency": 23.4,
      "path": ["ServerA", "ServerB", "ServerD"]
    }
    ```
  - Errors:
    - `400`: Missing field or node does not exist.
    - `404`: No path exists (`{"error": "No path exists between ServerA and ServerE"}`).
  - *Note: Every successful query is automatically logged to query history.*

---

### 4. Route Query History
- **`GET /routes/history`**: Retrieve history of successful route calculations (ordered newest first).
  - Query parameters:
    - `?source=ServerA`: Filter by source node.
    - `?destination=ServerD`: Filter by destination node.
    - `?limit=5`: Limit number of returned results (must be integer `>= 1`).
    - `?date_from=2026-02-20T00:00:00Z` & `?date_to=2026-02-20T23:59:59Z`: Filter by ISO 8601 date range.
  - Response (`200`):
    ```json
    [
      {
        "id": 1,
        "source": "ServerA",
        "destination": "ServerD",
        "total_latency": 23.4,
        "path": ["ServerA", "ServerB", "ServerD"],
        "created_at": "2026-02-20T14:30:00Z"
      }
    ]
    ```

---

## 🧪 Testing & Coverage

Run the full pytest suite:
```powershell
uv run pytest
```

Run test suite with detailed line coverage report:
```powershell
uv run pytest --cov=network --cov-report=term-missing
```

### Coverage Summary:
```
Name                     Stmts   Miss  Cover
--------------------------------------------
network\admin.py            17      0   100%
network\models.py           25      0   100%
network\serializers.py      44      0   100%
network\services.py         27      0   100%
network\views.py            50      0   100%
network\urls.py              3      0   100%
...
--------------------------------------------
TOTAL                      543      0   100%
```
