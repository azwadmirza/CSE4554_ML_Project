    def add_deposited_particle_field(self, deposit_field, method, kernel_name='cubic',
                                     weight_field='particle_mass'):
        """Add a new deposited particle field

        Creates a new deposited field based on the particle *deposit_field*.

        Parameters
        ----------

        deposit_field : tuple
           The field name tuple of the particle field the deposited field will
           be created from.  This must be a field name tuple so yt can
           appropriately infer the correct particle type.
        method : string
           This is the "method name" which will be looked up in the
           `particle_deposit` namespace as `methodname_deposit`.  Current
           methods include `simple_smooth`, `sum`, `std`, `cic`, `weighted_mean`,
           `mesh_id`, and `nearest`.
        kernel_name : string, default 'cubic'
           This is the name of the smoothing kernel to use. It is only used for
           the `simple_smooth` method and is otherwise ignored. Current
           supported kernel names include `cubic`, `quartic`, `quintic`,
           `wendland2`, `wendland4`, and `wendland6`.
        weight_field : string, default 'particle_mass'
           Weighting field name for deposition method `weighted_mean`.

        Returns
        -------

        The field name tuple for the newly created field.
        """
        self.index
        if isinstance(deposit_field, tuple):
            ptype, deposit_field = deposit_field[0], deposit_field[1]
        else:
            raise RuntimeError

        units = self.field_info[ptype, deposit_field].units
        take_log = self.field_info[ptype, deposit_field].take_log
        name_map = {"sum": "sum", "std":"std", "cic": "cic", "weighted_mean": "avg",
                    "nearest": "nn", "simple_smooth": "ss", "count": "count"}
        field_name = "%s_" + name_map[method] + "_%s"
        field_name = field_name % (ptype, deposit_field.replace('particle_', ''))

        if method == "count":
            field_name = "%s_count" % ptype
            if ("deposit", field_name) in self.field_info:
                mylog.warning("The deposited field %s already exists" % field_name)
                return ("deposit", field_name)
            else:
                units = "dimensionless"
                take_log = False

        def _deposit_field(field, data):
            """
            Create a grid field for particle quantities using given method.
            """
            pos = data[ptype, "particle_position"]
            if method == 'weighted_mean':
                d = data.ds.arr(data.deposit(pos, [data[ptype, deposit_field],
                                                   data[ptype, weight_field]],
                                             method=method, kernel_name=kernel_name),
                                             input_units=units)
                d[np.isnan(d)] = 0.0
            else:
                d = data.ds.arr(data.deposit(pos, [data[ptype, deposit_field]],
                                             method=method, kernel_name=kernel_name),
                                             input_units=units)
            return d

        self.add_field(
            ("deposit", field_name),
            function=_deposit_field,
            units=units,
            take_log=take_log,
            validators=[ValidateSpatial()])
        return ("deposit", field_name)