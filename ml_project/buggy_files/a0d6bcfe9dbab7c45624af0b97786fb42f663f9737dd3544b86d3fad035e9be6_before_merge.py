    async def describe_database_restore(
        self,
        tx_snapshot_id: str,
        dump_server_ver_str: Optional[str],
        schema_ddl: bytes,
        schema_ids: List[Tuple[str, str, bytes]],
        blocks: List[Tuple[bytes, bytes]],  # type_id, typespec
    ) -> RestoreDescriptor:
        schema_object_ids = {
            (name, qltype if qltype else None): uuidgen.from_bytes(objid)
            for name, qltype, objid in schema_ids
        }

        if dump_server_ver_str is not None:
            dump_server_ver = verutils.parse_version(dump_server_ver_str)
        else:
            dump_server_ver = None

        schema = await self._introspect_schema_in_snapshot(tx_snapshot_id)
        ctx = await self._ctx_new_con_state(
            dbver=b'',
            io_format=enums.IoFormat.BINARY,
            expect_one=False,
            modaliases=DEFAULT_MODULE_ALIASES_MAP,
            session_config=EMPTY_MAP,
            stmt_mode=enums.CompileStatementMode.ALL,
            capability=enums.Capability.ALL,
            json_parameters=False,
            schema=schema,
            schema_object_ids=schema_object_ids,
            compat_ver=dump_server_ver,
        )
        ctx.state.start_tx()

        units = self._compile(
            ctx=ctx,
            tokens=tokenizer.tokenize(schema_ddl),
        )
        schema = ctx.state.current_tx().get_schema()

        restore_blocks = []
        tables = []
        for schema_object_id, typedesc in blocks:
            schema_object_id = uuidgen.from_bytes(schema_object_id)
            obj = schema._id_to_type.get(schema_object_id)
            desc = sertypes.TypeSerializer.parse(typedesc)

            if isinstance(obj, s_props.Property):
                assert isinstance(desc, sertypes.NamedTupleDesc)
                desc_ptrs = list(desc.fields.keys())
                if set(desc_ptrs) != {'source', 'target', 'ptr_item_id'}:
                    raise RuntimeError(
                        'Property table dump data has extra fields')
                cols = {
                    'source': 'source',
                    'target': 'target',
                    'ptr_item_id': 'ptr_item_id',
                }

            elif isinstance(obj, s_links.Link):
                assert isinstance(desc, sertypes.NamedTupleDesc)
                desc_ptrs = list(desc.fields.keys())
                cols = {
                    'source': 'source',
                    'target': 'target',
                    'ptr_item_id': 'ptr_item_id',
                }

                for ptr in obj.get_pointers(schema).objects(schema):
                    if ptr.is_endpoint_pointer(schema):
                        continue
                    stor_info = pg_types.get_pointer_storage_info(
                        ptr,
                        schema=schema,
                        source=obj,
                        link_bias=True,
                    )

                    ptr_name = ptr.get_shortname(schema).name
                    cols[ptr_name] = stor_info.column_name

                if set(desc_ptrs) != set(cols):
                    raise RuntimeError(
                        'Link table dump data has extra fields')

            elif isinstance(obj, s_objtypes.ObjectType):
                assert isinstance(desc, sertypes.ShapeDesc)
                desc_ptrs = list(desc.fields.keys())

                cols = {}
                for ptr in obj.get_pointers(schema).objects(schema):
                    if ptr.is_endpoint_pointer(schema):
                        continue

                    stor_info = pg_types.get_pointer_storage_info(
                        ptr,
                        schema=schema,
                        source=obj,
                    )

                    if stor_info.table_type == 'ObjectType':
                        ptr_name = ptr.get_shortname(schema).name
                        cols[ptr_name] = stor_info.column_name

                if set(desc_ptrs) != set(cols):
                    raise RuntimeError(
                        'Object table dump data has extra fields')

            else:
                raise AssertionError(
                    f'unexpected object type in restore '
                    f'type descriptor: {obj!r}'
                )

            table_name = pg_common.get_backend_name(
                schema, obj, catenate=True)

            col_list = (pg_common.quote_ident(cols[pn]) for pn in desc_ptrs)

            stmt = (
                f'COPY {table_name} '
                f'({", ".join(col_list)})'
                f'FROM STDIN WITH BINARY'
            ).encode()

            restore_blocks.append(
                RestoreBlockDescriptor(
                    schema_object_id=schema_object_id,
                    sql_copy_stmt=stmt,
                )
            )

            tables.append(table_name)

        return RestoreDescriptor(
            units=units,
            blocks=restore_blocks,
            tables=tables,
        )