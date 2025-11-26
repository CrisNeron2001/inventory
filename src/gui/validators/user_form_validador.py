class UserFormValidator:
    @staticmethod
    def validate_form_user(data: dict) -> tuple[bool, list[str]]:
        errors = []
        
        fields_validate: dict[str, list[str]] = {
            "first_name": ["", "Este campo es requerido"],
            "username": ["", "Este campo es requerido"],
            "password": ["", "Este campo es requerido"],
            "role_inv": ["", "Este campo es requerido"],
        }
        for field, (_, message) in fields_validate.items():
            value = data.get(field, "")
            if not str(value).strip():
                errors.append(message)
        return len(errors) == 0, errors