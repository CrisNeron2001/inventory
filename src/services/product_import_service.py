import pandas as pd
from typing import List, Optional
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from services.category_service import CategoryService
from services.brand_service import BrandService
from services.product_service import ProductService
from utils.helpers import autoincrement_id
from config.settings import log

class ProductNormalizer:
	@staticmethod
	def clean(val):
		if pd.isna(val) or val == '' or (isinstance(val, str) and val.strip() == ''):
			return None
		if isinstance(val, str) and val.strip() == '""':
			return None
		return val

	@staticmethod
	def normalize_name(name):
		if not name:
			return None
		return str(name).replace('"', '').strip()

	@staticmethod
	def normalize_description(desc):
		return str(desc or '').strip()

	@staticmethod
	def normalize_stock(stock_raw):
		try:
			if stock_raw is None:
				return 0
			if isinstance(stock_raw, int):
				return stock_raw
			if isinstance(stock_raw, float):
				# Solo aceptar float si es entero exacto
				if stock_raw.is_integer():
					return int(stock_raw)
				else:
					return 0
			if isinstance(stock_raw, str):
				stock_str = stock_raw.strip().replace(',', '').replace(' ', '')
				if stock_str.upper() in ['', 'NULL', 'NAN']:
					return 0
				# Intentar convertir a int
				try:
					# Si es float pero termina en .0, lo acepta como int
					val = float(stock_str.replace('"', '').replace("'", ''))
					if val.is_integer():
						return int(val)
					else:
						return 0
				except Exception:
					return 0
			return 0
		except Exception:
			return 0

	@staticmethod
	def normalize_price(price_raw):
		if isinstance(price_raw, str):
			price_str = price_raw.replace('$', '').replace('"', '').replace(' ', '')
			try:
				return int(price_str) if price_str.isdigit() else int(''.join(filter(str.isdigit, price_str)))
			except Exception:
				return 0
		else:
			try:
				return int(price_raw) if price_raw else 0
			except Exception:
				return 0

	@staticmethod
	def normalize_is_available(stock, is_available_raw):
		is_available_str = str(is_available_raw).strip().lower() if is_available_raw is not None else ''
		if stock > 0:
			return True
		elif is_available_str in ['1', 'true', 'disponible', 'yes', 'si', 'y', 't']:
			return True
		else:
			return False

	@staticmethod
	def normalize_sku(sku):
		return str(sku).strip() if sku else None

