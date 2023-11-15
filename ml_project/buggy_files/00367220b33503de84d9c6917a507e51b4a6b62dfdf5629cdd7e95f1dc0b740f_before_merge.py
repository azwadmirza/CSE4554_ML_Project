    def search(self, *query):
        """
        Query for data in form of multiple parameters.

        Examples
        --------
        Query for LYRALightCurve data for the time range ('2012/3/4','2012/3/6')

        >>> from sunpy.net import Fido, attrs as a
        >>> unifresp = Fido.search(a.Time('2012/3/4', '2012/3/6'), a.Instrument('lyra'))

        Query for data from Nobeyama Radioheliograph and RHESSI

        >>> unifresp = Fido.search(a.Time('2012/3/4', '2012/3/6'),
                                   a.Instrument('norh') | a.Instrument('rhessi'))

        Query for 304 Angstrom SDO AIA data with a cadence of 10 minutes

        >>> import astropy.units as u
        >>> from sunpy.net import Fido, attrs as a
        >>> unifresp = Fido.search(a.Time('2012/3/4', '2012/3/6'),
                                   a.Instrument('AIA'),
                                   a.Wavelength(304*u.angstrom, 304*u.angstrom),
                                   a.Sample(10*u.minute))

        Parameters
        ----------
        query : `sunpy.net.vso.attrs`, `sunpy.net.jsoc.attrs`
            A query consisting of multiple parameters which define the
            requested data.  The query is specified using attributes from the
            VSO and the JSOC.  The query can mix attributes from the VSO and
            the JSOC.

        Returns
        -------
        `sunpy.net.fido_factory.UnifiedResponse` object
            Container of responses returned by clients servicing query.

        Notes
        -----
        The conjunction 'and' transforms query into disjunctive normal form
        ie. query is now of form A & B or ((A & B) | (C & D))
        This helps in modularising query into parts and handling each of the
        parts individually.
        """
        query = attr.and_(*query)
        return UnifiedResponse(query_walker.create(query, self))