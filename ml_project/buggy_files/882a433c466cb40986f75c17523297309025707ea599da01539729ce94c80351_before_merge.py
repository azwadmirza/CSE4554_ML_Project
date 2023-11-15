def setup_gettext(language=None):
    languages = [language] if language else None
    if not [key for key in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG') if key in os.environ]:
        os.environ['LC_MESSAGES'] = 'en_US.UTF-8'
    gt = gettext.translation('messages', locale_dir(), languages=languages)
    gt.install(names=["ngettext"])