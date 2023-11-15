    def _set_sum_edx(self, root, indexes):
        for i in indexes:
            spec_node = root.find(
                "./SpectrumData{0}/ClassInstance".format(str(i)))
            self.spectra_data[i] = EDXSpectrum(spec_node)