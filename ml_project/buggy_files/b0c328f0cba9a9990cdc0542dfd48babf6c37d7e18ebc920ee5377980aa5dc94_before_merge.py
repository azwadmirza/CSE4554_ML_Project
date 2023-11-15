    def write(text):
        if index is not None:
            text = prepend_context(text, index, prefix)
        dst_stream.write(text)
        dst_stream.flush()