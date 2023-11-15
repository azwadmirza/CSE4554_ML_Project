    def decode_stdout(self, stdout):
        fallback_encoding = self.savvy_settings.get("fallback_encoding")
        silent_fallback = self.savvy_settings.get("silent_fallback")
        try:
            return stdout.decode()
        except UnicodeDecodeError as unicode_err:
            try:
                return stdout.decode("latin-1")
            except UnicodeDecodeError as unicode_err:
                if silent_fallback or sublime.ok_cancel_dialog(UTF8_PARSE_ERROR_MSG, "Fallback?"):
                    try:
                        return stdout.decode(fallback_encoding)
                    except UnicodeDecodeError as fallback_err:
                        sublime.error_message(FALLBACK_PARSE_ERROR_MSG)
                        raise fallback_err
                raise unicode_err