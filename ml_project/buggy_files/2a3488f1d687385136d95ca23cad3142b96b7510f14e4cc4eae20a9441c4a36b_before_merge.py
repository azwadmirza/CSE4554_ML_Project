def _get_translations():
    translation_locale = request.form.get('use-translation')
    if translation_locale:
        babel_ext = flask_babel.current_app.extensions['babel']
        translation = Translations.load(next(babel_ext.translation_directories), 'oc')
    else:
        translation = _flask_babel_get_translations()
    return translation