import pandas as pd
from typing import List, Optional
from core.models.dto.product_dto import ProductDTO
from core.models.dto.category_dto import CategoryDTO
from core.models.dto.brand_dto import BrandDTO
from services.category_service import CategoryService
from services.brand_service import BrandService
from services.product_service import ProductService
from utils.helpers import autoincrement_id, autoincrement_sku
from config.settings import log
import unicodedata

class ProductNormalizer:
	@staticmethod
	def normalize_text(value: str) -> str:
		if value is None:
			return ""
		text = str(value).strip().lower()
		nfkd = unicodedata.normalize("NFKD", text)
		text = "".join(c for c in nfkd if not unicodedata.combining(c))
		text = " ".join(text.split())
		return text
	
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
		return str(desc or '*Ingrese una descripción').strip()

	@staticmethod
	def normalize_stock(stock_raw):
		try:
			if stock_raw is None:
				return 0

			allowed = {"": 0, "NULL": 0, "NAN": 0, "NONE": 0}

			if isinstance(stock_raw, str):
				stock_str = stock_raw.strip()
				normalized = stock_str.upper()
				if normalized in allowed:
					return allowed[normalized]

				cleaned = stock_str.replace(" ", "").replace(",", "")
				cleaned = cleaned.replace('"', "").replace("'", "")

				try:
					val = float(cleaned)
					return int(val) if val.is_integer() and val >= 0 else 0
				except Exception:
					return 0

			if isinstance(stock_raw, (int, float)):
				try:
					val = float(stock_raw)
					return int(val) if val.is_integer() and val >= 0 else 0
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
		try:
			s = int(stock or 0)
		except Exception:
			s = 0

		stock_checks = {
			'zero': s == 0,
			'positive': s > 0
		}
		stock_results = {
			'zero': False,
			'positive': True
		}

		for key, cond in stock_checks.items():
			if cond:
				return stock_results[key]

		if is_available_raw is None or (isinstance(is_available_raw, float) and pd.isna(is_available_raw)):
			val = ""
		else:
			val = str(is_available_raw).strip().lower()

		falsy = {"0", "false", "no", "n", "f"}
		return False if val in falsy else True

	@staticmethod
	def normalize_sku(sku_raw):
		return str(sku_raw).strip() if sku_raw else None

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

		norm_input_name = ProductNormalizer.normalize_text(str(cat_val))
		
		cat_id = None
		try:
			cat_id = int(cat_val)
		except Exception:
			cat_id = None

		if cat_id is not None:
			category = next((c for c in self.categories if getattr(c, 'category_id', None) == cat_id), None)
			if category:
				return category

		if norm_input_name == "":
			return None
		for c in self.categories:
			cname_norm = ProductNormalizer.normalize_text(getattr(c, 'name', ''))
			if cname_norm == norm_input_name:
				return c

		if cat_df is not None:
			match_row = None
			for _, r in cat_df.iterrows():
				row_name = ProductNormalizer.clean(r.get('name', r.get('name', '')))
				row_name_norm = ProductNormalizer.normalize_text(str(row_name))
				if row_name_norm == norm_input_name:
					match_row = r
					break

			if match_row is not None:
				new_id = None
				for icol in ('category_id', 'id'):
					try:
						val = ProductNormalizer.clean(match_row.get(icol))
						if val is not None:
							candidate_id = int(val)
							if next((c for c in self.categories if getattr(c, 'category_id', None) == candidate_id), None) is None:
								new_id = candidate_id
							break
					except Exception:
						continue

				for c in self.categories:
					cname_norm = ProductNormalizer.normalize_text(getattr(c, 'name', ''))
					if cname_norm == norm_input_name:
						return c

				cid = new_id if new_id is not None else autoincrement_id()
				category_name = str(
					match_row.get(
						'name', 
						match_row.get('nombre', cat_val))
					).strip()
				category = self.category_service.create_category(
					CategoryDTO(
						category_id=cid,
						name=category_name
					)
				)
				if category:
					log.info(f"[ProductImporter.find_category] Nueva categoría creada desde Excel: id={cid}, nombre='{category_name}' (valor original: '{cat_val}')")
					self.categories.append(category)
					return category

		return None

	def find_brand(self, brand_val, brand_df=None):
		if brand_val is None:
			return None

		norm_input_name = ProductNormalizer.normalize_text(str(brand_val))

		brand_id = None
		try:
			brand_id = int(brand_val)
		except Exception:
			brand_id = None

		if brand_id is not None:
			brand = next((b for b in self.brands if getattr(b, 'brand_id', None) == brand_id), None)
			if brand:
				return brand

		if norm_input_name == "":
			return None
		for b in self.brands:
			bname_norm = ProductNormalizer.normalize_text(getattr(b, 'name', ''))
			if bname_norm == norm_input_name:
				return b

		if brand_df is not None:
			match_row = None
			for _, r in brand_df.iterrows():
				row_name = ProductNormalizer.clean(r.get('name', r.get('nombre', '')))
				row_name_norm = ProductNormalizer.normalize_text(str(row_name))
				if row_name_norm == norm_input_name:
					match_row = r
					break

			if match_row is not None:
				new_id = None
				for icol in ('brand_id', 'id'):
					try:
						val = ProductNormalizer.clean(match_row.get(icol))
						if val is not None:
							candidate_id = int(val)
							if next((b for b in self.brands if getattr(b, 'brand_id', None) == candidate_id), None) is None:
								new_id = candidate_id
							break
					except Exception:
						continue

				for b in self.brands:
					bname_norm = ProductNormalizer.normalize_text(getattr(b, 'name', ''))
					if bname_norm == norm_input_name:
						return b

				bid = new_id if new_id is not None else autoincrement_id()
				brand_name = str(match_row.get('name', match_row.get('name', brand_val))).strip()
				brand = self.brand_service.create_brand(
					BrandDTO(
						brand_id=bid,
						name=brand_name
					)
				)
				if brand:
					log.info(f"[ProductImporter.find_brand] Nueva marca creada desde Excel: id={bid}, nombre='{brand_name}' (valor original: '{brand_val}')")
					self.brands.append(brand)
					return brand

		return None

	def import_products(self, filepath: str) -> List[ProductDTO]:
		log.info(f"[ProductImporter.import_product] Iniciando importación de productos desde archivo: {filepath}")
		try:
			if filepath.endswith('.csv'):
				df = pd.read_csv(filepath)
				sheets = {'Product': df}
			elif filepath.endswith('.xlsx'):
				xl = pd.ExcelFile(filepath)
				sheets = {name: xl.parse(name) for name in xl.sheet_names}
			else:
				log.error(f"[ProductImporter.import_product] Formato de archivo no soportado: {filepath}")
				raise ValueError('Formato de archivo no soportado. Usa .csv o .xlsx')
		except Exception as e:
			log.error(f"[ProductImporter.import_product] Error al leer archivo: {e}")
			return []

		prod_df = sheets.get('Product')
		cat_df = sheets.get('Category')
		brand_df = sheets.get('Brand')
		if prod_df is None:
			log.error("[ProductImporter.import_product] No se encontró hoja 'Product' en el archivo.")
			return []
		if cat_df is None:
			log.warning("[ProductImporter.import_product] No se encontró hoja 'Category', se omite normalización de categorías.")
		if brand_df is None:
			log.warning("[ProductImporter.import_product] No se encontró hoja 'Brand', se omite normalización de marcas.")

		products = []
		new_sku = None
		log.info(f"[ProductImporter.import_product] Filas a procesar: {len(prod_df)}")
		for idx, row in prod_df.iterrows():
			try:
				field_name = ProductNormalizer.normalize_name(ProductNormalizer.clean(row.get('name', '')))
				if not field_name:
					log.warning(f"[ProductImporter.import_product] Fila {idx}: nombre vacío, se omite.")
					continue
				field_description = ProductNormalizer.normalize_description(ProductNormalizer.clean(row.get('description', '*Ingrese una descripción')))
				field_stock = ProductNormalizer.normalize_stock(ProductNormalizer.clean(row.get('stock', 0)))
				field_price = ProductNormalizer.normalize_price(ProductNormalizer.clean(row.get('price', 0)))
				field_sku = ProductNormalizer.normalize_sku(ProductNormalizer.clean(row.get('sku', '')))
				field_is_available = ProductNormalizer.normalize_is_available(field_stock, ProductNormalizer.clean(row.get('is_available', None)))
				new_sku = field_sku if field_sku is not None else autoincrement_sku()

				cat_val = ProductNormalizer.clean(row.get('category'))
				if cat_val is None:
					cat_val = ProductNormalizer.clean(row.get('category_name'))
				
				brand_val = ProductNormalizer.clean(row.get('brand'))
				if brand_val is None:
					brand_val = ProductNormalizer.clean(row.get('brand_name'))
				
				field_category = self.find_category(cat_val, cat_df)
				if field_category is None:
					log.warning(f"[ProductImporter.import_product] Fila {idx}: categoría no encontrada, se omite. Valor recibido: {cat_val}")
					continue
				
				field_brand = self.find_brand(brand_val, brand_df)
				if field_brand is None:
					log.warning(f"[ProductImporter.import_product] Fila {idx}: marca no encontrada, se omite. Valor recibido: {brand_val}")
					continue
				
				dto = ProductDTO(
					product_id=autoincrement_id(),
					name=field_name,
					description=field_description,
					stock=field_stock,
					price=field_price,
					sku=new_sku,
					is_available=field_is_available,
					category=field_category,
					brand=field_brand,
				)
				created_product = self.product_service.create_product(dto)
				products.append(created_product)
				log.info(f"[ProductImporter.import_product] Fila {idx}: producto '{field_name}' importado correctamente.")
			except Exception as ex:
				log.error(f"[ProductImporter.import_product] Fila {idx}: error al importar producto: {ex}")
		log.info(f"[ProductImporter.import_product] Total productos importados: {len(products)}")
		return products

def load_products_from_file(filepath: str) -> List[ProductDTO]:
    importer = ProductImporter()
    productos = importer.import_products(filepath)
    return productos