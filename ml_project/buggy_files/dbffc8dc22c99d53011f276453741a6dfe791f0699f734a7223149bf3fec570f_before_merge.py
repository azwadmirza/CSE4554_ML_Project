    def _describe_object(
        self,
        schema: s_schema.Schema,
        source: s_obj.Object,
    ) -> List[DumpBlockDescriptor]:

        cols = []
        shape = []
        ptrdesc: List[DumpBlockDescriptor] = []

        if isinstance(source, s_props.Property):
            schema, prop_tuple = s_types.Tuple.from_subtypes(
                schema,
                {
                    'source': schema.get('std::uuid'),
                    'target': source.get_target(schema),
                    'ptr_item_id': schema.get('std::uuid'),
                },
                {'named': True},
            )

            type_data, type_id = sertypes.TypeSerializer.describe(
                schema,
                prop_tuple,
                view_shapes={},
                view_shapes_metadata={},
                follow_links=False,
            )

            cols.extend([
                'source',
                'target',
                'ptr_item_id',
            ])

        elif isinstance(source, s_links.Link):
            props = {
                'source': schema.get('std::uuid'),
                'target': schema.get('std::uuid'),
                'ptr_item_id': schema.get('std::uuid'),
            }

            cols.extend([
                'source',
                'target',
                'ptr_item_id',
            ])

            for ptr in source.get_pointers(schema).objects(schema):
                if ptr.is_endpoint_pointer(schema):
                    continue

                stor_info = pg_types.get_pointer_storage_info(
                    ptr,
                    schema=schema,
                    source=source,
                    link_bias=True,
                )

                cols.append(stor_info.column_name)

                props[ptr.get_shortname(schema).name] = ptr.get_target(schema)

            schema, link_tuple = s_types.Tuple.from_subtypes(
                schema,
                props,
                {'named': True},
            )

            type_data, type_id = sertypes.TypeSerializer.describe(
                schema,
                link_tuple,
                view_shapes={},
                view_shapes_metadata={},
                follow_links=False,
            )

        else:
            for ptr in source.get_pointers(schema).objects(schema):
                if ptr.is_endpoint_pointer(schema):
                    continue

                stor_info = pg_types.get_pointer_storage_info(
                    ptr,
                    schema=schema,
                    source=source,
                )

                if stor_info.table_type == 'ObjectType':
                    cols.append(stor_info.column_name)
                    shape.append(ptr)

                link_stor_info = pg_types.get_pointer_storage_info(
                    ptr,
                    schema=schema,
                    source=source,
                    link_bias=True,
                )

                if link_stor_info is not None:
                    ptrdesc.extend(self._describe_object(schema, ptr))

            type_data, type_id = sertypes.TypeSerializer.describe(
                schema,
                source,
                view_shapes={source: shape},
                view_shapes_metadata={},
                follow_links=False,
            )

        table_name = pg_common.get_backend_name(
            schema, source, catenate=True
        )

        stmt = (
            f'COPY {table_name} '
            f'({", ".join(pg_common.quote_ident(c) for c in cols)}) '
            f'TO STDOUT WITH BINARY'
        ).encode()

        return [DumpBlockDescriptor(
            schema_object_id=source.id,
            schema_object_class=type(source).get_ql_class(),
            schema_deps=tuple(p.schema_object_id for p in ptrdesc),
            type_desc_id=type_id,
            type_desc=type_data,
            sql_copy_stmt=stmt,
        )] + ptrdesc