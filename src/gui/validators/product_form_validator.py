class FormProductValidator:
    @staticmethod
    def validate_basic_data(data: dict) -> tuple[bool, list[str]]:
        errors = []
        
        if not data.get('name', '').strip():
            errors.append("El nombre del producto es requerido")
        
        try:
            quantity = int(data.get('quantity', '0'))
            if quantity <= 0:
                errors.append("La cantidad debe ser mayor o igual a 0")
        except ValueError:
            errors.append("La cantidad debe ser un número válido")
            
        try:
            price = int(data.get('price', '0'))
            if price <= 0:
                errors.append("El precio debe ser mayor o igual a 0")
        except ValueError:
            errors.append("El precio debe ser un número válido")
            
        sku = data.get('sku', '').strip()
        if sku and len(sku) < 3:
            errors.append("El código SKU debe tener menos 3 caracteres")
            
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_step_product_form_data(step_name: str, data: dict) -> tuple[bool, list[str]]:
        if step_name == "basic_data":
            return FormProductValidator.validate_basic_data(data)
        elif step_name == "availability":
            return FormProductValidator.validate_availability_data(data)
        else:
            return True, []
        
    @staticmethod
    def validate_availability_data(data: dict) -> tuple[bool, list[str]]:
        errors = []
        
        if not data.get('is_available'):
            errors.append("Debe indicar el estado")
        if not data.get('category'):
            errors.append("Debe indicar una categoria")
        if not data.get('brand'):
            errors.append("Debe indicar una marca")
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_edit_product_form_data(data: dict) -> tuple[bool, list[str]]:
        validator = FormProductValidator()
        if validator:
            validator.validate_basic_data(data)
            validator.validate_availability_data(data)
        return True, []