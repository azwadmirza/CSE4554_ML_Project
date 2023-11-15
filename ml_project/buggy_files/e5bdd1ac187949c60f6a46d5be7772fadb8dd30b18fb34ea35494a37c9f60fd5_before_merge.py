    def __call__(self, projectables, optional_datasets=None, **info):
        factor = self.info.get('factor', 2)

        (band,) = projectables

        LOG.info('Expanding datasize by a factor %d.', factor)

        proj = Dataset(
            np.repeat(np.repeat(band, factor, axis=0), factor, axis=1),
            copy=False, **band.info)

        old_area = proj.info['area']
        proj.info['area'] = AreaDefinition(old_area.area_id,
                                           old_area.name,
                                           old_area.proj_id,
                                           old_area.proj_dict,
                                           old_area.x_size * factor,
                                           old_area.y_size * factor,
                                           old_area.area_extent)
        proj.info['resolution'] *= factor
        self.apply_modifier_info(band, proj)
        return proj