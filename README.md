# Data Relation Finder

> Ferramenta para descobrir possíveis relações entre datasets tabulares, mesmo sem chaves explícitas.

Undergraduate final project (TCC), B.Sc. Computer Science — **PUC-Rio**.

This tool analyzes tabular datasets (CSV) and automatically suggests **primary keys**, **foreign-key relationships** and **similar attributes** between tables, using a combination of statistical profiling and fuzzy textual matching. It is useful for data discovery, schema inference and data integration tasks.

## Key features

- **Data profiling** — column names, data types, unique/null counts for every dataset.
- **Primary-key suggestion** — columns are ranked by *uniqueness* and *non-null* thresholds.
- **Foreign-key detection** — candidate columns are tested for value *inclusion* across tables and compared by *name similarity* (fuzzy matching with `rapidfuzz`).
- **Relation validation** — suggested relations are scored with a confidence level before being accepted.
- **Harmonization** — suggests simple transformations (date/number formatting, whitespace normalization).
- **Exports** — consolidated report as CSV, JSON and Markdown.
- **Two interfaces** — interactive CLI and a FastAPI REST endpoint (with configurable thresholds).

## How it works

```
Load CSV(s) → Profile each dataset → Suggest PKs → Match attributes (fuzzy)
            → Detect candidate FKs (inclusion + name similarity) → Validate → Export report
```

Each analysis step is a dedicated component under `src/components/`, exposing a threshold
parameter that is passed both from the CLI and from the API.

## Tech stack

| Area | Tools |
|---|---|
| Language | Python |
| Data | pandas |
| Fuzzy matching | rapidfuzz (difflib fallback) |
| API | FastAPI (OpenAPI docs at `/docs`) |
| Tests | pytest |

## Project structure

```
.
├── api.py                 # FastAPI application (POST /analyze_folder/)
├── src/
│   ├── main.py            # CLI entry point + orchestration
│   ├── components/        # data_profiler, attribute_matcher, fk_finder, attribute_validator
│   └── utils/             # file_handler, logger, data_loader, result_exporter
├── tests/                 # pytest suite + data generators
├── docs/                  # TCC documents (proposal, report, LaTeX)
└── datasets/              # sample real datasets used in the project
```

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Run the CLI:

```bash
python -m src.main --help
```

Run the API:

```bash
uvicorn api:app --reload
# interactive docs: http://localhost:8000/docs
```

Run the tests:

```bash
pytest -v
```

## Documentation

All academic artifacts (project proposal, final report and LaTeX sources) are available
under [`docs/`](./docs). The thesis was developed with a real-world use case: discovering
relations between fisheries datasets (Brazilian fishing records).

---

🇧🇷 Projeto final de graduação em Ciência da Computação na PUC-Rio, orientado pelo
Instituto Tecgraf. Desenvolvido por **Sérgio Bernardelli Netto**.

[Portfolio](https://sbnetto01.github.io/Portfolio-SBN/) · [LinkedIn](https://www.linkedin.com/in/sergio-b-netto/)