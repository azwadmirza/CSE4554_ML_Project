    def _transfer_transBlock_data(self, fromBlock, toBlock):
        # We know that we have a list of transformed disjuncts on both. We need
        # to move those over. Then there might be constraints on the block also
        # (at this point only the diaggregation constraints from chull,
        # but... I'll leave it general for now.
        disjunctList = toBlock.relaxedDisjuncts
        for idx, disjunctBlock in iteritems(fromBlock.relaxedDisjuncts):
            # I think this should work when #1106 is resolved:
            # disjunctList[len(disjunctList)] = disjunctBlock
            # newblock = disjunctList[len(disjunctList)-1]

            # HACK in the meantime:
            newblock = disjunctList[len(disjunctList)]
            self._copy_to_block(disjunctBlock, newblock)

            # update the mappings
            original = disjunctBlock._srcDisjunct()
            original._transformation_block = weakref_ref(newblock)
            newblock._srcDisjunct = weakref_ref(original)

        # move any constraints. I'm assuming they are all just on the
        # transformation block right now, because that is in our control and I
        # can't think why we would do anything messier at the moment. (And I
        # don't want to descend into Blocks because we already handled the
        # above).
        for cons in fromBlock.component_data_objects(Constraint):
            toBlock.add_component(unique_component_name(cons.name, toBlock),
                                  cons)