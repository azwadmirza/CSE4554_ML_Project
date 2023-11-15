def get_content_languages():
    """
    Cache of settings.WAGTAIL_CONTENT_LANGUAGES in a dictionary for easy lookups by key.
    """
    content_languages = getattr(settings, 'WAGTAIL_CONTENT_LANGUAGES', None)
    languages = dict(settings.LANGUAGES)

    if content_languages is None:
        # Default to a single language based on LANGUAGE_CODE
        default_language_code = get_supported_language_variant(settings.LANGUAGE_CODE)
        content_languages = [
            (default_language_code, languages[default_language_code]),
        ]

    # Check that each content language is in LANGUAGES
    for language_code, name in content_languages:
        if language_code not in languages:
            raise ImproperlyConfigured(
                "The language {} is specified in WAGTAIL_CONTENT_LANGUAGES but not LANGUAGES. "
                "WAGTAIL_CONTENT_LANGUAGES must be a subset of LANGUAGES.".format(language_code)
            )

    return dict(content_languages)