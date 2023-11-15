def get_content_languages():
    """
    Cache of settings.WAGTAIL_CONTENT_LANGUAGES in a dictionary for easy lookups by key.
    """
    content_languages = getattr(settings, 'WAGTAIL_CONTENT_LANGUAGES', None)
    languages = dict(settings.LANGUAGES)

    if content_languages is None:
        # Default to a single language based on LANGUAGE_CODE
        default_language_code = get_supported_language_variant(settings.LANGUAGE_CODE)
        try:
            language_name = languages[default_language_code]
        except KeyError:
            # get_supported_language_variant on the 'null' translation backend (used for
            # USE_I18N=False) returns settings.LANGUAGE_CODE unchanged without accounting for
            # language variants (en-us versus en), so retry with the generic version.
            default_language_code = default_language_code.split("-")[0]
            try:
                language_name = languages[default_language_code]
            except KeyError:
                # Can't extract a display name, so fall back on displaying LANGUAGE_CODE instead
                language_name = settings.LANGUAGE_CODE
                # Also need to tweak the languages dict to get around the check below
                languages[default_language_code] = settings.LANGUAGE_CODE

        content_languages = [
            (default_language_code, language_name),
        ]

    # Check that each content language is in LANGUAGES
    for language_code, name in content_languages:
        if language_code not in languages:
            raise ImproperlyConfigured(
                "The language {} is specified in WAGTAIL_CONTENT_LANGUAGES but not LANGUAGES. "
                "WAGTAIL_CONTENT_LANGUAGES must be a subset of LANGUAGES.".format(language_code)
            )

    return dict(content_languages)