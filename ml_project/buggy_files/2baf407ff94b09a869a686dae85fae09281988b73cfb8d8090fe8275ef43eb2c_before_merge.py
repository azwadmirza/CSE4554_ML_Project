    def _match(target, pattern, regex_match=False, exact_match=False):
        if regex_match:
            try:
                return re.match(pattern.lower(), six.text_type(target).lower())
            except Exception:
                log.error('Invalid regex \'%s\' in match', pattern)
                return False
        elif exact_match:
            return six.text_type(target).lower() == pattern.lower()
        else:
            return fnmatch.fnmatch(six.text_type(target).lower(), pattern.lower())