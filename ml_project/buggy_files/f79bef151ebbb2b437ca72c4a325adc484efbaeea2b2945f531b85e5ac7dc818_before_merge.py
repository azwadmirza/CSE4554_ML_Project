    def __init__(self, input_fname, eog=(),
                 preload=False, uint16_codec=None, verbose=None):  # noqa: D102
        eeg = _check_load_mat(input_fname, uint16_codec)
        if eeg.trials != 1:
            raise TypeError('The number of trials is %d. It must be 1 for raw'
                            ' files. Please use `mne.io.read_epochs_eeglab` if'
                            ' the .set file contains epochs.' % eeg.trials)

        last_samps = [eeg.pnts - 1]
        info, eeg_montage, update_ch_names = _get_info(eeg, eog=eog)

        # read the data
        if isinstance(eeg.data, str):
            data_fname = _check_fname(input_fname, eeg.data)
            logger.info('Reading %s' % data_fname)

            super(RawEEGLAB, self).__init__(
                info, preload, filenames=[data_fname], last_samps=last_samps,
                orig_format='double', verbose=verbose)
        else:
            if preload is False or isinstance(preload, str):
                warn('Data will be preloaded. preload=False or a string '
                     'preload is not supported when the data is stored in '
                     'the .set file')
            # can't be done in standard way with preload=True because of
            # different reading path (.set file)
            if eeg.nbchan == 1 and len(eeg.data.shape) == 1:
                n_chan, n_times = [1, eeg.data.shape[0]]
            else:
                n_chan, n_times = eeg.data.shape
            data = np.empty((n_chan, n_times), dtype=float)
            data[:n_chan] = eeg.data
            data *= CAL
            super(RawEEGLAB, self).__init__(
                info, data, filenames=[input_fname], last_samps=last_samps,
                orig_format='double', verbose=verbose)

        # create event_ch from annotations
        annot = read_annotations(input_fname)
        self.set_annotations(annot)
        _check_boundary(annot, None)

        _set_dig_montage_in_init(self, eeg_montage)

        latencies = np.round(annot.onset * self.info['sfreq'])
        _check_latencies(latencies)