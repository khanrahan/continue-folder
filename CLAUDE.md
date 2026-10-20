# Continue Folder

Autodesk Flame 2025+ MediaHub plugin (Python 3.11, PySide6). It is the
reference layout for refactoring the other scripts in `../` (see the
`flame-script-refactor` skill).

## Running things

- Tests: `.venv/bin/python -m pytest -q` (`python` is not on PATH).
- Lint: `ruff check .` (ruff is installed globally, not in `.venv`).
- `flame` and the bundled PySide6 only import inside Flame, so
  `continue_folder.py` and the window/widget modules cannot be imported or
  run here. Tests cover only the Flame-free modules; say so when a change
  touches anything they don't import.

## Layout

All modules sit flat in the repo root, prefixed `continue_folder_`, because
Flame loads every `continue_folder*.py` from one folder.

- `continue_folder.py`: entry point and controller (`ContinueFolder`), the
  Flame menu hooks, and `TITLE` / `VERSION_INFO` constants.
- Model, no Qt or Flame: `_destination`, `_preset`, `_settings_store`,
  `_token`, `_token_store_input`, `_token_store_output`. All are tested.
- Windows: `_window_main`, `_window_save_preset`, `_window_mixin`. They emit
  Qt signals; the controller connects them.
- Widgets: `_pyflame_*` (`PyFlameButton`, `PyFlameLabel`, …) plus
  `_pyflame_colors` and `_button_mixin`. These are shared across scripts;
  keep edits minimal and avoid restructuring them.

## Conventions

- Module and class names use the same word order: `<script>_<group>_<thing>`
  → `<Group><Thing>` (`window_main` → `WindowMain`, `token_store_input` →
  `TokenStoreInput`, `pyflame_button` → `PyFlameButton`). Attributes follow
  suit (`token_store_input`).
- XML `Element` attributes end in `_element` (`_version_element`).
- Style is set in `pyproject.toml`: single quotes, Google docstrings, code
  lines ≤ 88, docstring lines ≤ 79.
- Rename files with `git mv`, never a plain move.

## Leave as is

- The `continue_folder.py` module docstring is a fixed Flame script header
  and fails D205/D212/D415. Don't reformat it.
- The version appears both in that header and in `VERSION_INFO`; both are
  required. Bump them together, along with `Update Date`.
- `ContinueFolder._windows` stays a dict keyed `'parent'`, `'main'`,
  `'save'`.
- `_convert_to_ascii` stays multi-line for readability.

## Settings

Presets live in `~/.config/continue-folder/continue_folder.xml` under
`<script_name>/<version>/<presets>`. `SettingsStore` loads the highest saved
`<version>` with the running major version and rewrites its text to the
running version; other major versions are left untouched.
