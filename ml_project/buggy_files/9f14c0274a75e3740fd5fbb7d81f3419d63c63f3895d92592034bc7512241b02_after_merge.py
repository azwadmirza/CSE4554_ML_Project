    def add_component(self, name, val):
        """
        Add a component 'name' to the block.

        This method assumes that the attribute is not in the model.
        """
        #
        # Error checks
        #
        if not val.valid_model_component():
            raise RuntimeError(
                "Cannot add '%s' as a component to a block" % str(type(val)))
        if name in self._Block_reserved_words and hasattr(self, name):
            raise ValueError("Attempting to declare a block component using "
                             "the name of a reserved attribute:\n\t%s"
                             % (name,))
        if name in self.__dict__:
            raise RuntimeError(
                "Cannot add component '%s' (type %s) to block '%s': a "
                "component by that name (type %s) is already defined."
                % (name, type(val), self.name, type(getattr(self, name))))
        #
        # Skip the add_component() logic if this is a
        # component type that is suppressed.
        #
        _component = self.parent_component()
        _type = val.type()
        if _type in _component._suppress_ctypes:
            return
        #
        # Raise an exception if the component already has a parent.
        #
        if (val._parent is not None) and (val._parent() is not None):
            if val._parent() is self:
                msg = """
Attempting to re-assign the component '%s' to the same
block under a different name (%s).""" % (val.name, name)
            else:
                msg = """
Re-assigning the component '%s' from block '%s' to
block '%s' as '%s'.""" % (val._name, val._parent().name,
                          self.name, name)

            raise RuntimeError("""%s

This behavior is not supported by Pyomo; components must have a
single owning block (or model), and a component may not appear
multiple times in a block.  If you want to re-name or move this
component, use the block del_component() and add_component() methods.
""" % (msg.strip(),))
        #
        # If the new component is a Block, then there is the chance that
        # it is the model(), and assigning it would create a circular
        # hierarchy.  Note that we only have to check the model as the
        # check immediately above would catch any "internal" blocks in
        # the block hierarchy
        #
        if isinstance(val, Block) and val is self.model():
            raise ValueError(
                "Cannot assign the top-level block as a subblock of one of "
                "its children (%s): creates a circular hierarchy"
                % (self,))
        #
        # Set the name and parent pointer of this component.
        #
        val._name = name
        val._parent = weakref.ref(self)
        #
        # We want to add the temporary / implicit sets first so that
        # they get constructed before this component
        #
        # FIXME: This is sloppy and wasteful (most components trigger
        # this, even when there is no need for it).  We should
        # reconsider the whole _implicit_subsets logic to defer this
        # kind of thing to an "update_parent()" method on the
        # components.
        #
        if hasattr(val, '_index'):
            self._add_temporary_set(val)
        #
        # Add the component to the underlying Component store
        #
        _new_idx = len(self._decl_order)
        self._decl[name] = _new_idx
        self._decl_order.append((val, None))
        #
        # Add the component as an attribute.  Note that
        #
        #     self.__dict__[name]=val
        #
        # is inappropriate here.  The correct way to add the attribute
        # is to delegate the work to the next class up the MRO.
        #
        super(_BlockData, self).__setattr__(name, val)
        #
        # Update the ctype linked lists
        #
        if _type in self._ctypes:
            idx_info = self._ctypes[_type]
            tmp = idx_info[1]
            self._decl_order[tmp] = (self._decl_order[tmp][0], _new_idx)
            idx_info[1] = _new_idx
            idx_info[2] += 1
        else:
            self._ctypes[_type] = [_new_idx, _new_idx, 1]
        #
        # Propagate properties to sub-blocks:
        #   suppressed ctypes
        #
        if _type is Block:
            val._suppress_ctypes |= _component._suppress_ctypes
        #
        # Error, for disabled support implicit rule names
        #
        if '_rule' in val.__dict__ and val._rule is None:
            _found = False
            try:
                _test = val.local_name + '_rule'
                for i in (1, 2):
                    frame = sys._getframe(i)
                    _found |= _test in frame.f_locals
            except:
                pass
            if _found:
                # JDS: Do not blindly reformat this message.  The
                # formatter inserts arbitrarily-long names(), which can
                # cause the resulting logged message to be very poorly
                # formatted due to long lines.
                logger.warning(
                    """As of Pyomo 4.0, Pyomo components no longer support implicit rules.
You defined a component (%s) that appears
to rely on an implicit rule (%s).
Components must now specify their rules explicitly using 'rule=' keywords.""" %
                    (val.name, _test))
        #
        # Don't reconstruct if this component has already been constructed.
        # This allows a user to move a component from one block to
        # another.
        #
        if val._constructed is True:
            return
        #
        # If the block is Concrete, construct the component
        # Note: we are explicitly using getattr because (Scalar)
        #   classes that derive from Block may want to declare components
        #   within their __init__() [notably, pyomo.gdp's Disjunct).
        #   Those components are added *before* the _constructed flag is
        #   added to the class by Block.__init__()
        #
        if getattr(_component, '_constructed', False):
            # NB: we don't have to construct the temporary / implicit
            # sets here: if necessary, that happens when
            # _add_temporary_set() calls add_component().
            if id(self) in _BlockConstruction.data:
                data = _BlockConstruction.data[id(self)].get(name, None)
            else:
                data = None
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                # This is tricky: If we are in the middle of
                # constructing an indexed block, the block component
                # already has _constructed=True.  Now, if the
                # _BlockData.__init__() defines any local variables
                # (like pyomo.gdp.Disjunct's indicator_var), name(True)
                # will fail: this block data exists and has a parent(),
                # but it has not yet been added to the parent's _data
                # (so the idx lookup will fail in name).
                if self.parent_block() is None:
                    _blockName = "[Model]"
                else:
                    try:
                        _blockName = "Block '%s'" % self.name
                    except:
                        _blockName = "Block '%s[...]'" \
                            % self.parent_component().name
                logger.debug("Constructing %s '%s' on %s from data=%s",
                             val.__class__.__name__, val.name,
                             _blockName, str(data))
            try:
                val.construct(data)
            except:
                err = sys.exc_info()[1]
                logger.error(
                    "Constructing component '%s' from data=%s failed:\n%s: %s",
                    str(val.name), str(data).strip(),
                    type(err).__name__, err)
                raise
            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                if _blockName[-1] == "'":
                    _blockName = _blockName[:-1] + '.' + val.name + "'"
                else:
                    _blockName = "'" + _blockName + '.' + val.name + "'"
                _out = StringIO()
                val.pprint(ostream=_out)
                logger.debug("Constructed component '%s':\n%s"
                             % (_blockName, _out.getvalue()))