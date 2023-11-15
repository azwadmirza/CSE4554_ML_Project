    def write(text):
        if index is not None and prefix is not None:
            context = get_context(index, prefix)
            dst_stream.write(context)
        dst_stream.write(text)
        dst_stream.flush()