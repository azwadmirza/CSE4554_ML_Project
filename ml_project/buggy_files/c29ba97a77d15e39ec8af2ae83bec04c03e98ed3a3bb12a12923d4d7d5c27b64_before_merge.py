  def __hash__(self):
    # TODO(mattjj): this is not semantically correct because it is possible
    # __eq__ is true for values with unequal __hash__ values. However, the
    # main use case at the moment is memoization for which false negatives are
    # fine.
    return id(self)