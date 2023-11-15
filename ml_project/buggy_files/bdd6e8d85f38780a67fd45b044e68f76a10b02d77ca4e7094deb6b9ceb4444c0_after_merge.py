    def _add_temporary_set(self, val):
        """TODO: This method has known issues (see tickets) and needs to be
        reviewed. [JDS 9/2014]"""

        _component_sets = getattr(val, '_implicit_subsets', None)
        #
        # FIXME: The name attribute should begin with "_", and None
        # should replace "_unknown_"
        #
        if _component_sets is not None:
            for ctr, tset in enumerate(_component_sets):
                if tset.parent_component()._name == "_unknown_":
                    self._construct_temporary_set(
                        tset,
                        val.local_name + "_index_" + str(ctr)
                    )
        if isinstance(val._index, _SetDataBase) and \
                val._index.parent_component().local_name == "_unknown_":
            self._construct_temporary_set(val._index, val.local_name + "_index")
        if isinstance(getattr(val, 'initialize', None), _SetDataBase) and \
                val.initialize.parent_component().local_name == "_unknown_":
            self._construct_temporary_set(val.initialize, val.local_name + "_index_init")
        if getattr(val, 'domain', None) is not None and \
           getattr(val.domain, 'local_name', None) == "_unknown_":
            self._construct_temporary_set(val.domain, val.local_name + "_domain")