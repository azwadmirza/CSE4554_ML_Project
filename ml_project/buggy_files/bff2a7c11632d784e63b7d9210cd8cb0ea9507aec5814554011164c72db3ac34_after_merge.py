    def fetch(self, *query_results, **kwargs):
        """
        Download the records represented by
        `~sunpy.net.fido_factory.UnifiedResponse` objects.

        Parameters
        ----------
        query_results : `sunpy.net.fido_factory.UnifiedResponse`
            Container returned by query method, or multiple.

        wait : `bool`
            fetch will wait until the download is complete before returning.

        progress : `bool`
            Show a progress bar while the download is running.

        Returns
        -------
        `sunpy.net.fido_factory.DownloadResponse`

        Example
        --------
        >>> from sunpy.net.vso.attrs import Time, Instrument
        >>> unifresp = Fido.search(Time('2012/3/4','2012/3/6'), Instrument('AIA'))
        >>> downresp = Fido.get(unifresp)
        >>> file_paths = downresp.wait()
        """
        wait = kwargs.pop("wait", True)
        progress = kwargs.pop("progress", True)
        reslist = []
        for query_result in query_results:
            for block in query_result.responses:
                reslist.append(block.client.get(block, **kwargs))

        results = DownloadResponse(reslist)

        if wait:
            return results.wait(progress=progress)
        else:
            return results