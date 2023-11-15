    def _set_sum_edx(self, root):
        for i in range(self.mapping_count):
            spec_node = root.find(
                "./SpectrumData{0}/ClassInstance".format(str(i)))
            self.spectra_data[i] = EDXSpectrum(spec_node)