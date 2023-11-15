def factorial_notation(tokens, local_dict, global_dict):
    """Allows standard notation for factorial."""
    result = []
    prevtoken = ''
    for toknum, tokval in tokens:
        if toknum == OP:
            op = tokval

            if op == '!!':
                if prevtoken == '!' or prevtoken == '!!':
                    raise TokenError
                result = _add_factorial_tokens('factorial2', result)
            elif op == '!':
                if prevtoken == '!' or prevtoken == '!!':
                    raise TokenError
                result = _add_factorial_tokens('factorial', result)
            else:
                result.append((OP, op))
        else:
            result.append((toknum, tokval))

        prevtoken = tokval

    return result