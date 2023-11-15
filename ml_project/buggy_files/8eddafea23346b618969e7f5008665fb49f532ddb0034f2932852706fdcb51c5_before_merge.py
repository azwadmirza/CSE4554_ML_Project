    def parse_root_type(self, name: str, obj: JsonSchemaObject) -> None:
        if obj.type:
            types: List[DataType] = self.get_data_type(obj)
        elif obj.anyOf:
            types = self.parse_any_of(name, obj)
        else:
            types = [
                self.data_type(
                    type=obj.ref_object_name, ref=True, version_compatible=True
                )
            ]
        data_model_root_type = self.data_model_root_type(
            name,
            [
                self.data_model_field_type(
                    data_types=types,
                    description=obj.description,
                    example=obj.examples,
                    default=obj.default,
                    required=not obj.nullable,
                )
            ],
            custom_base_class=self.base_class,
            custom_template_dir=self.custom_template_dir,
            extra_template_data=self.extra_template_data,
        )
        self.append_result(data_model_root_type)