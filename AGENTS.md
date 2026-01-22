# Repository Guidelines

## Project Structure & Module Organization
- `backend-python/` contains the 3D volumetric pipeline and API. Core modules live in `backend-python/src/`, helpers in `backend-python/utils/`, and services/config in `backend-python/services.py` + `backend-python/config.yaml`.
- Test coverage for the Python pipeline is in `backend-python/tests/` (pytest).
- Input/output data is under `backend-python/data/` (`videos/`, `frames/`, `colmap_output/`). Treat generated folders (`frames/`, `colmap_output/`) as build artifacts.
- `ui-java/` contains the Swing UI. Source code lives in `ui-java/src/main/java/` and the distributable jar is `ui-java/release/InterfaceUI.jar`.

## Build, Test, and Development Commands
- `python3 backend-python/bin/venv_dependencies/setup_venv.py` — create/update the Python virtual environment and install dependencies.
- `DEV_MODE=true python3 backend-python/main.py` — run the pipeline from the terminal (backend-only, uses `config.yaml` execution mode).
- `python3 backend-python/main.py` — launch the Java UI and start the Flask backend.
- `pytest backend-python/tests` — run Python unit tests.
- `mvn -f ui-java/pom.xml package` — build the Java UI jar (Maven, Java 17).
- `java -jar ui-java/release/InterfaceUI.jar` — run the packaged UI directly.

## Coding Style & Naming Conventions
- Python: 4-space indentation, `snake_case` for functions/modules, `CamelCase` for classes.
- Java: standard `camelCase` for methods/fields and `PascalCase` for classes.
- Tests: `backend-python/tests/test_*.py` naming, mirroring pipeline modules.
- Data paths: keep media in `backend-python/data/videos/` and avoid hand-editing generated outputs.

## Testing Guidelines
- Framework: `pytest` for the Python backend.
- No explicit coverage threshold is configured; add tests for new pipeline logic and regression fixes.
- Keep tests focused on module boundaries (`acquisition`, `reconstruction`, `processing`).

## Commit & Pull Request Guidelines
- Existing commits use short, capitalized, imperative messages (e.g., “ADD LICENSE”, “Change target directory…”). Follow this style.
- PRs should include: a brief summary, how to run/verify, and screenshots when changing the Java UI.

## Configuration & Assets
- `backend-python/config.yaml` drives execution modes and pipeline behavior; document changes in PRs.
- Large datasets/videos should stay out of git and be referenced via `backend-python/data/`.
