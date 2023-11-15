    def _setup_vfs(self):
        """Setup the virtual file system tree represented as python dictionary
        with values populated with SFSTreeItem instances

        See also:
        SFSTreeItem
        """
        with open(self.filename, 'rb') as fn:
            #check if file tree do not exceed one chunk:
            n_file_tree_chunks = ceil((self.n_tree_items * 0x200) /
                                      (self.chunksize - 0x20))
            if n_file_tree_chunks == 1:
                # file tree do not exceed one chunk in bcf:
                fn.seek(self.chunksize * self.tree_address + 0x138)
                raw_tree = fn.read(0x200 * self.n_tree_items)
            else:
                temp_str = io.BytesIO()
                tree_address = self.tree_address
                tree_items_in_chunk = (self.chunksize - 0x20) // 0x200
                for i in range(n_file_tree_chunks):
                    # jump to tree/list address:
                    fn.seek(self.chunksize * tree_address + 0x118)
                    # next tree/list address:
                    tree_address = strct_unp('<I', fn.read(4))[0]
                    fn.seek(28, 1)
                    temp_str.write(fn.read(tree_items_in_chunk * 0x200))
                temp_str.seek(0)
                raw_tree = temp_str.read(self.n_tree_items * 0x200)
                temp_str.close()
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