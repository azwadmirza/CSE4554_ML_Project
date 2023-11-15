def paren(p):
    cont = p[1]

    # Dotted lists are expressions of the form
    # (a b c . d)
    # that evaluate to nested cons cells of the form
    # (a . (b . (c . d)))
    if len(cont) >= 3 and isinstance(cont[-2], HySymbol) and cont[-2] == ".":

        reject_spurious_dots(cont[:-2], cont[-1:])

        if len(cont) == 3:
            # Two-item dotted list: return the cons cell directly
            return HyCons(cont[0], cont[2])
        else:
            # Return a nested cons cell
            return HyCons(cont[0], paren([p[0], cont[1:], p[2]]))

    # Warn preemptively on a malformed dotted list.
    # Only check for dots after the first item to allow for a potential
    # attribute accessor shorthand
    reject_spurious_dots(cont[1:])

    return HyExpression(p[1])