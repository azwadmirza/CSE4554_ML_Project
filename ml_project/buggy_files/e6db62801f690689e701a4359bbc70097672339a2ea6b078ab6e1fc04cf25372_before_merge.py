    def __init__(self, settings=None):
        CodePrinter.__init__(self, settings)
        # leading columns depend on fixed or free format
        if self._settings['source_format'] == 'fixed':
            self._lead_code = "      "
            self._lead_cont = "     @ "
            self._lead_comment = "C     "
        elif self._settings['source_format'] == 'free':
            self._lead_code = ""
            self._lead_cont = "      "
            self._lead_comment = "! "
        else:
            raise ValueError("Unknown source format: %s" % self._settings[
                             'source_format'])
        standards = set([66, 77, 90, 95, 2003, 2008])
        if self._settings['standard'] not in standards:
            raise ValueError("Unknown Fortran standard: %s" % self._settings[
                             'standard'])