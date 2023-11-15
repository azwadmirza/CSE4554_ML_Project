    def parse_array(self, name: str, obj: JsonSchemaObject, path: List[str]) -> None:
        field, item_obj_names = self.parse_array_fields(name, obj, [*path, name])
        self.model_resolver.add(path, name)
        data_model_root = self.data_model_root_type(
            name,
            [field],
            custom_base_class=self.base_class,
            custom_template_dir=self.custom_template_dir,
            extra_template_data=self.extra_template_data,
        )

        self.append_result(data_model_root)