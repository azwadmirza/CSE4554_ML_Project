    def __init__(self, config_files, mask_surface=True, mask_quality=True, **kwargs):
        """Configure reader behavior.

        Args:
            mask_surface (boolean): mask anything below the surface pressure
            mask_quality (boolean): mask anything where the `Quality_Flag` metadata is ``!= 1``.

        """
        self.pressure_dataset_names = defaultdict(list)
        super(NUCAPSReader, self).__init__(config_files,
                                           **kwargs)
        self.mask_surface = self.info.get('mask_surface', mask_surface)
        self.mask_quality = self.info.get('mask_quality', mask_quality)