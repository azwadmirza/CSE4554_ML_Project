    def _message(self, as_unicode=compat.py3k):
        # rules:
        #
        # 1. under py2k, for __str__ return single string arg as it was
        # given without converting to unicode.  for __unicode__
        # do a conversion but check that it's not unicode already just in
        # case
        #
        # 2. under py3k, single arg string will usually be a unicode
        # object, but since __str__() must return unicode, check for
        # bytestring just in case
        #
        # 3. for multiple self.args, this is not a case in current
        # SQLAlchemy though this is happening in at least one known external
        # library, call str() which does a repr().
        #
        if len(self.args) == 1:
            text = self.args[0]
            if as_unicode and isinstance(text, compat.binary_types):
                return compat.decode_backslashreplace(text, "utf-8")
            else:
                return self.args[0]
        else:
            # this is not a normal case within SQLAlchemy but is here for
            # compatibility with Exception.args - the str() comes out as
            # a repr() of the tuple
            return str(self.args)