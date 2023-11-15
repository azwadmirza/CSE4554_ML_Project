    def set_value(self, val, guarantee_components=set()):
        # Copy over everything from the other block.  If the other
        # block has an indicator_var, it should override this block's.
        # Otherwise restore this block's indicator_var.
        guarantee_components.add('indicator_var')
        super(_DisjunctData, self).set_value(val, guarantee_components)