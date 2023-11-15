                def detect_su_prompt(b_data):
                    b_SU_PROMPT_LOCALIZATIONS_RE = re.compile(b"|".join([b'(\w+\'s )?' + x + b' ?: ?' for x in b_SU_PROMPT_LOCALIZATIONS]), flags=re.IGNORECASE)
                    return bool(b_SU_PROMPT_LOCALIZATIONS_RE.match(b_data))