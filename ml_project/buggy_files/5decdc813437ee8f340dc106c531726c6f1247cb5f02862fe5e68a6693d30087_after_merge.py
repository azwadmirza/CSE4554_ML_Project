    def _set_elements(self, root):
        """wrap objectified xml part with selection of elements to
        self.elements list
        """
        try:
            elements = root.find(
                "./ClassInstance[@Type='TRTContainerClass']"
                "/ChildClassInstances"
                "/ClassInstance[@Type='TRTElementInformationList']"
                "/ClassInstance[@Type='TRTSpectrumRegionList']"
                "/ChildClassInstances")
            for j in elements.findall(
                    "./ClassInstance[@Type='TRTSpectrumRegion']"):
                tmp_d = dictionarize(j)
                self.elements[tmp_d['XmlClassName']] = {'line': tmp_d['Line'],
                                                        'energy': tmp_d['Energy']}
        except AttributeError:
            _logger.info('no element selection present in the spectra..')