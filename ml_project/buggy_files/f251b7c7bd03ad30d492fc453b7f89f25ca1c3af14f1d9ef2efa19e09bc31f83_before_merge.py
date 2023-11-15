    def _concat_same_type(
            cls, to_concat: Sequence["ArrowArray"]) -> "ArrowArray":
        chunks = list(itertools.chain.from_iterable(
            x._arrow_array.chunks for x in to_concat))
        if len(chunks) == 0:
            chunks = [pa.array([], type=to_concat[0].dtype.arrow_type)]
        return cls(pa.chunked_array(chunks))