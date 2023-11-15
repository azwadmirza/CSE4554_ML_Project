                def detect_su_prompt(data):
                    SU_PROMPT_LOCALIZATIONS_RE = re.compile("|".join(['(\w+\'s )?' + x + ' ?: ?' for x in SU_PROMPT_LOCALIZATIONS]), flags=re.IGNORECASE)
                    return bool(SU_PROMPT_LOCALIZATIONS_RE.match(data))