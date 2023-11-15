    def _concat_same_type(
            cls, to_concat: Sequence["ArrowStringArray"]) -> "ArrowStringArray":
        chunks = list(itertools.chain.from_iterable(
            x._arrow_array.chunks for x in to_concat))
        if len(chunks) == 0:
            chunks = [pa.array([], type=pa.string())]
        return cls(pa.chunked_array(chunks))