    def __init__(self, variable, context, types, assignment=False, **kwds):
        super(PromotionType, self).__init__(variable, **kwds)
        self.context = context
        self.types = oset.OrderedSet(types)
        self.assignment = assignment
        variable.type = self

        self.add_parents(type for type in types if type.is_unresolved)

        self.count = PromotionType.count
        PromotionType.count += 1