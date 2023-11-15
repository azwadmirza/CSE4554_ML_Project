    def __new__(cls, car, cdr):
        if isinstance(cdr, list):

            # Keep unquotes in the cdr of conses
            if type(cdr) == HyExpression:
                if len(cdr) > 0 and type(cdr[0]) == HySymbol:
                    if cdr[0] in ("unquote", "unquote-splice"):
                        return super(HyCons, cls).__new__(cls)

            return cdr.__class__([wrap_value(car)] + cdr)

        elif cdr is None:
            return HyExpression([wrap_value(car)])

        else:
            return super(HyCons, cls).__new__(cls)