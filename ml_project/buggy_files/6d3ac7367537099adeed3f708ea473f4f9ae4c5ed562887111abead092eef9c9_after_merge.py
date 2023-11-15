    def _component_data_iter(self, ctype=None, active=None, sort=False):
        """
        Generator that returns a 3-tuple of (component name, index value,
        and _ComponentData) for every component data in the block.
        """
        _sort_indices = SortComponents.sort_indices(sort)
        _subcomp = PseudoMap(self, ctype, active, sort)
        for name, comp in _subcomp.iteritems():
            # NOTE: Suffix has a dict interface (something other derived
            #   non-indexed Components may do as well), so we don't want
            #   to test the existence of iteritems as a check for
            #   component datas. We will rely on is_indexed() to catch
            #   all the indexed components.  Then we will do special
            #   processing for the scalar components to catch the case
            #   where there are "sparse scalar components"
            if comp.is_indexed():
                _items = comp.iteritems()
            elif hasattr(comp, '_data'):
                # This may be an empty Scalar component (e.g., from
                # Constraint.Skip on a scalar Constraint)
                assert len(comp._data) <= 1
                _items = iteritems(comp._data)
            else:
                _items = ((None, comp),)

            if _sort_indices:
                _items = sorted(_items, key=itemgetter(0))
            if active is None or not isinstance(comp, ActiveIndexedComponent):
                for idx, compData in _items:
                    yield (name, idx), compData
            else:
                for idx, compData in _items:
                    if compData.active == active:
                        yield (name, idx), compData