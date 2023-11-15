    def _transform_block_components(self, block, disjunct, bigM, suffix_list):
        # We first need to find any transformed disjunctions that might be here
        # because we need to move their transformation blocks up onto the parent
        # block before we transform anything else on this block 
        destinationBlock = disjunct._transformation_block().parent_block()
        for obj in block.component_data_objects(
                Disjunction, 
                sort=SortComponents.deterministic, 
                descend_into=(Block)):
            print(obj)
            if not obj.algebraic_constraint:
                # This could be bad if it's active, but we'll wait to yell
                # until the next loop
                continue
            disjParentBlock = disjunct.parent_block()
            # get this disjunction's relaxation block.
            transBlock = None
            for d in obj.disjuncts:
                if d._transformation_block:
                    transBlock = d._transformation_block().parent_block()
            if transBlock is None:
                raise GDP_Error(
                    "Found transformed disjunction %s on disjunt %s, "
                    "but none of its disjuncts have been transformed. "
                    "This is very strange if not impossible" % (obj.name,
                                                                disjunct.name))
            # move transBlock up to parent component
            transBlock.parent_block().del_component(transBlock)
            self._transfer_transBlock_data(transBlock, destinationBlock)

        # Now look through the component map of block and transform
        # everything we have a handler for. Yell if we don't know how
        # to handle it.
        for name, obj in list(iteritems(block.component_map())):
            if hasattr(obj, 'active') and not obj.active:
                continue
            handler = self.handlers.get(obj.type(), None)
            if not handler:
                if handler is None:
                    raise GDP_Error(
                        "No BigM transformation handler registered "
                        "for modeling components of type %s. If your " 
                        "disjuncts contain non-GDP Pyomo components that "
                        "require transformation, please transform them first."
                        % obj.type())
                continue
            # obj is what we are transforming, we pass disjunct
            # through so that we will have access to the indicator
            # variables down the line.
            handler(obj, disjunct, bigM, suffix_list)