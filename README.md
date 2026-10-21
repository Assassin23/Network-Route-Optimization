# Network Route Optimization API

A REST API for modelling a network as a graph and finding the best routes through it. You add **nodes** (servers, routers and so on) and **edges** (weighted links between them), then ask for the optimal path between two nodes.

Built with **Django** and **Django REST Framework**, managed with **[uv](https://docs.astral.sh/uv/)**, and developed **test-first (TDD)** with **pytest**.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.13 |
| Web framework | Django 6 |
| API toolkit | Django REST Framework |
| Package / env manager | uv |
| Testing | pytest + pytest-django |
| Database (dev) | SQLite |

---

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/), which installs the right Python version for you
- Git

### Setup

```bash
git clone https://github.com/Assassin23/Network-Route-Optimization.git
cd Network-Route-Optimization

# Create the virtual environment and install all dependencies (including dev tools)
uv sync

# Create the local database
uv run python manage.py migrate
```

### Run the development server

```bash
uv run python manage.py runserver
```

The API will be available at <http://127.0.0.1:8000>.

---

## Running Tests

```bash
uv run pytest            # run the full test suite
uv run pytest -x         # stop at the first failure
uv run pytest -k nodes   # run tests whose name matches "nodes"
```

---

## API Reference

> 🚧 The API is being built incrementally. Endpoints marked **Planned** are not implemented yet.

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `POST` | `/nodes` | Add a node | Planned |
| — | Edges endpoints | Add, list and remove links between nodes | Planned |
| — | Route endpoints | Find the optimal path between two nodes | Planned |

### Add Node

**POST** `/nodes`

**Request body**

```json
{
  "name": "ServerA"
}
```

**Response: `201 Created`**

```json
{
  "id": 1,
  "name": "ServerA"
}
```

**Errors**

| Status | Reason |
|--------|--------|
| `400 Bad Request` | `name` is missing, blank, or already exists |

---

## Project Structure

```
.
├── config/            # Django project settings and root URL config
├── network/           # App: nodes, edges, route optimization
│   ├── migrations/
│   └── tests/         # pytest test suite
├── manage.py
├── pyproject.toml     # Project metadata and dependencies (uv)
├── uv.lock            # Locked dependency versions
└── pytest.ini         # pytest / pytest-django configuration
```

---

## Development Workflow

This project follows **Test-Driven Development**:

1. 🔴 **Red**: write a failing test for the next small behaviour.
2. 🟢 **Green**: write the minimum code to make it pass.
3. 🔵 **Refactor**: clean up while keeping all tests green.

### Useful commands

```bash
uv add <package>                          # add a runtime dependency
uv add --dev <package>                    # add a dev-only dependency
uv run python manage.py makemigrations    # create migrations after model changes
uv run python manage.py migrate           # apply migrations
```
