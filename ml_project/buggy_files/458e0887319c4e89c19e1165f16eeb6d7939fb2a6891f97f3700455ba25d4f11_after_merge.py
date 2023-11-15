    def _make_image_description(self, datasets, **kwargs):
        """
        generate image description for mitiff.

        Satellite: NOAA 18
        Date and Time: 06:58 31/05-2016
        SatDir: 0
        Channels:   6 In this file: 1-VIS0.63 2-VIS0.86 3(3B)-IR3.7
        4-IR10.8 5-IR11.5 6(3A)-VIS1.6
        Xsize:  4720
        Ysize:  5544
        Map projection: Stereographic
        Proj string: +proj=stere +lon_0=0 +lat_0=90 +lat_ts=60
        +ellps=WGS84 +towgs84=0,0,0 +units=km
        +x_0=2526000.000000 +y_0=5806000.000000
        TrueLat: 60 N
        GridRot: 0
        Xunit:1000 m Yunit: 1000 m
        NPX: 0.000000 NPY: 0.000000
        Ax: 1.000000 Ay: 1.000000 Bx: -2526.000000 By: -262.000000

        Satellite: <satellite name>
        Date and Time: <HH:MM dd/mm-yyyy>
        SatDir: 0
        Channels:   <number of chanels> In this file: <channels names in order>
        Xsize:  <number of pixels x>
        Ysize:  <number of pixels y>
        Map projection: Stereographic
        Proj string: <proj4 string with +x_0 and +y_0 which is the positive
        distance from proj origo
        to the lower left corner of the image data>
        TrueLat: 60 N
        GridRot: 0
        Xunit:1000 m Yunit: 1000 m
        NPX: 0.000000 NPY: 0.000000
        Ax: <pixels size x in km> Ay: <pixel size y in km> Bx: <left corner of
        upper right pixel in km>
        By: <upper corner of upper right pixel in km>


        if palette image write special palette
        if normal channel write table calibration:
        Table_calibration: <channel name>, <calibration type>, [<unit>],
        <no of bits of data>,
        [<calibration values space separated>]\n\n
        """

        translate_platform_name = {'metop01': 'Metop-B',
                                   'metop02': 'Metop-A',
                                   'metop03': 'Metop-C',
                                   'noaa15': 'NOAA-15',
                                   'noaa16': 'NOAA-16',
                                   'noaa17': 'NOAA-17',
                                   'noaa18': 'NOAA-18',
                                   'noaa19': 'NOAA-19'}

        first_dataset = datasets
        if isinstance(datasets, list):
            LOG.debug("Datasets is a list of dataset")
            first_dataset = datasets[0]

        if 'platform_name' in first_dataset.attrs:
            _platform_name = translate_platform_name.get(
                first_dataset.attrs['platform_name'],
                first_dataset.attrs['platform_name'])
        elif 'platform_name' in kwargs:
            _platform_name = translate_platform_name.get(
                kwargs['platform_name'], kwargs['platform_name'])
        else:
            _platform_name = None

        _image_description = ''
        _image_description.encode('utf-8')

        _image_description += ' Satellite: '
        if _platform_name is not None:
            _image_description += _platform_name

        _image_description += '\n'

        _image_description += ' Date and Time: '
        # Select earliest start_time
        first = True
        earliest = 0
        for dataset in datasets:
            if first:
                earliest = dataset.attrs['start_time']
            else:
                if dataset.attrs['start_time'] < earliest:
                    earliest = dataset.attrs['start_time']
            first = False
        LOG.debug("earliest start_time: %s", earliest)
        _image_description += earliest.strftime("%H:%M %d/%m-%Y\n")

        _image_description += ' SatDir: 0\n'

        _image_description += ' Channels: '

        if isinstance(datasets, list):
            LOG.debug("len datasets: %s", len(datasets))
            _image_description += str(len(datasets))
        elif 'bands' in datasets.sizes:
            LOG.debug("len datasets: %s", datasets.sizes['bands'])
            _image_description += str(datasets.sizes['bands'])
        elif len(datasets.sizes) == 2:
            LOG.debug("len datasets: 1")
            _image_description += '1'

        _image_description += ' In this file: '

        channels = self._make_channel_list(datasets, **kwargs)

        try:
            cns = self.translate_channel_name.get(kwargs['sensor'], {})
        except KeyError:
            pass

        _image_description += self._channel_names(channels, cns, **kwargs)

        _image_description += self._add_sizes(datasets, first_dataset)

        _image_description += ' Map projection: Stereographic\n'

        _image_description += self._add_proj4_string(datasets, first_dataset)

        _image_description += ' TrueLat: 60N\n'
        _image_description += ' GridRot: 0\n'

        _image_description += ' Xunit:1000 m Yunit: 1000 m\n'

        _image_description += ' NPX: %.6f' % (0)
        _image_description += ' NPY: %.6f' % (0) + '\n'

        _image_description += self._add_pixel_sizes(datasets, first_dataset)
        _image_description += self._add_corners(datasets, first_dataset)

        if isinstance(datasets, list):
            LOG.debug("Area extent: %s", first_dataset.attrs['area'].area_extent)
        else:
            LOG.debug("Area extent: %s", datasets.attrs['area'].area_extent)

        _image_description += self._add_calibration(channels, cns, datasets, **kwargs)

        return _image_description