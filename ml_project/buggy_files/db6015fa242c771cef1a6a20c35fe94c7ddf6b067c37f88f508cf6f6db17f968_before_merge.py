    def __init__(self):
        if self.parent is not None:
            # All _DrawValuesContext instances that are in the context of
            # another _DrawValuesContext will share the reference to the
            # drawn_vars dictionary. This means that separate branches
            # in the nested _DrawValuesContext context tree will see the
            # same drawn values
            self.drawn_vars = self.parent.drawn_vars
        else:
            self.drawn_vars = dict()