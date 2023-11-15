    def detect_language(lang=None, detect_fallback=True):
        """
        returns the language (if it's retrievable)
        """
        # We want to only use the 2 character version of this language
        # hence en_CA becomes en, en_US becomes en.
        if not isinstance(lang, six.string_types):
            if detect_fallback is False:
                # no detection enabled; we're done
                return None

            if hasattr(ctypes, 'windll'):
                windll = ctypes.windll.kernel32
                try:
                    lang = locale.windows_locale[
                        windll.GetUserDefaultUILanguage()]

                    # Our detected windows language
                    return lang[0:2].lower()

                except (TypeError, KeyError):
                    # Fallback to posix detection
                    pass

            try:
                # Detect language
                lang = locale.getdefaultlocale()[0]

            except TypeError:
                # None is returned if the default can't be determined
                # we're done in this case
                return None

        return None if not lang else lang[0:2].lower()