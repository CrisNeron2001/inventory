from __future__ import annotations
import argparse
import os
import shutil
import sys


def find_targets(root: str, remove_pyc_files: bool):
		pycache_dirs = []
		pyc_files = []
		for dirpath, dirnames, filenames in os.walk(root):
				for d in list(dirnames):
						if d == "__pycache__":
								pycache_dirs.append(os.path.join(dirpath, d))
				if remove_pyc_files:
						for f in filenames:
								if f.endswith(".pyc"):
										pyc_files.append(os.path.join(dirpath, f))
		return pycache_dirs, pyc_files

def remove_path(path: str):
		if os.path.isdir(path):
				shutil.rmtree(path, ignore_errors=False)
		else:
				os.remove(path)

def main():
		p = argparse.ArgumentParser(description="Eliminar __pycache__ recursivamente")
		p.add_argument("--root", "-r", default=".", help="Directorio raíz donde buscar (por defecto: cwd)")
		p.add_argument("--dry-run", action="store_true", help="Solo listar lo que se eliminaría")
		p.add_argument("--yes", "-y", action="store_true", help="No pedir confirmación")
		p.add_argument("--pyc", action="store_true", help="También eliminar archivos .pyc fuera de __pycache__")
		args = p.parse_args()

		root = os.path.abspath(args.root)
		if not os.path.exists(root):
				print(f"Ruta no encontrada: {root}", file=sys.stderr)
				sys.exit(2)

		pycache_dirs, pyc_files = find_targets(root, args.pyc)

		if not pycache_dirs and not pyc_files:
				print("No se encontraron __pycache__ ni archivos .pyc para eliminar.")
				return

		print("Se encontraron los siguientes elementos:")
		for d in pycache_dirs:
				print("  DIR:", d)
		for f in pyc_files:
				print("  FILE:", f)

		if args.dry_run:
				print("\nModo dry-run activado: no se realizarán borrados.")
				return

		if not args.yes:
				resp = input("\n¿Eliminar los elementos listados? [y/N]: ").strip().lower()
				if resp not in ("y", "yes"):
						print("Operación cancelada.")
						return

		errors = []
		removed_count = 0
		for d in pycache_dirs:
				try:
						remove_path(d)
						removed_count += 1
				except Exception as e:
						errors.append((d, str(e)))
		for f in pyc_files:
				try:
						remove_path(f)
						removed_count += 1
				except Exception as e:
						errors.append((f, str(e)))

		print(f"\nEliminados: {removed_count}")
		if errors:
				print("Errores durante la eliminación:")
				for path, err in errors:
						print(f"  {path}: {err}")
				sys.exit(1)

if __name__ == "__main__":
		main()