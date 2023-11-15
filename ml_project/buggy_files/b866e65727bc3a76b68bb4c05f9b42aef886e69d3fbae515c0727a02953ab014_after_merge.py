    def parse_enum(self, name: str, obj: JsonSchemaObject) -> DataModel:
        enum_fields = []

        for i, enum_part in enumerate(obj.enum):  # type: ignore
            if obj.type == 'string' or (
                isinstance(obj.type, list) and 'string' in obj.type
            ):
                default = f"'{enum_part}'"
                field_name = enum_part
            else:
                default = enum_part
                if obj.x_enum_varnames:
                    field_name = obj.x_enum_varnames[i]
                else:
                    field_name = f'{obj.type}_{enum_part}'
            enum_fields.append(
                self.data_model_field_type(name=field_name, default=default)
            )

        enum = Enum(self.get_class_name(name), fields=enum_fields)
        self.append_result(enum)
        return enum