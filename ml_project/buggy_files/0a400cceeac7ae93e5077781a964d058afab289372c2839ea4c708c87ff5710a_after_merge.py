    def get_tokens(self, cli, width):
        result = []
        append = result.append
        Signature = Token.Toolbar.Signature

        if cli.line.signatures:
            sig = cli.line.signatures[0]  # Always take the first one.

            append((Token, '           '))
            try:
                append((Signature, sig.full_name))
            except IndexError:
                # Workaround for #37: https://github.com/jonathanslenders/python-prompt-toolkit/issues/37
                # See also: https://github.com/davidhalter/jedi/issues/490
                return []

            append((Signature.Operator, '('))

            for i, p in enumerate(sig.params):
                if i == sig.index:
                    append((Signature.CurrentName, str(p.name)))
                else:
                    append((Signature, str(p.name)))
                append((Signature.Operator, ', '))

            result.pop()  # Pop last comma
            append((Signature.Operator, ')'))
        return result