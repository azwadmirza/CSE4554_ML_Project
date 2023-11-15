async def _get_all_intents(skills):
    """Get all skill intents and concatenate into a single markdown string."""
    matchers = [matcher for skill in skills for matcher in skill.matchers]
    intents = [matcher["intents"] for matcher in matchers
               if matcher["intents"] is not None]
    if not intents:
        return None
    intents = "\n\n".join(intents)
    return unicodedata.normalize("NFKD", intents).encode('ascii')