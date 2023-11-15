    def parse_object_fields(
        self, obj: JsonSchemaObject, path: List[str]
    ) -> List[DataModelFieldBase]:
        properties: Dict[str, JsonSchemaObject] = (
            obj.properties if obj.properties is not None else {}
        )
        requires: Set[str] = {*obj.required} if obj.required is not None else {*()}
        fields: List[DataModelFieldBase] = []

        for field_name, field in properties.items():
            is_list: bool = False
            is_union: bool = False
            field_types: List[DataType]
            original_field_name: str = field_name
            constraints: Optional[Mapping[str, Any]] = None
            field_name, alias = self.model_resolver.get_valid_field_name_and_alias(
                field_name
            )
            if field.ref:
                field_types = [
                    self.data_type(
                        type=self.model_resolver.add_ref(field.ref).name,
                        ref=True,
                        version_compatible=True,
                    )
                ]
            elif field.is_array:
                array_field, array_field_classes = self.parse_array_fields(
                    field_name, field, [*path, field_name]
                )
                field_types = array_field.data_types
                is_list = True
                is_union = True
            elif field.anyOf:
                field_types = self.parse_any_of(field_name, field, [*path, field_name])
            elif field.oneOf:
                field_types = self.parse_one_of(field_name, field, [*path, field_name])
            elif field.allOf:
                field_types = self.parse_all_of(field_name, field, [*path, field_name])
            elif field.is_object:
                if field.properties:
                    field_types = [
                        self.data_type(
                            type=self.parse_object(
                                field_name, field, [*path, field_name], unique=True
                            ).name,
                            ref=True,
                            version_compatible=True,
                        )
                    ]
                elif isinstance(field.additionalProperties, JsonSchemaObject):
                    additional_properties_type = self.parse_object(
                        field_name,
                        field.additionalProperties,
                        [*path, field_name],
                        unique=True,
                    ).name

                    field_types = [
                        self.data_type(
                            type=f'Dict[str, {additional_properties_type}]',
                            imports_=[IMPORT_DICT],
                            unresolved_types=[additional_properties_type],
                        )
                    ]
                else:
                    field_types = [
                        self.data_type(
                            type='Dict[str, Any]', imports_=[IMPORT_ANY, IMPORT_DICT],
                        )
                    ]
            elif field.enum:
                enum = self.parse_enum(
                    field_name, field, [*path, field_name], unique=True
                )
                field_types = [
                    self.data_type(type=enum.name, ref=True, version_compatible=True)
                ]
            else:
                field_types = self.get_data_type(field)
                if self.field_constraints:
                    constraints = field.dict()
            required: bool = original_field_name in requires
            fields.append(
                self.data_model_field_type(
                    name=field_name,
                    example=field.example,
                    examples=field.examples,
                    description=field.description,
                    default=field.default,
                    title=field.title,
                    data_types=field_types,
                    required=required,
                    is_list=is_list,
                    is_union=is_union,
                    alias=alias,
                    constraints=constraints,
                )
            )
        return fields