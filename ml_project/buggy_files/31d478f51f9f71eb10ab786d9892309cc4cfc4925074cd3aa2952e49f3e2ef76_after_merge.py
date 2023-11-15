    def fetch(self, *query_results, path=None, max_conn=5, progress=True,
              overwrite=False, downloader=None, **kwargs):
        """
        Download the records represented by
        `~sunpy.net.fido_factory.UnifiedResponse` objects.

        Parameters
        ----------
        query_results : `sunpy.net.fido_factory.UnifiedResponse`
            Container returned by query method, or multiple.

        path : `str`
            The directory to retrieve the files into. Can refer to any fields
            in `UnifiedResponse.response_block_properties` via string formatting,
            moreover the file-name of the file downloaded can be referred to as file,
            e.g. "{source}/{instrument}/{time.start}/{file}".

        max_conn : `int`, optional
            The number of parallel download slots.

        progress : `bool`, optional
            If `True` show a progress bar showing how many of the total files
            have been downloaded. If `False`, no progress bars will be shown at all.

        overwrite : `bool` or `str`, optional
            Determine how to handle downloading if a file already exists with the
            same name. If `False` the file download will be skipped and the path
            returned to the existing file, if `True` the file will be downloaded
            and the existing file will be overwritten, if `'unique'` the filename
            will be modified to be unique.

        downloader : `parfive.Downloader`, optional
            The download manager to use. If specified the ``max_conn``,
            ``progress`` and ``overwrite`` arguments are ignored.

        Returns
        -------
        `parfive.Results`

        Examples
        --------
        >>> from sunpy.net.vso.attrs import Time, Instrument
        >>> unifresp = Fido.search(Time('2012/3/4','2012/3/5'), Instrument('EIT'))  # doctest: +REMOTE_DATA
        >>> filepaths = Fido.fetch(unifresp)  # doctest: +SKIP

        If any downloads fail, they can be retried by passing the `parfive.Results` object back into ``fetch``.

        >>> filepaths = Fido.fetch(filepaths)  # doctest: +SKIP

        """

        if "wait" in kwargs:
            raise ValueError("wait is not a valid keyword argument to Fido.fetch.")

        if downloader is None:
            downloader = Downloader(max_conn=max_conn, progress=progress, overwrite=overwrite)
        elif not isinstance(downloader, Downloader):
            raise TypeError("The downloader argument must be a parfive.Downloader object.")

        # Handle retrying failed downloads
        retries = [isinstance(arg, Results) for arg in query_results]
        if all(retries):
            results = Results()
            for retry in query_results:
                dr = downloader.retry(retry)
                results.data += dr.data
                results._errors += dr._errors
            return results
        elif any(retries):
            raise TypeError("If any arguments to fetch are "
                            "`parfive.Results` objects, all arguments must be.")

        reslist = []
        for query_result in query_results:
            for block in query_result.responses:
                reslist.append(block.client.fetch(block, path=path,
                                                  downloader=downloader,
                                                  wait=False, **kwargs))

        results = Results()
        # Combine the results objects from all the clients into one Results
        # object.
        for result in reslist:
            if result is None:
                continue
            if not isinstance(result, Results):
                raise TypeError(
                    "If wait is False a client must return a parfive.Downloader and either None"
                    " or a parfive.Results object.")
            results.data += result.data
            results._errors += result.errors

        return results