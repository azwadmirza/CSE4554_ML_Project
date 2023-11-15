    def _setup_vfs(self):
        """Setup the virtual file system tree represented as python dictionary
        with values populated with SFSTreeItem instances

        See also:
        SFSTreeItem
        """
        with open(self.filename, 'rb') as fn:
            # file tree do not exceed one chunk in bcf:
            fn.seek(self.chunksize * self.tree_address + 0x138)
            raw_tree = fn.read(0x200 * self.n_tree_items)
            temp_item_list = [SFSTreeItem(raw_tree[i * 0x200:(i + 1) * 0x200],
                                          self) for i in range(self.n_tree_items)]
            # temp list with parents of items
            paths = [[h.parent] for h in temp_item_list]
        # checking the compression header which can be different per file:
        self._check_the_compresion(temp_item_list)
        if self.compression == 'zlib':
            for c in temp_item_list:
                if not c.is_dir:
                    c.setup_compression_metadata()
        # convert the items to virtual file system tree
        dict_tree = self._flat_items_to_dict(paths, temp_item_list)
        # and finaly set the Virtual file system:
        self.vfs = dict_tree['root']