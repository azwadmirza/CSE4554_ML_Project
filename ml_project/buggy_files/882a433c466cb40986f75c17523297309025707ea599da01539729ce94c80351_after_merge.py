def setup_gettext(language=None):
    languages = [language] if language else None
    if not [key for key in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG') if os.environ.get(key)]:
        os.environ['LC_MESSAGES'] = 'en_US.UTF-8'
    print(locale_dir())
    gt = gettext.translation('messages', locale_dir(), languages=languages, fallback=True)
    gt.install(names=["ngettext"])