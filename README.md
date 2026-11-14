# Roadmap Tracker

A personal roadmap, notes, projects, and calendar tracker built with Flask and SQLite.

Organize learning or career goals into roadmaps, break them into stages and topics, track projects and notes, and see all deadlines on a calendar.

## Features

- **Roadmaps** with title, description, and color, plus automatic progress percentage
- **Stages** inside each roadmap, ordered by position
- **Topics** with status (`not_started` / `in_progress` / `completed`), priority, and due date
- **Projects** with status, tech stack, repository URL, due date, and optional stage link
- **Notes** attachable to a roadmap, stage, or topic
- **Calendar view** aggregating topic and project deadlines via JSON API
- **JSON export/import** for backups and migrations
- Server-rendered UI using Bootstrap and Bootstrap Icons (CDN)

## Tech Stack

- Python 3.12+
- Flask
- Flask-SQLAlchemy
- SQLite
- python-dotenv
- Ruff (linting/formatting)
- [uv](https://docs.astral.sh/uv/) for dependency management

## Getting Started

### Prerequisites

- Python 3.12+
- `uv`

### Setup

```bash
make install
cp .env.example .env   # adjust values as needed
make init-db           # optional; tables are also created on app startup
make run
```

The app runs at `http://127.0.0.1:5000`.

### Environment Variables

| Variable       | Default                     | Description                     |
| -------------- | --------------------------- | ------------------------------- |
| `SECRET_KEY`   | `dev-secret-key`            | Flask session secret            |
| `DATABASE_URL` | `sqlite:///roadmap.db`      | SQLAlchemy database connection  |
| `FLASK_APP`    | `src.main:app`              | Flask application entry point   |

The SQLite file is created in `instance/`.

## Usage

| Route                        | Description                        |
| ---------------------------- | ---------------------------------- |
| `/`                          | Roadmap dashboard                  |
| `/calendar`                  | Calendar of all deadlines          |
| `/api/calendar/events`       | JSON feed of topics/projects       |
| `/api/export/json`           | Download a JSON backup             |
| `/roadmap/import`            | Import a JSON backup (POST)        |

Creating, editing, deleting, and status-cycling items are handled through form `POST` routes defined in `src/main.py`.

## Project Structure

```
src/
  main.py              Flask app, models, routes, JSON import/export
  templates/
    base.html          Shared layout and navigation
    index.html         Roadmap dashboard
    calendar.html      Calendar view
instance/
  roadmap.db           SQLite database (gitignored)
Makefile               install / run / init-db / clean targets
pyproject.toml         Project metadata and dependencies
```

## Development

Run the development server with auto-reload:

```bash
make run
```

Lint the code:

```bash
uv run ruff check .
```

Reset the local database:

```bash
make clean
make init-db
```

## Data Model

- `Roadmap` has many `Stage`, `Project`, and `Note` records.
- `Stage` belongs to a `Roadmap` and has many `Topic` records.
- `Topic` belongs to a `Stage`.
- `Project` belongs to a `Roadmap` and optionally a `Stage`.
- `Note` belongs to a `Roadmap` and optionally a `Stage` or `Topic`.

Deleting a roadmap cascades to its stages, topics, projects, and notes.
