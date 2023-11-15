    def create_axes(self, axes, obj, validate=True, nan_rep=None,
                    data_columns=None, min_itemsize=None, **kwargs):
        """ create and return the axes
        leagcy tables create an indexable column, indexable index,
        non-indexable fields

            Parameters:
            -----------
            axes: a list of the axes in order to create (names or numbers of
                the axes)
            obj : the object to create axes on
            validate: validate the obj against an existing object already
                written
            min_itemsize: a dict of the min size for a column in bytes
            nan_rep : a values to use for string column nan_rep
            encoding : the encoding for string values
            data_columns : a list of columns that we want to create separate to
                allow indexing (or True will force all columns)

        """

        # set the default axes if needed
        if axes is None:
            try:
                axes = _AXES_MAP[type(obj)]
            except:
                raise TypeError("cannot properly create the storer for: "
                                "[group->%s,value->%s]"
                                % (self.group._v_name, type(obj)))

        # map axes to numbers
        axes = [obj._get_axis_number(a) for a in axes]

        # do we have an existing table (if so, use its axes & data_columns)
        if self.infer_axes():
            existing_table = self.copy()
            existing_table.infer_axes()
            axes = [a.axis for a in existing_table.index_axes]
            data_columns = existing_table.data_columns
            nan_rep = existing_table.nan_rep
            self.encoding = existing_table.encoding
            self.info = copy.copy(existing_table.info)
        else:
            existing_table = None

        # currently support on ndim-1 axes
        if len(axes) != self.ndim - 1:
            raise ValueError(
                "currently only support ndim-1 indexers in an AppendableTable")

        # create according to the new data
        self.non_index_axes = []
        self.data_columns = []

        # nan_representation
        if nan_rep is None:
            nan_rep = 'nan'

        self.nan_rep = nan_rep

        # create axes to index and non_index
        index_axes_map = dict()
        for i, a in enumerate(obj.axes):

            if i in axes:
                name = obj._AXIS_NAMES[i]
                index_axes_map[i] = _convert_index(
                    a, self.encoding, self.format_type
                ).set_name(name).set_axis(i)
            else:

                # we might be able to change the axes on the appending data if
                # necessary
                append_axis = list(a)
                if existing_table is not None:
                    indexer = len(self.non_index_axes)
                    exist_axis = existing_table.non_index_axes[indexer][1]
                    if append_axis != exist_axis:

                        # ahah! -> reindex
                        if sorted(append_axis) == sorted(exist_axis):
                            append_axis = exist_axis

                # the non_index_axes info
                info = _get_info(self.info, i)
                info['names'] = list(a.names)
                info['type'] = a.__class__.__name__

                self.non_index_axes.append((i, append_axis))

        # set axis positions (based on the axes)
        self.index_axes = [
            index_axes_map[a].set_pos(j).update_info(self.info)
            for j, a in enumerate(axes)
        ]
        j = len(self.index_axes)

        # check for column conflicts
        for a in self.axes:
            a.maybe_set_size(min_itemsize=min_itemsize)

        # reindex by our non_index_axes & compute data_columns
        for a in self.non_index_axes:
            obj = _reindex_axis(obj, a[0], a[1])

        def get_blk_items(mgr, blocks):
            return [mgr.items.take(blk.mgr_locs) for blk in blocks]

        # figure out data_columns and get out blocks
        block_obj = self.get_object(obj).consolidate()
        blocks = block_obj._data.blocks
        blk_items = get_blk_items(block_obj._data, blocks)
        if len(self.non_index_axes):
            axis, axis_labels = self.non_index_axes[0]
            data_columns = self.validate_data_columns(
                data_columns, min_itemsize)
            if len(data_columns):
                mgr = block_obj.reindex_axis(
                    Index(axis_labels).difference(Index(data_columns)),
                    axis=axis
                )._data

                blocks = list(mgr.blocks)
                blk_items = get_blk_items(mgr, blocks)
                for c in data_columns:
                    mgr = block_obj.reindex_axis([c], axis=axis)._data
                    blocks.extend(mgr.blocks)
                    blk_items.extend(get_blk_items(mgr, mgr.blocks))

        # reorder the blocks in the same order as the existing_table if we can
        if existing_table is not None:
            by_items = dict([(tuple(b_items.tolist()), (b, b_items))
                             for b, b_items in zip(blocks, blk_items)])
            new_blocks = []
            new_blk_items = []
            for ea in existing_table.values_axes:
                items = tuple(ea.values)
                try:
                    b, b_items = by_items.pop(items)
                    new_blocks.append(b)
                    new_blk_items.append(b_items)
                except:
                    raise ValueError(
                        "cannot match existing table structure for [%s] on "
                        "appending data" % ','.join(pprint_thing(item) for
                                                    item in items))
            blocks = new_blocks
            blk_items = new_blk_items

        # add my values
        self.values_axes = []
        for i, (b, b_items) in enumerate(zip(blocks, blk_items)):

            # shape of the data column are the indexable axes
            klass = DataCol
            name = None

            # we have a data_column
            if (data_columns and len(b_items) == 1 and
                    b_items[0] in data_columns):
                klass = DataIndexableCol
                name = b_items[0]
                self.data_columns.append(name)

            # make sure that we match up the existing columns
            # if we have an existing table
            if existing_table is not None and validate:
                try:
                    existing_col = existing_table.values_axes[i]
                except:
                    raise ValueError("Incompatible appended table [%s] with "
                                     "existing table [%s]"
                                     % (blocks, existing_table.values_axes))
            else:
                existing_col = None

            try:
                col = klass.create_for_block(
                    i=i, name=name, version=self.version)
                col.set_atom(block=b, block_items=b_items,
                             existing_col=existing_col,
                             min_itemsize=min_itemsize,
                             nan_rep=nan_rep,
                             encoding=self.encoding,
                             info=self.info,
                             **kwargs)
                col.set_pos(j)

                self.values_axes.append(col)
            except (NotImplementedError, ValueError, TypeError) as e:
                raise e
            except Exception as detail:
                raise Exception(
                    "cannot find the correct atom type -> "
                    "[dtype->%s,items->%s] %s"
                    % (b.dtype.name, b_items, str(detail))
                )
            j += 1

        # validate our min_itemsize
        self.validate_min_itemsize(min_itemsize)

        # validate our metadata
        self.validate_metadata(existing_table)

        # validate the axes if we have an existing table
        if validate:
            self.validate(existing_table)