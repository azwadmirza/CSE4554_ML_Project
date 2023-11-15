    def construct(self, data=None):
        """
        Initialize the block
        """
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("Constructing %s '%s', from data=%s",
                         self.__class__.__name__, self.name, str(data))
        if self._constructed:
            return
        timer = ConstructionTimer(self)
        self._constructed = True

        # We must check that any pre-existing components are
        # constructed.  This catches the case where someone is building
        # a Concrete model by building (potentially pseudo-abstract)
        # sub-blocks and then adding them to a Concrete model block.
        for idx in self._data:
            _block = self[idx]
            for name, obj in iteritems(_block.component_map()):
                if not obj._constructed:
                    if data is None:
                        _data = None
                    else:
                        _data = data.get(name, None)
                    obj.construct(_data)

        if self._rule is None:
            # Ensure the _data dictionary is populated for singleton
            # blocks
            if not self.is_indexed():
                self[None]
            timer.report()
            return
        # If we have a rule, fire the rule for all indices.
        # Notes:
        #  - Since this block is now concrete, any components added to
        #    it will be immediately constructed by
        #    block.add_component().
        #  - Since the rule does not pass any "data" on, we build a
        #    scalar "stack" of pointers to block data
        #    (_BlockConstruction.data) that the individual blocks'
        #    add_component() can refer back to to handle component
        #    construction.
        for idx in self._index:
            _block = self[idx]
            if data is not None and idx in data:
                _BlockConstruction.data[id(_block)] = data[idx]
            obj = apply_indexed_rule(
                self, self._rule, _block, idx, self._options)
            if id(_block) in _BlockConstruction.data:
                del _BlockConstruction.data[id(_block)]

            if isinstance(obj, _BlockData) and obj is not _block:
                # If the user returns a block, use their block instead
                # of the empty one we just created.
                for c in list(obj.component_objects(descend_into=False)):
                    obj.del_component(c)
                    _block.add_component(c.local_name, c)
                # transfer over any other attributes that are not components
                for name, val in iteritems(obj.__dict__):
                    if not hasattr(_block, name) and not hasattr(self, name):
                        super(_BlockData, _block).__setattr__(name, val)

            # TBD: Should we allow skipping Blocks???
            # if obj is Block.Skip and idx is not None:
            #   del self._data[idx]
        timer.report()