class ProductImporter:
	def __init__(self):
		self.category_service = CategoryService()
		self.brand_service = BrandService()
		self.product_service = ProductService()
		self.categories = self.category_service.get_all_categories()
		self.brands = self.brand_service.get_all_brands()

	def find_category(self, cat_val, cat_df=None):
		if cat_val is None:
			return None

		cat_id = None
		try:
			cat_id = int(cat_val)
		except Exception:
			cat_id = None

		if cat_id is not None:
			category = next((c for c in self.categories if getattr(c, 'category_id', None) == cat_id), None)
			if category:
				return category

			# try to find in provided category sheet by id
			if cat_df is not None:
				for _, r in cat_df.iterrows():
					try:
						raw_val = ProductNormalizer.clean(r.get('category_id', r.get('id', None)))
						if raw_val is None:
							continue
						row_id = int(raw_val)
						if row_id == cat_id:
							cname = str(ProductNormalizer.clean(r.get('name', r.get('nombre', '')))).strip()
							exists = next((c for c in self.categories if c.name.strip().lower() == (cname or '').lower()), None)
							if exists:
								return exists
							category = self.category_service.create_category(
								CategoryDTO(
									category_id=cat_id, 
									name=cname or f'Category {cat_id}'
									)
								)
							if category:
								self.categories.append(category)
							return category
					except Exception:
						continue

		# try by name
		cat_name = str(cat_val).strip().lower()
		if cat_name == '':
			return None
		category = next((c for c in self.categories if c.name.strip().lower() == cat_name), None)
		if category:
			return category

		# try to find or create from category sheet by name
		if cat_df is not None:
			match_row = next((r for _, r in cat_df.iterrows() if str(ProductNormalizer.clean(r.get(
				'name', 
				r.get('nombre', '')
			))).strip().lower() == cat_name), None)
			if match_row is not None:
				new_id = None
				for icol in ('category_id', 'id'):
					try:
						val = ProductNormalizer.clean(match_row.get(icol))
						if val is not None:
							new_id = int(val)
							break
					except Exception:
						continue
				exists = next((c for c in self.categories if c.name.strip().lower() == cat_name), None)
				if exists:
					return exists
				cid = new_id if new_id is not None else autoincrement_id()
				category = self.category_service.create_category(CategoryDTO(
					category_id=cid, 
					name=str(
						match_row.get(
							'name', 
							match_row.get(
								'nombre', 
								cat_name))).strip()))
				if category:
					self.categories.append(category)
					return category

		return None

	def find_brand(self, brand_val, brand_df=None):
		if brand_val is None:
			return None

		# try by numeric id
		brand_id = None
		try:
			brand_id = int(brand_val)
		except Exception:
			brand_id = None

		if brand_id is not None:
			brand = next((b for b in self.brands if getattr(b, 'brand_id', None) == brand_id), None)
			if brand:
				return brand

			# try to find in provided brand sheet by id
			if brand_df is not None:
				for _, r in brand_df.iterrows():
					try:
						raw_val = ProductNormalizer.clean(r.get('brand_id', r.get('id', None)))
						if raw_val is None:
							continue
						row_id = int(raw_val)
						if row_id == brand_id:
							bname = str(ProductNormalizer.clean(r.get('name', r.get('nombre', '')))).strip()
							exists = next((b for b in self.brands if b.name.strip().lower() == (bname or '').lower()), None)
							if exists:
								return exists
							brand = self.brand_service.create_brand(BrandDTO(brand_id=brand_id, name=bname or f'Brand {brand_id}'))
							if brand:
								self.brands.append(brand)
							return brand
					except Exception:
						continue

		# try by name
		brand_name = str(brand_val).strip().lower()
		if brand_name == '':
			return None
		brand = next((b for b in self.brands if b.name.strip().lower() == brand_name), None)
		if brand:
			return brand

		# try to find or create from brand sheet by name
		if brand_df is not None:
			match_row = next((r for _, r in brand_df.iterrows() if str(ProductNormalizer.clean(
				r.get('name', 
		  		r.get('nombre', 
				'')))).strip().lower() == brand_name), None)
			if match_row is not None:
				new_id = None
				for icol in ('brand_id', 'id'):
					try:
						val = ProductNormalizer.clean(match_row.get(icol))
						if val is not None:
							new_id = int(val)
							break
					except Exception:
						continue
				exists = next((b for b in self.brands if b.name.strip().lower() == brand_name), None)
				if exists:
					return exists
				bid = new_id if new_id is not None else autoincrement_id()
				brand = self.brand_service.create_brand(BrandDTO(
					brand_id=bid, 
					name=str(
						match_row.get('name', match_row.get('nombre', brand_name))).strip()))
				if brand:
					self.brands.append(brand)
					return brand

		return None

	def import_products(self, filepath: str) -> List[ProductDTO]:
		print(f"[DEBUG] import_products llamado con: {filepath}")
		log.info(f"[IMPORT] Iniciando importación de productos desde archivo: {filepath}")
		try:
			if filepath.endswith('.csv'):
				print(f"[DEBUG] Leyendo CSV: {filepath}")
				df = pd.read_csv(filepath)
				sheets = {'Product': df}
			elif filepath.endswith('.xlsx'):
				print(f"[DEBUG] Leyendo XLSX: {filepath}")
				xl = pd.ExcelFile(filepath)
				sheets = {name: xl.parse(name) for name in xl.sheet_names}
			else:
				log.error(f"[IMPORT] Formato de archivo no soportado: {filepath}")
				print(f"[DEBUG] Formato de archivo no soportado: {filepath}")
				raise ValueError('Formato de archivo no soportado. Usa .csv o .xlsx')
		except Exception as e:
			log.error(f"[IMPORT] Error al leer archivo: {e}")
			print(f"[DEBUG] Error al leer archivo: {e}")
			return []

		# Buscar hojas
		prod_df = sheets.get('Product')
		cat_df = sheets.get('Category')
		brand_df = sheets.get('Brand')
		if prod_df is None:
			log.error("[IMPORT] No se encontró hoja 'Product' en el archivo.")
			print("[DEBUG] No se encontró hoja 'Product' en el archivo.")
			return []
		if cat_df is None:
			log.warning("[IMPORT] No se encontró hoja 'Category', se omite normalización de categorías.")
			print("[DEBUG] No se encontró hoja 'Category', se omite normalización de categorías.")
		if brand_df is None:
			log.warning("[IMPORT] No se encontró hoja 'Brand', se omite normalización de marcas.")
			print("[DEBUG] No se encontró hoja 'Brand', se omite normalización de marcas.")

		products = []
		print(f"[DEBUG] Filas a procesar: {len(prod_df)}")
		log.info(f"[IMPORT] Filas a procesar: {len(prod_df)}")
		for idx, row in prod_df.iterrows():
			try:
				name = ProductNormalizer.normalize_name(ProductNormalizer.clean(row.get('name', '')))
				if not name:
					log.warning(f"[IMPORT] Fila {idx}: nombre vacío, se omite.")
					print(f"[DEBUG] Fila {idx}: nombre vacío, se omite.")
					continue
				description = ProductNormalizer.normalize_description(ProductNormalizer.clean(row.get('description', '')))
				stock = ProductNormalizer.normalize_stock(ProductNormalizer.clean(row.get('stock', 0)))
				price = ProductNormalizer.normalize_price(ProductNormalizer.clean(row.get('price', 0)))
				sku = ProductNormalizer.normalize_sku(ProductNormalizer.clean(row.get('sku', '')))
				is_available = ProductNormalizer.normalize_is_available(stock, ProductNormalizer.clean(row.get('is_available', None)))

				# Buscar categoría por id o nombre usando hoja Category
				cat_val = ProductNormalizer.clean(row.get('category_id', row.get('category', None)))
				category = self.find_category(cat_val, cat_df)
				if category is None:
					log.warning(f"[IMPORT] Fila {idx}: categoría no encontrada, se omite.")
					print(f"[DEBUG] Fila {idx}: categoría no encontrada, se omite.")
					continue

				# Buscar marca por id o nombre usando hoja Brand
				brand_val = ProductNormalizer.clean(row.get('brand_id', row.get('brand', None)))
				brand = self.find_brand(brand_val, brand_df)
				if brand is None:
					log.warning(f"[IMPORT] Fila {idx}: marca no encontrada, se omite.")
					print(f"[DEBUG] Fila {idx}: marca no encontrada, se omite.")
					continue

				dto = ProductDTO(
					product_id=autoincrement_id(),
					name=name,
					description=description,
					stock=stock,
					price=price,
					sku=sku,
					is_available=is_available,
					category=category,
					brand=brand
				)
				created_product = self.product_service.create_product(dto)
				products.append(created_product)
				log.info(f"[IMPORT] Fila {idx}: producto '{name}' importado correctamente.")
				print(f"[DEBUG] Fila {idx}: producto '{name}' importado correctamente.")
			except Exception as ex:
				log.error(f"[IMPORT] Fila {idx}: error al importar producto: {ex}")
				print(f"[DEBUG] Fila {idx}: error al importar producto: {ex}")
		print(f"[DEBUG] Total productos importados: {len(products)}")
		log.info(f"[IMPORT] Total productos importados: {len(products)}")
		return products

# API principal para importar productos
def load_products_from_file(filepath: str) -> List[ProductDTO]:
    print(f"[DEBUG] load_products_from_file llamado con: {filepath}")
    importer = ProductImporter()
    productos = importer.import_products(filepath)
    print(f"[DEBUG] Productos importados: {len(productos)}")
    return productos