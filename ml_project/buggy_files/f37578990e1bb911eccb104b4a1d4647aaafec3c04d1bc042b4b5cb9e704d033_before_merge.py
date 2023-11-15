    def get_valtype(x):
        if not in_py2:
            if encodings:
                return PersonName(x, encodings).decode()
            return PersonName(x).decode()
        return PersonName(x)