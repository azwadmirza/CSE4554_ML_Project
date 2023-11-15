def load_messages(themes, translations, default_lang):
    """ Load theme's messages into context.

    All the messages from parent themes are loaded,
    and "younger" themes have priority.
    """
    messages = Functionary(dict, default_lang)
    oldpath = sys.path[:]
    for theme_name in themes[::-1]:
        msg_folder = os.path.join(get_theme_path(theme_name), 'messages')
        default_folder = os.path.join(get_theme_path('base'), 'messages')
        sys.path.insert(0, default_folder)
        sys.path.insert(0, msg_folder)
        english = __import__('messages_en')
        for lang in list(translations.keys()):
            try:
                translation = __import__('messages_' + lang)
                # If we don't do the reload, the module is cached
                reload(translation)
                if sorted(translation.MESSAGES.keys()) !=\
                        sorted(english.MESSAGES.keys()) and \
                        lang not in warned:
                    warned.append(lang)
                    LOGGER.warn("Incomplete translation for language "
                                "'{0}'.".format(lang))
                messages[lang].update(english.MESSAGES)
                for k, v in translation.MESSAGES.items():
                    if v:
                        messages[lang][k] = v
                del(translation)
            except ImportError as orig:
                raise LanguageNotFoundError(lang, orig)
    sys.path = oldpath
    return messages