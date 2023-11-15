    def __init__(self, xml_str, indexes, instrument=None):
        root = ET.fromstring(xml_str)
        root = root.find("./ClassInstance[@Type='TRTSpectrumDatabase']")
        try:
            self.name = str(root.attrib['Name'])
        except KeyError:
            self.name = 'Undefinded'
            _logger.info("hypermap have no name. Giving it 'Undefined' name")
        hd = root.find("./Header")
        dt = datetime.strptime(' '.join([str(hd.find('./Date').text),
                                         str(hd.find('./Time').text)]),
                               "%d.%m.%Y %H:%M:%S")
        self.date = dt.date().isoformat()
        self.time = dt.time().isoformat()
        self.version = int(hd.find('./FileVersion').text)
        # fill the sem and stage attributes:
        self._set_microscope(root)
        self._get_mode(instrument)
        self._set_images(root)
        self.elements = {}
        self._set_elements(root)
        self.line_counter = interpret(root.find('./LineCounter').text)
        self.channel_count = int(root.find('./ChCount').text)
        self.mapping_count = int(root.find('./DetectorCount').text)
        #self.channel_factors = {}
        self.spectra_data = {}
        self._set_sum_edx(root, indexes)