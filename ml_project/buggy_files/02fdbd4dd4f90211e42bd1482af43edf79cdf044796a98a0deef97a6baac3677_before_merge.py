    def parse_folder(self, data_path, pattern='*.fif', n_jobs=1, mri_decim=2,
                     sort_sections=True, on_error='warn', image_format=None,
                     render_bem=True, verbose=None):
        r"""Render all the files in the folder.

        Parameters
        ----------
        data_path : str
            Path to the folder containing data whose HTML report will be
            created.
        pattern : str | list of str
            Filename pattern(s) to include in the report.
            Example: [\*raw.fif, \*ave.fif] will include Raw as well as Evoked
            files.
        %(n_jobs)s
        mri_decim : int
            Use this decimation factor for generating MRI/BEM images
            (since it can be time consuming).
        sort_sections : bool
            If True, sort sections in the order: raw -> events -> epochs
             -> evoked -> covariance -> trans -> mri -> forward -> inverse.
        on_error : str
            What to do if a file cannot be rendered. Can be 'ignore',
            'warn' (default), or 'raise'.
        image_format : str | None
            The image format to be used for the report, can be 'png' or 'svd'.
            None (default) will use the default specified during Report
            class construction.

            .. versionadded:: 0.15
        render_bem : bool
            If True (default), try to render the BEM.

            .. versionadded:: 0.16
        %(verbose_meth)s
        """
        image_format = _check_image_format(self, image_format)
        _check_option('on_error', on_error, ['ignore', 'warn', 'raise'])
        self._sort = sort_sections

        n_jobs = check_n_jobs(n_jobs)
        self.data_path = data_path

        if self.title is None:
            self.title = 'MNE Report for ...%s' % self.data_path[-20:]

        if not isinstance(pattern, (list, tuple)):
            pattern = [pattern]

        # iterate through the possible patterns
        fnames = list()
        for p in pattern:
            fnames.extend(sorted(_recursive_search(self.data_path, p)))

        if self.info_fname is not None:
            info = read_info(self.info_fname, verbose=False)
            sfreq = info['sfreq']
        else:
            # only warn if relevant
            if any(_endswith(fname, 'cov') for fname in fnames):
                warn('`info_fname` not provided. Cannot render '
                     '-cov.fif(.gz) files.')
            if any(_endswith(fname, 'trans') for fname in fnames):
                warn('`info_fname` not provided. Cannot render '
                     '-trans.fif(.gz) files.')
            if any(_endswith(fname, 'proj') for fname in fnames):
                warn('`info_fname` not provided. Cannot render '
                     '-proj.fif(.gz) files.')
            info, sfreq = None, None

        cov = None
        if self.cov_fname is not None:
            cov = read_cov(self.cov_fname)
        baseline = self.baseline

        # render plots in parallel; check that n_jobs <= # of files
        logger.info('Iterating over %s potential files (this may take some '
                    'time)' % len(fnames))
        use_jobs = min(n_jobs, max(1, len(fnames)))
        parallel, p_fun, _ = parallel_func(_iterate_files, use_jobs)
        r = parallel(p_fun(self, fname, info, cov, baseline, sfreq, on_error,
                           image_format, self.data_path)
                     for fname in np.array_split(fnames, use_jobs))
        htmls, report_fnames, report_sectionlabels = zip(*r)

        # combine results from n_jobs discarding plots not rendered
        self.html = [html for html in sum(htmls, []) if html is not None]
        self.fnames = [fname for fname in sum(report_fnames, []) if
                       fname is not None]
        self._sectionlabels = [slabel for slabel in
                               sum(report_sectionlabels, [])
                               if slabel is not None]

        # find unique section labels
        self.sections = sorted(set(self._sectionlabels))
        self._sectionvars = dict(zip(self.sections, self.sections))

        # render mri
        if render_bem:
            if self.subjects_dir is not None and self.subject is not None:
                logger.info('Rendering BEM')
                self.fnames.append('bem')
                self.add_bem_to_section(
                    self.subject, decim=mri_decim, n_jobs=n_jobs,
                    subjects_dir=self.subjects_dir)
            else:
                warn('`subjects_dir` and `subject` not provided. Cannot '
                     'render MRI and -trans.fif(.gz) files.')