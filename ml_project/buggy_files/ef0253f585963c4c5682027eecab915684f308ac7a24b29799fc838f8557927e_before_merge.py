def _pud_tagger():
    global _PUD_TAGGER
    if not _PUD_TAGGER:
        with open(_PUD_PATH, "rb") as fh:
            _PUD_TAGGER = pickle.load(fh)
    return _PUD_TAGGER