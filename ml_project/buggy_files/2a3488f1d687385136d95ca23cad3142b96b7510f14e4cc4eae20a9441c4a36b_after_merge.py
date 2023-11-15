def _get_translations():
    if has_request_context() and request.form.get('use-translation') == 'oc':
        babel_ext = flask_babel.current_app.extensions['babel']
        return Translations.load(next(babel_ext.translation_directories), 'oc')

    return _flask_babel_get_translations()