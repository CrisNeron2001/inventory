class NameFieldValidator:
    @staticmethod
    def validate_name_field(data: dict) -> tuple[bool, list[str]]:
        errors = []
        
        if not data.get('name', '').strip():
            errors.append("El nombre es requerido")
            
        return len(errors) ==  0, errors