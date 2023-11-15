    def parse_object_fields(self, obj: JsonSchemaObject) -> List[DataModelField]:
        properties: Dict[str, JsonSchemaObject] = (
            obj.properties if obj.properties is not None else {}
        )
        requires: Set[str] = {*obj.required} if obj.required is not None else {*()}
        fields: List[DataModelField] = []

        for field_name, field in properties.items():  # type: ignore
            is_list = False
            field_types: List[DataType]
            if field.ref:
                field_types = [
                    self.data_type(
                        type=field.ref_object_name, ref=True, version_compatible=True
                    )
                ]
            elif field.is_array:
                class_name = self.get_class_name(field_name)
                array_fields, array_field_classes = self.parse_array_fields(
                    class_name, field
                )
                field_types = array_fields[0].data_types
                is_list = True
            elif field.anyOf:
                field_types = self.parse_any_of(field_name, field)
            elif field.allOf:
                field_types = self.parse_all_of(field_name, field)
            elif field.is_object:
                if field.properties:
                    class_name = self.get_class_name(field_name)
                    self.parse_object(class_name, field)
                    field_types = [
                        self.data_type(
                            type=class_name, ref=True, version_compatible=True
                        )
                    ]
                else:
                    field_types = [
                        self.data_type(
                            type='Dict[str, Any]',
                            imports_=[
                                Import(from_='typing', import_='Any'),
                                Import(from_='typing', import_='Dict'),
                            ],
                        )
                    ]
            elif field.enum:
                enum = self.parse_enum(field_name, field)
                field_types = [
                    self.data_type(type=enum.name, ref=True, version_compatible=True)
                ]
            else:
                data_type = self.get_data_type(field)
                field_types = [data_type]
            required: bool = field_name in requires
            fields.append(
                self.data_model_field_type(
                    name=field_name,
                    example=field.examples,
                    description=field.description,
                    default=field.default,
                    title=field.title,
                    data_types=field_types,
                    required=required,
                    is_list=is_list,
                )
            )
        return fields