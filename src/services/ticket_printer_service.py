from typing import Any, Iterable, Optional

try:
    from escpos.printer import Usb, Network, Serial, File
except Exception:  # pragma: no cover 
    Usb = Network = Serial = File = None  # type: ignore[misc,assignment]

from config.settings import log


class TicketPrinterConfig:
    def __init__(
        self,
        backend: str = "usb",
        vendor_id: Optional[int] = None,
        product_id: Optional[int] = None,
        host: str | None = None,
        port: int = 9100,
        serial_port: str | None = None,
        serial_baudrate: int = 9600,
        file_path: str | None = None,
    ) -> None:
        self.backend = backend.lower()
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.host = host
        self.port = port
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.file_path = file_path


class TicketPrinterService:
    def __init__(self, config: TicketPrinterConfig) -> None:
        self.config = config

    def _get_printer(self):
        if Usb is None and Network is None and Serial is None and File is None:
            log.error("[TicketPrinterService] La librería 'python-escpos' no está instalada.")
            raise RuntimeError("La librería 'python-escpos' no está instalada.")

        backend = self.config.backend

        if backend == "usb":
            if not (self.config.vendor_id and self.config.product_id):
                raise ValueError("Debe configurar 'vendor_id' y 'product_id' para backend USB.")
            if Usb is None:
                log.error("[TicketPrinterService] Backend USB no disponible porque 'python-escpos' no proporcionó Usb.")
                raise RuntimeError("Backend USB no disponible: la clase Usb no está disponible.")
            return Usb(self.config.vendor_id, self.config.product_id)

        if backend == "network":
            if not self.config.host:
                raise ValueError("Debe configurar 'host' para backend Network.")
            if Network is None:
                log.error("[TicketPrinterService] Backend Network no disponible porque 'python-escpos' no proporcionó Network.")
                raise RuntimeError("Backend Network no disponible: la clase Network no está disponible.")
            return Network(self.config.host, self.config.port)

        if backend == "serial":
            if not self.config.serial_port:
                raise ValueError("Debe configurar 'serial_port' para backend Serial.")
            if Serial is None:
                log.error("[TicketPrinterService] Backend Serial no disponible porque 'python-escpos' no proporcionó Serial.")
                raise RuntimeError("Backend Serial no disponible: la clase Serial no está disponible.")
            return Serial(self.config.serial_port, baudrate=self.config.serial_baudrate)

        if backend == "file":
            if not self.config.file_path:
                raise ValueError("Debe configurar 'file_path' para backend File.")
            if File is None:
                log.error("[TicketPrinterService] Backend File no disponible porque 'python-escpos' no proporcionó File.")
                raise RuntimeError("Backend File no disponible: la clase File no está disponible.")
            return File(self.config.file_path)

        raise ValueError(f"Backend de impresora no soportado: {backend}")

    def print_ticket(
        self,
        header_lines: Iterable[str] | None = None,
        items: Iterable[dict[str, Any]] | None = None,
        footer_lines: Iterable[str] | None = None,
    ) -> bool:

        try:
            printer = self._get_printer()
        except Exception as ex:  # pragma: no cover
            log.error(f"[TicketPrinterService.print_ticket] No se pudo obtener impresora: {ex}")
            return False

        try:
            if header_lines:
                for line in header_lines:
                    printer.text(str(line) + "\n")

            if header_lines:
                printer.text("-" * 32 + "\n")

            if items:
                for it in items:
                    name = str(it.get("name", ""))
                    qty = it.get("qty", 0)
                    price = it.get("price", 0)
                    total = it.get("total", 0)

                    left = f"{name[:16]:16s} {qty:>3}x{price:>5}"
                    right = f"{total:>6}"
                    line = f"{left} {right}\n"
                    printer.text(line)

            if footer_lines:
                printer.text("-" * 32 + "\n")
                for line in footer_lines:
                    printer.text(str(line) + "\n")

            printer.cut()
            return True
        except Exception as ex:  # pragma: no cover
            log.error(f"[TicketPrinterService.print_ticket] Error al imprimir ticket: {ex}")
            try:
                printer.close()  # type: ignore[call-arg]
            except Exception:
                pass
            return False
        finally:
            try:
                printer.close()  # type: ignore[call-arg]
            except Exception:
                pass

    def print_sale_ticket(
        self,
        sale: Any,
        cart_items: Iterable[dict[str, Any]],
        business_name: str = "Mi Comercio",
        business_rut: str | None = None,
    ) -> bool:
        sale_id = getattr(sale, "sale_id", None) if not isinstance(sale, dict) else sale.get("sale_id")
        total = getattr(sale, "total", None) if not isinstance(sale, dict) else sale.get("total")
        created_at = getattr(sale, "created_at", None) if not isinstance(sale, dict) else sale.get("created_at")

        header: list[str] = [str(business_name)]
        if business_rut:
            header.append(f"RUT: {business_rut}")
        if sale_id is not None:
            header.append(f"Venta N° {sale_id}")
        if created_at is not None:
            header.append(f"Fecha: {created_at}")

        items_print: list[dict[str, Any]] = []
        for it in cart_items:
            prod = it.get("product")
            name = None
            price = None
            if prod is not None:
                if isinstance(prod, dict):
                    name = prod.get("name")
                    price = prod.get("price")
                else:
                    name = getattr(prod, "name", None)
                    price = getattr(prod, "price", None)

            if name is None:
                name = str(it.get("name", "Producto"))
            if price is None:
                price = it.get("price", 0)

            qty = it.get("qty") or it.get("quantity") or 0
            line_total = it.get("line_total")
            if line_total is None and price is not None:
                line_total = int(price) * int(qty)

            items_print.append(
                {
                    "name": name,
                    "qty": int(qty),
                    "price": int(price or 0),
                    "total": int(line_total or 0),
                }
            )

        footer: list[str] = []
        if total is None:
            total = sum(it.get("total", 0) for it in items_print)
        footer.append(f"TOTAL: {total}")
        footer.append("Gracias por su compra")

        return self.print_ticket(header_lines=header, items=items_print, footer_lines=footer)
