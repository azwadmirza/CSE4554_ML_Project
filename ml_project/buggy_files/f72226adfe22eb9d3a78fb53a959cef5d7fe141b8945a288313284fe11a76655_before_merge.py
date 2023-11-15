    def __deepcopy__(self, memo):
        # The problem we are addressing is when we want to clone a
        # sub-block in a model.  In that case, the block can have
        # references to both child components and to external
        # ComponentData (mostly through expressions pointing to Vars
        # and Params outside this block).  For everything stored beneath
        # this block, we want to clone the Component (and all
        # corresponding ComponentData objects).  But for everything
        # stored outside this Block, we want to do a simple shallow
        # copy.
        #
        # Nominally, expressions only point to ComponentData
        # derivatives.  However, with the development of Expression
        # Templates (and the corresponding _GetItemExpression object),
        # expressions can refer to container (non-Simple) components, so
        # we need to override __deepcopy__ for both Component and
        # ComponentData.

        #try:
        #    print("Component: %s" % (self.name,))
        #except:
        #    print("DANGLING ComponentData: %s on %s" % (
        #        type(self),self.parent_component()))

        # Note: there is an edge case when cloning a block: the initial
        # call to deepcopy (on the target block) has __block_scope__
        # defined, however, the parent block of self is either None, or
        # is (by definition) out of scope.  So we will check that
        # id(self) is not in __block_scope__: if it is, then this is the
        # top-level block and we need to do the normal deepcopy.
        if '__block_scope__' in memo and \
                id(self) not in memo['__block_scope__']:
            _known = memo['__block_scope__']
            _new = []
            tmp = self.parent_block()
            tmpId = id(tmp)
            # Note: normally we would need to check that tmp does not
            # end up being None.  However, since clone() inserts
            # id(None) into the __block_scope__ dictionary, we are safe
            while tmpId not in _known:
                _new.append(tmpId)
                tmp = tmp.parent_block()
                tmpId = id(tmp)

            # Remember whether all newly-encountered blocks are in or
            # out of scope (prevent duplicate work)
            for _id in _new:
                _known[_id] = _known[tmpId]

            if not _known[tmpId]:
                # component is out-of-scope.  shallow copy only
                ans = memo[id(self)] = self
                return ans

        #
        # There is a particularly subtle bug with 'uncopyable'
        # attributes: if the exception is thrown while copying a complex
        # data structure, we can be in a state where objects have been
        # created and assigned to the memo in the try block, but they
        # haven't had their state set yet.  When the exception moves us
        # into the except block, we need to effectively "undo" those
        # partially copied classes.  The only way is to restore the memo
        # to the state it was in before we started.  Right now, our
        # solution is to make a (shallow) copy of the memo before each
        # operation and restoring it in the case of exception.
        # Unfortunately that is a lot of usually unnecessary work.
        # Since *most* classes are copyable, we will avoid that
        # "paranoia" unless the naive clone generated an error - in
        # which case Block.clone() will switch over to the more
        # "paranoid" mode.
        #
        paranoid = memo.get('__paranoid__', None)

        ans = memo[id(self)] = self.__class__.__new__(self.__class__)
        # We can't do the "obvious", since this is a (partially)
        # slot-ized class and the __dict__ structure is
        # nonauthoritative:
        #
        # for key, val in self.__dict__.iteritems():
        #     object.__setattr__(ans, key, deepcopy(val, memo))
        #
        # Further, __slots__ is also nonauthoritative (this may be a
        # singleton component -- in which case it also has a __dict__).
        # Plus, as this may be a derived class with several layers of
        # slots.  So, we will resort to partially "pickling" the object,
        # deepcopying the state dict, and then restoring the copy into
        # the new instance.
        #
        # [JDS 7/7/14] I worry about the efficiency of using both
        # getstate/setstate *and* deepcopy, but we need deepcopy to
        # update the _parent refs appropriately, and since this is a
        # slot-ized class, we cannot overwrite the __deepcopy__
        # attribute to prevent infinite recursion.
        state = self.__getstate__()
        try:
            if paranoid:
                saved_memo = dict(memo)
            new_state = deepcopy(state, memo)
        except:
            if paranoid:
                # Note: memo is intentionally pass-by-reference.  We
                # need to clear and reset the object we were handed (and
                # not overwrite it)
                memo.clear()
                memo.update(saved_memo)
            elif paranoid is not None:
                raise PickleError()
            new_state = {}
            for k,v in iteritems(state):
                try:
                    if paranoid:
                        saved_memo = dict(memo)
                    new_state[k] = deepcopy(v, memo)
                except:
                    if paranoid:
                        memo.clear()
                        memo.update(saved_memo)
                    elif paranoid is None:
                        logger.warning("""
                            Uncopyable field encountered when deep
                            copying outside the scope of Block.clone().
                            There is a distinct possibility that the new
                            copy is not complete.  To avoid this
                            situation, either use Block.clone() or set
                            'paranoid' mode by adding '__paranoid__' ==
                            True to the memo before calling
                            copy.deepcopy.""")
                    logger.error(
                        "Unable to clone Pyomo component attribute.\n"
                        "Component '%s' contains an uncopyable field '%s' (%s)"
                        % ( self.name, k, type(v) ))
        ans.__setstate__(new_state)
        return ans