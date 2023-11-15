    def __init__(self, *objs):
        self.locals = {}
        self.objs = list(objs) + [self.locals]