    def _execute_map(cls, ctx, op: "ProximaBuilder"):
        inp = ctx[op.tensor.key]
        out = op.outputs[0]
        pks = ctx[op.pk.key]
        proxima_type = get_proxima_type(inp.dtype)

        # holder
        holder = proxima.IndexHolder(type=proxima_type,
                                     dimension=op.dimension)
        for pk, record in zip(pks, inp):
            pk = pk.item() if hasattr(pk, 'item') else pk
            holder.emplace(pk, record.copy())

        # converter
        meta = proxima.IndexMeta(proxima_type, dimension=op.dimension,
                                 measure_name=op.distance_metric)
        if op.index_converter is not None:
            converter = proxima.IndexConverter(name=op.index_converter,
                                               meta=meta, params=op.index_converter_params)
            converter.train_and_transform(holder)
            holder = converter.result()
            meta = converter.meta()

        # builder && dumper
        builder = proxima.IndexBuilder(name=op.index_builder,
                                       meta=meta,
                                       params=op.index_builder_params)
        builder = builder.train_and_build(holder)

        path = tempfile.mkstemp(prefix='proxima-', suffix='.index')[1]
        dumper = proxima.IndexDumper(name="FileDumper", path=path)
        builder.dump(dumper)
        dumper.close()

        if op.index_path is None:
            ctx[out.key] = path
        else:
            # write to external file system
            fs = get_fs(op.index_path, op.storage_options)
            filename = f'proxima_{out.index[0]}_index'
            out_path = f'{op.index_path.rstrip("/")}/{filename}'
            with fs.open(out_path, 'wb') as out_f:
                with open(path, 'rb') as in_f:
                    # 32M
                    chunk_bytes = 32 * 1024 ** 2
                    while True:
                        data = in_f.read(chunk_bytes)
                        if data:
                            out_f.write(data)
                        else:
                            break

            ctx[out.key] = filename