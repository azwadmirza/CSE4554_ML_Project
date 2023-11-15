    def get_valtype(x):
        if not in_py2:
            return PersonName(x, encodings).decode()
        return PersonName(x, encodings)