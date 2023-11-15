    def __init__(self, filename, dataset_type="gadget_binary",
                 additional_fields=(),
                 unit_base=None, n_ref=64,
                 over_refine_factor=1,
                 kernel_name=None,
                 index_ptype="all",
                 bounding_box=None,
                 header_spec="default",
                 field_spec="default",
                 ptype_spec="default",
                 units_override=None,
                 unit_system="cgs",
                 use_dark_factor = False,
                 w_0 = -1.0,
                 w_a = 0.0):
        if self._instantiated:
            return
        self._header_spec = self._setup_binary_spec(
            header_spec, gadget_header_specs)
        self._header_size = _compute_header_size(self._header_spec)
        if self._header_size != 256:
            only_on_root(
                mylog.warn,
                "Non-standard header size is detected! "
                "Gadget-2 standard header is 256 bytes, but yours is %s. "
                "Make sure a non-standard header is actually expected. "
                "Otherwise something is wrong, "
                "and you might want to check how the dataset is loaded. "
                "Futher information about header specification can be found in "
                "https://yt-project.org/docs/dev/examining/loading_data.html#header-specification.",
                self._header_size
            )
        self._field_spec = self._setup_binary_spec(
            field_spec, gadget_field_specs)
        self._ptype_spec = self._setup_binary_spec(
            ptype_spec, gadget_ptype_specs)
        self.index_ptype = index_ptype
        self.storage_filename = None
        if unit_base is not None and "UnitLength_in_cm" in unit_base:
            # We assume this is comoving, because in the absence of comoving
            # integration the redshift will be zero.
            unit_base['cmcm'] = 1.0 / unit_base["UnitLength_in_cm"]
        self._unit_base = unit_base
        if bounding_box is not None:
            bbox = np.array(bounding_box, dtype="float64")
            if bbox.shape == (2, 3):
                bbox = bbox.transpose()
            self.domain_left_edge = bbox[:, 0]
            self.domain_right_edge = bbox[:, 1]
        else:
            self.domain_left_edge = self.domain_right_edge = None
        if units_override is not None:
            raise RuntimeError("units_override is not supported for GadgetDataset. " +
                               "Use unit_base instead.")

        # Set dark energy parameters before cosmology object is created
        self.use_dark_factor = use_dark_factor
        self.w_0 = w_0
        self.w_a = w_a

        super(GadgetDataset, self).__init__(
            filename, dataset_type=dataset_type, unit_system=unit_system,
            n_ref=n_ref, over_refine_factor=over_refine_factor,
            kernel_name=kernel_name)
        if self.cosmological_simulation:
            self.time_unit.convert_to_units('s/h')
            self.length_unit.convert_to_units('kpccm/h')
            self.mass_unit.convert_to_units('g/h')
        else:
            self.time_unit.convert_to_units('s')
            self.length_unit.convert_to_units('kpc')
            self.mass_unit.convert_to_units('Msun')