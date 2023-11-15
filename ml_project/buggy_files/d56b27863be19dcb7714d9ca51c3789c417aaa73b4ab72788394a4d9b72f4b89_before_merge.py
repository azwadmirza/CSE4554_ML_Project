    def fetch(self, query_response, path=None, methods=None, site=None,
              progress=True, overwrite=False, downloader=None, wait=True):
        """
        Download data specified in the query_response.

        Parameters
        ----------
        query_response : sunpy.net.vso.QueryResponse
            QueryResponse containing the items to be downloaded.

        path : str
            Specify where the data is to be downloaded. Can refer to arbitrary
            fields of the QueryResponseItem (instrument, source, time, ...) via
            string formatting, moreover the file-name of the file downloaded can
            be referred to as file, e.g.
            "{source}/{instrument}/{time.start}/{file}".

        methods : {list of str}
            Download methods, defaults to URL-FILE_Rice then URL-FILE.
            Methods are a concatenation of one PREFIX followed by any number of
            SUFFIXES i.e. `PREFIX-SUFFIX_SUFFIX2_SUFFIX3`.
            The full list of
            `PREFIXES <https://sdac.virtualsolar.org/cgi/show_details?keyword=METHOD_PREFIX>`_
            and `SUFFIXES <https://sdac.virtualsolar.org/cgi/show_details?keyword=METHOD_SUFFIX>`_
            are listed on the VSO site.

        site : str
            There are a number of caching mirrors for SDO and other
            instruments, some available ones are listed below.

            =============== ========================================================
            NSO             National Solar Observatory, Tucson (US)
            SAO  (aka CFA)  Smithonian Astronomical Observatory, Harvard U. (US)
            SDAC (aka GSFC) Solar Data Analysis Center, NASA/GSFC (US)
            ROB             Royal Observatory of Belgium (Belgium)
            MPS             Max Planck Institute for Solar System Research (Germany)
            UCLan           University of Central Lancashire (UK)
            IAS             Institut Aeronautique et Spatial (France)
            KIS             Kiepenheuer-Institut fur Sonnenphysik Germany)
            NMSU            New Mexico State University (US)
            =============== ========================================================

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
            The download manager to use.

        wait : `bool`, optional
           If `False` ``downloader.download()`` will not be called. Only has
           any effect if `downloader` is not `None`.

        Returns
        -------
        out : `parfive.Results`
            Object that supplies a list of filenames and any errors.

        Examples
        --------
        >>> files = fetch(qr) # doctest:+SKIP
        """
        if path is None:
            path = os.path.join(config.get('downloads', 'download_dir'),
                                '{file}')
        elif isinstance(path, str) and '{file}' not in path:
            path = os.path.join(path, '{file}')
        path = os.path.expanduser(path)

        dl_set = True
        if not downloader:
            dl_set = False
            downloader = Downloader(progress=progress)

        fileids = VSOClient.by_fileid(query_response)
        if not fileids:
            return downloader.download()
        # Adding the site parameter to the info
        info = {}
        if site is not None:
            info['site'] = site

        VSOGetDataResponse = self.api.get_type("VSO:VSOGetDataResponse")

        data_request = self.make_getdatarequest(query_response, methods, info)
        data_response = VSOGetDataResponse(self.api.service.GetData(data_request))

        err_results = self.download_all(data_response, methods, downloader, path, fileids)

        if dl_set and not wait:
            return err_results

        results = downloader.download()
        results += err_results
        results._errors += err_results.errors
        return results