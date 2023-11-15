def open(path, fs_options):
    source = vaex.file.open_for_arrow(path=path, mode='rb', fs_options=fs_options, mmap=True)
    file_signature = source.read(6)
    is_arrow_file = file_signature == b'ARROW1'
    source.seek(0)

    if is_arrow_file:
        reader = pa.ipc.open_file(source)
        # for some reason this reader is not iterable
        batches = [reader.get_batch(i) for i in range(reader.num_record_batches)]
    else:
        reader = pa.ipc.open_stream(source)
        batches = reader  # this reader is iterable
    table = pa.Table.from_batches(batches)
    return from_table(table)