# Test Suite Overview

This directory contains automated tests for the Smart Inventory platform. The goal of the suite is to
protect the core forecasting and inventory logic while providing confidence that end-to-end workflows
and the Streamlit UI continue to operate as expected.

## Directory structure

```
tests/
├── core/               # Isolated unit tests for forecast and inventory logic
│   ├── forecasting/
│   │   └── test_baseline.py
│   └── inventory/
│       └── test_reorder.py
└── integration/        # Multi-component integration and smoke tests
    ├── test_end_to_end.py
    └── test_ui.py
```

### `core/forecasting/test_baseline.py`
Unit tests for the baseline demand forecasting utilities in
`packages.core.forecasting.baseline`. They validate:

* Conversion of raw sales data to a zero-filled daily time series via `to_daily`.
* Behavior of `moving_avg_forecast`, including handling of short histories, all-zero series, and
  long-horizon forecasts.
* Basic non-regression properties such as monotonic forecast dates and non-negative predictions.

### `core/inventory/test_reorder.py`
Unit tests for `packages.core.inventory.reorder.suggest_order`. The checks focus on:

* Returning a zero order quantity when existing stock covers demand.
* Respecting minimum order quantities and clipping negative demand.
* Increased safety stock and reorder points under high demand variability.

### `integration/test_end_to_end.py`
Integration tests that exercise the forecast-to-reorder pipeline using both synthetic data and the
sample CSV files stored under `data/`. The scenarios ensure:

* Daily demand conversion, forecasting, and reorder suggestions link together without errors.
* Outputs remain non-negative, respect minimum order quantities, and return numeric types suitable
  for downstream consumption.

### `integration/test_ui.py`
A smoke test that boots the Streamlit application defined in `apps/web/Home.py` for a few seconds to
confirm it starts without crashing. The test terminates the subprocess after the health check to
avoid leaving background processes.

## Running the tests

1. Install the project dependencies (see the repository-level `README.md` or run `pip install -r requirements.txt`).
2. From the project root, run the entire suite with:
   ```bash
   pytest
   ```
3. To target a subset of tests, point `pytest` at a directory or file, e.g.:
   ```bash
   pytest tests/core            # unit tests only
   pytest tests/integration/test_ui.py -k streamlit
   ```

> **Tip:** The UI smoke test launches Streamlit; if you only want fast logic checks, you can exclude
> it with `pytest -k "not test_streamlit_ui_starts"`.

## Adding new tests

* Co-locate unit tests with the relevant domain area under `tests/core/`.
* Prefer descriptive test names and docstrings so the intent is clear without reading the
  implementation.
* When integration tests depend on fixture data, document or version the datasets in the `data/`
  directory to keep runs reproducible.

Keeping this structure and set of conventions helps ensure the Smart Inventory codebase remains
maintainable and well-tested as new features land.
