import logging

#APP_SETTINGS = { "title": "Gestor de Inventario" , "window_size": (800, 600), "title_color": (0.2, 0.6, 0.8, 1) }

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	handlers=[
		logging.FileHandler("logger_inv.log"),
		logging.StreamHandler()
	]
)

log = logging.getLogger(__name__)