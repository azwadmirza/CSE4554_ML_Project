def iter_windows(texts, window_size, copy=False, ignore_below_size=True, include_doc_num=False):
    """Produce a generator over the given texts using a sliding window of `window_size`.
    The windows produced are views of some subsequence of a text. To use deep copies
    instead, pass `copy=True`.

    Args:
        texts: List of string sentences.
        window_size: Size of sliding window.
        copy: False to use views of the texts (default) or True to produce deep copies.
        ignore_below_size: ignore documents that are not at least `window_size` in length (default behavior).
            If False, the documents below `window_size` will be yielded as the full document.

    """
    for doc_num, document in enumerate(texts):
        for window in _iter_windows(document, window_size, copy, ignore_below_size):
            if include_doc_num:
                yield (doc_num, window)
            else:
                yield window