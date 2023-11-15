        def get(key):
            result = None
            for sect in cnf:
                if sect in sections and key in cnf[sect]:
                    result = cnf[sect][key]
            # HACK: if result is a list, then ConfigObj() probably decoded from
            # string by splitting on comma, so reconstruct string by joining on
            # comma.
            if isinstance(result, list):
                result = ','.join(result)
            return result