    def get(cls, language):
        try:
            if PYCOUNTRY:
                lang = (languages.get(alpha_2=language)
                        or languages.get(alpha_3=language)
                        or languages.get(bibliographic=language)
                        or languages.get(name=language))
                if not lang:
                    raise KeyError(language)
                return Language(
                    # some languages don't have an alpha_2 code
                    getattr(lang, "alpha_2", ""),
                    lang.alpha_3,
                    lang.name,
                    getattr(lang, "bibliographic", "")
                )
            else:
                lang = None
                if len(language) == 2:
                    lang = languages.get(alpha2=language)
                elif len(language) == 3:
                    for code_type in ['part2b', 'part2t', 'part3']:
                        try:
                            lang = languages.get(**{code_type: language})
                            break
                        except KeyError:
                            pass
                    if not lang:
                        raise KeyError(language)
                else:
                    raise KeyError(language)
                return Language(lang.alpha2, lang.part3, lang.name, lang.part2b or lang.part2t)
        except (LookupError, KeyError):
            raise LookupError("Invalid language code: {0}".format(language))