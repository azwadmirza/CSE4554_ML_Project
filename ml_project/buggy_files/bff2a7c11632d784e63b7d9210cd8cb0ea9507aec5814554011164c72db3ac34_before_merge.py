    def fetch(self, query_result, wait=True, progress=True, **kwargs):
        """
        Downloads the files pointed at by URLs contained within UnifiedResponse
        object.

        Parameters
        ----------
        query_result : `sunpy.net.fido_factory.UnifiedResponse`
            Container returned by query method.

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
        reslist = []
        for block in query_result.responses:
            reslist.append(block.client.get(block, **kwargs))

        results = DownloadResponse(reslist)

        if wait:
            return results.wait(progress=progress)
        else:
            return results