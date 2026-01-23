# Inventory POS

Aplicación de **inventario con punto de venta (POS)** desarrollada en **Python**, utilizando la librería **Flet** para la interfaz gráfica de usuario.

## Descripción general

Este proyecto es un sistema de gestión de inventario y ventas pensado para pequeños y medianos negocios. Permite llevar control de productos, categorías, usuarios y ventas desde una interfaz de escritorio construida con Flet.

## Características principales

- Gestión de productos (creación, edición, eliminación, búsqueda).
- Manejo de categorías y marcas.
- Registro y control de usuarios.
- Módulo de ventas con carrito de compra.
- Integración con impresora de tickets (según configuración).
- Persistencia de datos mediante base de datos.

## Tecnologías

- **Lenguaje:** Python
- **Interfaz gráfica:** Flet
- **Base de datos:** PostgreSQL
- **Dependencias:** gestionadas mediante `requirements.txt` y `pyproject.toml` (incluye, por ejemplo, `python-escpos` para impresión de boletas).

## Estructura básica del proyecto

- `src/`: código fuente principal de la aplicación.
  - `core/`: modelos, base de datos, excepciones y lógica central.
  - `gui/`: vistas, controladores y componentes de la interfaz.
  - `services/`: servicios de dominio (productos, ventas, usuarios, etc.).
  - `utils/`: utilidades y constantes.
- `script/`: scripts auxiliares (poblado de base de datos, limpieza, etc.).

## Ejecución básica

Asegúrate de tener Python instalado y de crear un entorno virtual. Luego instala las dependencias:

```pwsh
pip install -r requirements.txt
```

Para ejecutar la aplicación (ajusta el comando si tu punto de entrada cambia):

```pwsh
python -m src.main
```

## Estado del proyecto

Proyecto en desarrollo activo. La funcionalidad y documentación pueden ir cambiando con el tiempo.
