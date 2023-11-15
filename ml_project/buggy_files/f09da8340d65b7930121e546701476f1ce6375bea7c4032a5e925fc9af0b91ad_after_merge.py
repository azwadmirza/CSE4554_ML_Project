    def get_data_type(self, obj: JsonSchemaObject) -> List[DataType]:
        if obj.type is None:
            return [
                self.data_type(
                    type='Any', version_compatible=True, imports_=[IMPORT_ANY]
                )
            ]
        if isinstance(obj.type, list):
            types: List[str] = [t for t in obj.type if t != 'null']
            format_ = 'default'
        else:
            types = [obj.type]
            format_ = obj.format or 'default'

        return [
            self.data_model_type.get_data_type(
                json_schema_data_formats[t][format_],
                **obj.dict() if not self.field_constraints else {},
            )
            for t in types
        ]