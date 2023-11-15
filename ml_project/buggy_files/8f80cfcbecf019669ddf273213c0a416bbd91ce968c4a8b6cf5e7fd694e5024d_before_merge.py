    def get(cls, language):
        try:
            if PYCOUNTRY:
                # lookup workaround for alpha_2 language codes
                lang = languages.get(alpha_2=language) if re.match(r"^[a-z]{2}$", language) else languages.lookup(language)
                return Language(lang.alpha_2, lang.alpha_3, lang.name, getattr(lang, "bibliographic", None))
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