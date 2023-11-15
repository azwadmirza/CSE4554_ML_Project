def signature_toolbar(python_input):
    """
    Return the `Layout` for the signature.
    """
    def get_tokens(cli):
        result = []
        append = result.append
        Signature = Token.Toolbar.Signature

        if python_input.signatures:
            sig = python_input.signatures[0]  # Always take the first one.

            append((Signature, ' '))
            try:
                append((Signature, sig.full_name))
            except IndexError:
                # Workaround for #37: https://github.com/jonathanslenders/python-prompt-toolkit/issues/37
                # See also: https://github.com/davidhalter/jedi/issues/490
                return []

            append((Signature.Operator, '('))

            try:
                enumerated_params = enumerate(sig.params)
            except AttributeError:
                # Workaround for #136: https://github.com/jonathanslenders/ptpython/issues/136
                # AttributeError: 'Lambda' object has no attribute 'get_subscope_by_name'
                return []

            for i, p in enumerated_params:
                # Workaround for #47: 'p' is None when we hit the '*' in the signature.
                #                     and sig has no 'index' attribute.
                # See: https://github.com/jonathanslenders/ptpython/issues/47
                #      https://github.com/davidhalter/jedi/issues/598
                description = (p.description if p else '*') #or '*'
                sig_index = getattr(sig, 'index', 0)

                if i == sig_index:
                    # Note: we use `_Param.description` instead of
                    #       `_Param.name`, that way we also get the '*' before args.
                    append((Signature.CurrentName, str(description)))
                else:
                    append((Signature, str(description)))
                append((Signature.Operator, ', '))

            if sig.params:
                # Pop last comma
                result.pop()

            append((Signature.Operator, ')'))
            append((Signature, ' '))
        return result

    return ConditionalContainer(
        content=Window(
            TokenListControl(get_tokens),
            height=LayoutDimension.exact(1)),
        filter=
            # Show only when there is a signature
            HasSignature(python_input) &
            # And there are no completions to be shown. (would cover signature pop-up.)
            ~(HasCompletions() & (show_completions_menu(python_input) |
                                   show_multi_column_completions_menu(python_input)))
            # Signature needs to be shown.
            & ShowSignature(python_input) &
            # Not done yet.
            ~IsDone())