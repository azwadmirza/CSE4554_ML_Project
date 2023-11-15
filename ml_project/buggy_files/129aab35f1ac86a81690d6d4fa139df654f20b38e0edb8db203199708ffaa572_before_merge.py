    def _concat_same_type(
        cls, to_concat: Sequence["ArrowStringArray"]) -> "ArrowStringArray":
        chunks = list(itertools.chain.from_iterable(x._arrow_array.chunks
                                                    for x in to_concat))
        return cls(pa.chunked_array(chunks))