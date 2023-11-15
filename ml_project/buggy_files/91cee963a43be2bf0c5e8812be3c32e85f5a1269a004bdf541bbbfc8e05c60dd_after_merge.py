    def parse_object(
        self,
        name: str,
        obj: JsonSchemaObject,
        path: List[str],
        singular_name: bool = False,
        unique: bool = False,
        additional_properties: Optional[JsonSchemaObject] = None,
    ) -> DataModel:
        class_name = self.model_resolver.add(
            path, name, class_name=True, singular_name=singular_name, unique=unique
        ).name
        fields = self.parse_object_fields(obj, path)
        self.set_title(class_name, obj)
        self.set_additional_properties(class_name, additional_properties or obj)
        data_model_type = self.data_model_type(
            class_name,
            fields=fields,
            custom_base_class=self.base_class,
            custom_template_dir=self.custom_template_dir,
            extra_template_data=self.extra_template_data,
        )
        self.append_result(data_model_type)
        return data_model_type