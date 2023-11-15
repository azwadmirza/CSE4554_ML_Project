    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.step:
                raise TypeError("Resources fix the subject for slicing, and can only be sliced by predicate/object. ")
            p,o=item.start,item.stop
            if p is None and o is None:
                return self.predicate_objects()
            elif p is None:
                return self.predicates(o)
            elif o is None:
                return self.objects(p)
            else:
                return (self.identifier, p, o) in self._graph
        elif isinstance(item, (Node, Path)):
            return self.objects(item)
        else:
            raise TypeError("You can only index a resource by a single rdflib term, a slice of rdflib terms, not %s (%s)"%(item, type(item)))