    def __init__(self, outputs, indices, fields=None, suppress_logging=False):

        indices.sort() # Just in case the caller wasn't careful
        self.field_data = YTFieldData()
        self.data_series = outputs
        self.masks = []
        self.sorts = []
        self.array_indices = []
        self.indices = indices
        self.num_indices = len(indices)
        self.num_steps = len(outputs)
        self.times = []
        self.suppress_logging = suppress_logging

        if fields is None: fields = []
        fields = list(OrderedDict.fromkeys(fields))

        if self.suppress_logging:
            old_level = int(ytcfg.get("yt","loglevel"))
            mylog.setLevel(40)
        
        fds = {}
        ds_first = self.data_series[0]
        dd_first = ds_first.all_data()
        idx_field = dd_first._determine_fields("particle_index")[0]
        for field in ("particle_position_%s" % ax for ax in "xyz"):
            fds[field] = dd_first._determine_fields(field)[0]

        my_storage = {}
        pbar = get_pbar("Constructing trajectory information", len(self.data_series))
        for i, (sto, ds) in enumerate(self.data_series.piter(storage=my_storage)):
            dd = ds.all_data()
            newtags = dd[idx_field].d.astype("int64")
            mask = np.in1d(newtags, indices, assume_unique=True)
            sort = np.argsort(newtags[mask])
            array_indices = np.where(np.in1d(indices, newtags, assume_unique=True))[0]
            self.array_indices.append(array_indices)
            self.masks.append(mask)
            self.sorts.append(sort)

            pfields = {}
            for field in ("particle_position_%s" % ax for ax in "xyz"):
                pfields[field] = dd[fds[field]].ndarray_view()[mask][sort]

            sto.result_id = ds.parameter_filename
            sto.result = (ds.current_time, array_indices, pfields)
            pbar.update(i)
        pbar.finish()

        if self.suppress_logging:
            mylog.setLevel(old_level)

        times = []
        for fn, (time, indices, pfields) in sorted(my_storage.items()):
            times.append(time)
        self.times = self.data_series[0].arr([time for time in times], times[0].units)

        self.particle_fields = []
        output_field = np.empty((self.num_indices, self.num_steps))
        output_field.fill(np.nan)
        for field in ("particle_position_%s" % ax for ax in "xyz"):
            for i, (fn, (time, indices, pfields)) in enumerate(sorted(my_storage.items())):
                output_field[indices, i] = pfields[field]
            self.field_data[field] = array_like_field(
                dd_first, output_field.copy(), fds[field])
            self.particle_fields.append(field)

        # Instantiate fields the caller requested
        self._get_data(fields)