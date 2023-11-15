    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls.__eq_operators__ = {
            n: pick_equality_operator(f.type_)
            for n, f in cls.__fields__.items()
        }
        return cls