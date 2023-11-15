    def get_class_name(self, field_name: str) -> str:
        upper_camel_name = snake_to_upper_camel(field_name)
        return get_uniq_name(upper_camel_name, self.created_model_names, camel=True)