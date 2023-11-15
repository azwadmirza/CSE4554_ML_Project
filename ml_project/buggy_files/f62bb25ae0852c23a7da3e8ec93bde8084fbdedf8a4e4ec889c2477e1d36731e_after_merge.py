    def parse_any_of(self, name: str, obj: JsonSchemaObject) -> List[DataType]:
        any_of_data_types: List[DataType] = []
        for any_of_item in obj.anyOf:
            if any_of_item.ref:  # $ref
                any_of_data_types.append(
                    self.data_type(
                        type=any_of_item.ref_object_name,
                        ref=True,
                        version_compatible=True,
                    )
                )
            elif not any(v for k, v in vars(any_of_item).items() if k != 'type'):
                # trivial types
                any_of_data_types.extend(self.get_data_type(any_of_item))
            elif (
                any_of_item.is_array
                and isinstance(any_of_item.items, JsonSchemaObject)
                and not any(
                    v for k, v in vars(any_of_item.items).items() if k != 'type'
                )
            ):
                # trivial item types
                any_of_data_types.append(
                    self.data_type(
                        type=f"List[{', '.join([t.type_hint for t in self.get_data_type(any_of_item.items)])}]",
                        imports_=[Import(from_='typing', import_='List')],
                    )
                )
            else:
                singular_name = get_singular_name(name)
                self.parse_object(singular_name, any_of_item)
                any_of_data_types.append(
                    self.data_type(
                        type=singular_name, ref=True, version_compatible=True
                    )
                )
        return any_of_data_types