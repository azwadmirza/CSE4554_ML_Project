def _update_block(blk):
    """
    This method will construct any additional indices in a block
    resulting from the discretization of a ContinuousSet. For
    Block-derived components we check if the Block construct method has
    been overridden. If not then we update it like a regular block. If
    construct has been overridden then we try to call the component's
    update_after_discretization method. If the component hasn't
    implemented this method then we throw a warning and try to update it
    like a normal block. The issue, when construct is overridden, is that
    anything could be happening and we can't automatically assume that
    treating the block-derived component like a normal block will be
    sufficient to update it correctly.

    """
    
    # Check if Block construct method is overridden
    # getattr needed below for Python 2, 3 compatibility
    if blk.construct.__func__ is not getattr(IndexedBlock.construct,
                                             '__func__',
                                             IndexedBlock.construct):
        # check for custom update function
        if hasattr(blk, 'update_after_discretization'):
            blk.update_after_discretization()
            return
        else:
            logger.warning(
                'DAE(misc): Attempting to apply a discretization '
                'transformation to the Block-derived component "%s". The '
                'component overrides the Block construct method but no '
                'update_after_discretization() function was found. Will '
                'attempt to update as a standard Block but user should verify '
                'that the component was expanded correctly. To suppress this '
                'warning, please provide an update_after_discretization() '
                'function on Block-derived components that override '
                'construct()' % blk.name)

    # Code taken from the construct() method of Block
    missing_idx = getattr(blk, '_dae_missing_idx', set([]))
    for idx in list(missing_idx):
        _block = blk[idx]
        obj = apply_indexed_rule(
            blk, blk._rule, _block, idx, blk._options)
 
        if isinstance(obj, _BlockData) and obj is not _block:
            # If the user returns a block, use their block instead
            # of the empty one we just created.
            for c in list(obj.component_objects(descend_into=False)):
                obj.del_component(c)
                _block.add_component(c.local_name, c)
                # transfer over any other attributes that are not components
            for name, val in iteritems(obj.__dict__):
                if not hasattr(_block, name) and not hasattr(blk, name):
                    super(_BlockData, _block).__setattr__(name, val)

    # Remove book-keeping data after Block is discretized
    if hasattr(blk, '_dae_missing_idx'):
        del blk._dae_missing_idx