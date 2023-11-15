    def get_dataset(self, key, info):
        """Read data from file and return the corresponding projectables.
        """
        datadict = {
            1000: ['EV_250_Aggr1km_RefSB',
                   'EV_500_Aggr1km_RefSB',
                   'EV_1KM_RefSB',
                   'EV_1KM_Emissive'],
            500: ['EV_250_Aggr500_RefSB',
                  'EV_500_RefSB'],
            250: ['EV_250_RefSB']}

        platform_name = self.metadata['INVENTORYMETADATA']['ASSOCIATEDPLATFORMINSTRUMENTSENSOR'][
            'ASSOCIATEDPLATFORMINSTRUMENTSENSORCONTAINER']['ASSOCIATEDPLATFORMSHORTNAME']['VALUE']

        info.update({'platform_name': 'EOS-' + platform_name})
        info.update({'sensor': 'modis'})

        if self.resolution != key.resolution:
            return

        datasets = datadict[self.resolution]

        for dataset in datasets:
            subdata = self.sd.select(dataset)
            band_names = subdata.attributes()["band_names"].split(",")

            # get the relative indices of the desired channel
            try:
                index = band_names.index(key.name)
            except ValueError:
                continue
            uncertainty = self.sd.select(dataset + "_Uncert_Indexes")
            if dataset.endswith('Emissive'):
                array = calibrate_tb(subdata, uncertainty, [index], band_names)
            else:
                array = calibrate_refl(subdata, uncertainty, [index])

            projectable = Dataset(array[0], id=key, mask=array[0].mask, **info)
            # if ((platform_name == 'Aqua' and key.name in ["6", "27", "36"]) or
            #         (platform_name == 'Terra' and key.name in ["29"])):
            #     height, width = projectable.shape
            #     row_indices = projectable.mask.sum(1) == width
            #     if row_indices.sum() != height:
            #         projectable.mask[row_indices, :] = True

            # Get the orbit number
            # if not satscene.orbit:
            #     mda = self.data.attributes()["CoreMetadata.0"]
            #     orbit_idx = mda.index("ORBITNUMBER")
            #     satscene.orbit = mda[orbit_idx + 111:orbit_idx + 116]

            # Get the geolocation
            # if resolution != 1000:
            #    logger.warning("Cannot load geolocation at this resolution (yet).")
            #    return

            # Trimming out dead sensor lines (detectors) on terra:
            # (in addition channel 27, 30, 34, 35, and 36 are nosiy)
            # if satscene.satname == "terra":
            #     for band in ["29"]:
            #         if not satscene[band].is_loaded() or satscene[band].data.mask.all():
            #             continue
            #         width = satscene[band].data.shape[1]
            #         height = satscene[band].data.shape[0]
            #         indices = satscene[band].data.mask.sum(1) < width
            #         if indices.sum() == height:
            #             continue
            #         satscene[band] = satscene[band].data[indices, :]
            #         satscene[band].area = geometry.SwathDefinition(
            #             lons=satscene[band].area.lons[indices, :],
            #             lats=satscene[band].area.lats[indices, :])
            return projectable