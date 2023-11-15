    def _render_quoted_form(self, form, level):
        """
        Render a quoted form as a new HyExpression.

        `level` is the level of quasiquoting of the current form. We can
        unquote if level is 0.

        Returns a three-tuple (`imports`, `expression`, `splice`).

        The `splice` return value is used to mark `unquote-splice`d forms.
        We need to distinguish them as want to concatenate them instead of
        just nesting them.
        """
        if level == 0:
            if isinstance(form, HyExpression):
                if form and form[0] in ("unquote", "unquote-splice"):
                    if len(form) != 2:
                        raise HyTypeError(form,
                                          ("`%s' needs 1 argument, got %s" %
                                           form[0], len(form) - 1))
                    return set(), form[1], (form[0] == "unquote-splice")

        if isinstance(form, HyExpression):
            if form and form[0] == "quasiquote":
                level += 1
            if form and form[0] in ("unquote", "unquote-splice"):
                level -= 1

        name = form.__class__.__name__
        imports = set([name])

        if isinstance(form, (HyList, HyDict, HySet)):
            if not form:
                contents = HyList()
            else:
                # If there are arguments, they can be spliced
                # so we build a sum...
                contents = HyExpression([HySymbol("+"), HyList()])

            for x in form:
                f_imports, f_contents, splice = self._render_quoted_form(x,
                                                                         level)
                imports.update(f_imports)
                if splice:
                    to_add = HyExpression([
                        HySymbol("list"),
                        HyExpression([HySymbol("or"), f_contents, HyList()])])
                else:
                    to_add = HyList([f_contents])

                contents.append(to_add)

            return imports, HyExpression([HySymbol(name),
                                          contents]).replace(form), False

        elif isinstance(form, HySymbol):
            return imports, HyExpression([HySymbol(name),
                                          HyString(form)]).replace(form), False

        elif isinstance(form, HyKeyword):
            return imports, form, False

        elif isinstance(form, HyString):
            x = [HySymbol(name), form]
            if form.brackets is not None:
                x.extend([HyKeyword("brackets"), form.brackets])
            return imports, HyExpression(x).replace(form), False

        return imports, HyExpression([HySymbol(name),
                                      form]).replace(form), False