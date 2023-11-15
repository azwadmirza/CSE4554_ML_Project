    def _match(target, pattern, regex_match=False, exact_match=False):
        # The reason for using six.text_type first and _then_ using
        # to_unicode as a fallback is because we want to eventually have
        # unicode types for comparison below. If either value is numeric then
        # six.text_type will turn it into a unicode string. However, if the
        # value is a PY2 str type with non-ascii chars, then the result will be
        # a UnicodeDecodeError. In those cases, we simply use to_unicode to
        # decode it to unicode. The reason we can't simply use to_unicode to
        # begin with is that (by design) to_unicode will raise a TypeError if a
        # non-string/bytestring/bytearray value is passed.
        try:
            target = six.text_type(target).lower()
        except UnicodeDecodeError:
            target = salt.utils.stringutils.to_unicode(target).lower()
        try:
            pattern = six.text_type(pattern).lower()
        except UnicodeDecodeError:
            pattern = salt.utils.stringutils.to_unicode(pattern).lower()

        if regex_match:
            try:
                return re.match(pattern, target)
            except Exception:
                log.error('Invalid regex \'%s\' in match', pattern)
                return False
        else:
            return target == pattern if exact_match \
                else fnmatch.fnmatch(target, pattern)