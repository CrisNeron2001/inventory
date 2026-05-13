# Inventory POS

**Inventory and Point of Sale (POS)** application built with **Python**, using the **Flet** library for the graphical user interface.

## Overview

This project is an inventory and sales management system designed for small and medium-sized businesses. It allows you to keep track of products, categories, users, and sales from a desktop interface built with Flet.

## Main features

- Product management (create, edit, delete, search).
- Category and brand management.
- User registration and access control.
- Sales module with shopping cart.
- Ticket/receipt printing support (depending on configuration).
- Data persistence through a database.

## Technologies

- **Language:** Python
- **UI framework:** Flet
- **Database:** PostgreSQL
- **Dependencies:** managed with `requirements.txt` and `pyproject.toml` (including, for example, `python-escpos` for receipt printing).

## Project structure

- `src/`: main application source code.
  - `core/`: models, database, exceptions, and core logic.
  - `gui/`: views, controllers, and UI components.
  - `services/`: domain services (products, sales, users, etc.).
  - `utils/`: utilities and constants.
- `script/`: auxiliary scripts (database seeding, cleanup, etc.).

## Getting started

```pwsh
python -m venv .venv
```

Make sure you have Python installed and create a virtual environment. Then install the dependencies:

```pwsh
pip install -r requirements.txt
```

To run the application (adjust the command if your entry point changes):

```pwsh
python -m src.main
```

## Project status

Active development. Functionality and documentation may change over time.
