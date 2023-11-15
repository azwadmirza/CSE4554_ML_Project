    def _parse_result(self, response, verbose=False):
        # if verbose is False then suppress any VOTable related warnings
        if not verbose:
            commons.suppress_vo_warnings()

        if "BATCH_RETRIEVAL_MSG ERROR:" in response.text:
            raise InvalidQueryError("One or more inputs is not recognized by HEASARC. "
                             "Check that the object name is in GRB, SIMBAD+Sesame, or "
                             "NED format and that the mission name is as listed in "
                             "query_mission_list().")
        elif "ERROR" in response.text:
            raise InvalidQueryError("unspecified error from HEASARC database. "
                                    "\nCheck error message: \n{!s}".format(response.text))

        try:
            data = BytesIO(response.content)
            table = Table.read(data, hdu=1)
            return table
        except ValueError:
            return self._fallback(response.content)