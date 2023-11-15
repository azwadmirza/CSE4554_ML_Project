def get_translations(ident, style):
    url = get_api_url(style + 's', ident, 'translations')
    trakt_translation = TraktShowTranslation if style == 'show' else TraktMovieTranslation
    trakt_translation_id = getattr(trakt_translation, style + '_id')
    translations = []
    req_session = get_session()
    try:
        results = req_session.get(url, params={'extended': 'full,images'}).json()
        with Session() as session:
            for result in results:
                translation = session.query(trakt_translation).filter(and_(
                    trakt_translation.language == result.get('language'),
                    trakt_translation_id == ident)).first()
                if not translation:
                    translation = trakt_translation(result, session)
                translations.append(translation)
        return translations
    except requests.RequestException as e:
        log.debug('Error adding translations to trakt id %s: %s', ident, e)