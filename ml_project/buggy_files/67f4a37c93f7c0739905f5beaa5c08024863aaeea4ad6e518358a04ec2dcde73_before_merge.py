    def __setitem__(self, index, data):
        """Sets a block with a VTK data object. To set the name simultaneously,
        pass a string name as the 2nd index.

        Example
        -------
        >>> import vtki
        >>> multi = vtki.MultiBlock()
        >>> multi[0] = vtki.PolyData()
        >>> multi[1, 'foo'] = vtki.UnstructuredGrid()
        >>> multi['bar'] = vtki.PolyData()
        >>> multi.n_blocks
        3
        """
        if isinstance(index, collections.Iterable) and not isinstance(index, str):
            i, name = index[0], index[1]
        elif isinstance(index, str):
            try:
                i = self.get_index_by_name(index)
            except KeyError:
                i = -1
            name = index
        else:
            i, name = index, None
        if data is not None and not is_vtki_obj(data):
            data = wrap(data)
        if i == -1:
            self.append(data)
            i = self.n_blocks - 1
        else:
            self.SetBlock(i, data)
        if name is None:
            name = 'Block-{0:02}'.format(i)
        self.set_block_name(i, name) # Note that this calls self.Modified()