def _orchid_tagger():
    global _ORCHID_TAGGER
    if not _ORCHID_TAGGER:
        with open(_ORCHID_PATH, "rb") as fh:
            _ORCHID_TAGGER = pickle.load(fh)
    return _ORCHID_TAGGER