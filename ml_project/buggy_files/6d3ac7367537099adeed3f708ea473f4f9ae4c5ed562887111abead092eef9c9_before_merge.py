    def _component_data_iter(self, ctype=None, active=None, sort=False):
        """
        Generator that returns a 3-tuple of (component name, index value,
        and _ComponentData) for every component data in the block.
        """
        _sort_indices = SortComponents.sort_indices(sort)
        _subcomp = PseudoMap(self, ctype, active, sort)
        for name, comp in _subcomp.iteritems():
            # _NOTE_: Suffix has a dict interface (something other
            #         derived non-indexed Components may do as well),
            #         so we don't want to test the existence of
            #         iteritems as a check for components. Also,
            #         the case where we test len(comp) after seeing
            #         that comp.is_indexed is False is a hack for a
            #         SimpleConstraint whose expression resolved to
            #         Constraint.skip or Constraint.feasible (in which
            #         case its data is empty and iteritems would have
            #         been empty as well)
            # try:
            #    _items = comp.iteritems()
            # except AttributeError:
            #    _items = [ (None, comp) ]
            if comp.is_indexed():
                _items = comp.iteritems()
            # This is a hack (see _NOTE_ above).
            elif len(comp) or not hasattr(comp, '_data'):
                _items = ((None, comp),)
            else:
                _items = tuple()

            if _sort_indices:
                _items = sorted(_items, key=itemgetter(0))
            if active is None or not isinstance(comp, ActiveIndexedComponent):
                for idx, compData in _items:
                    yield (name, idx), compData
            else:
                for idx, compData in _items:
                    if compData.active == active:
                        yield (name, idx), compData