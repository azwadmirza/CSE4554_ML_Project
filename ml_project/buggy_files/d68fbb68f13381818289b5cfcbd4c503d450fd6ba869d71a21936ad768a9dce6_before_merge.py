def get_translations(translate):
    res = {}
    for lang in translate:
        info = {'overview': lang.overview,
                'title': lang.title,
                'tagline': lang.tagline,
                }
        res[lang.language] = info
    return res