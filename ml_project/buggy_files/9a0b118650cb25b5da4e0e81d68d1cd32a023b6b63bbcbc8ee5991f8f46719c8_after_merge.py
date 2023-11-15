    def __init__(self, info, data, events, event_id=None, tmin=-0.2, tmax=0.5,
                 baseline=(None, 0), raw=None, picks=None, reject=None,
                 flat=None, decim=1, reject_tmin=None, reject_tmax=None,
                 detrend=None, proj=True, on_missing='raise',
                 preload_at_end=False, selection=None, drop_log=None,
                 filename=None, metadata=None, event_repeated='error',
                 verbose=None):  # noqa: D102
        self.verbose = verbose

        if events is not None:  # RtEpochs can have events=None
            events_type = type(events)
            with warnings.catch_warnings(record=True):
                warnings.simplefilter('ignore')  # deprecation for object array
                events = np.asarray(events)
            if not np.issubdtype(events.dtype, np.integer):
                raise TypeError('events should be a NumPy array of integers, '
                                f'got {events_type}')
            if events.ndim != 2 or events.shape[1] != 3:
                raise ValueError(
                    f'events must be of shape (N, 3), got {events.shape}')
            events_max = events.max()
            if events_max > INT32_MAX:
                raise ValueError(
                    f'events array values must not exceed {INT32_MAX}, '
                    f'got {events_max}')
        event_id = _check_event_id(event_id, events)
        self.event_id = event_id
        del event_id

        if events is not None:  # RtEpochs can have events=None
            for key, val in self.event_id.items():
                if val not in events[:, 2]:
                    msg = ('No matching events found for %s '
                           '(event id %i)' % (key, val))
                    _on_missing(on_missing, msg)

            # ensure metadata matches original events size
            self.selection = np.arange(len(events))
            self.events = events
            self.metadata = metadata
            del events

            values = list(self.event_id.values())
            selected = np.where(np.in1d(self.events[:, 2], values))[0]
            if selection is None:
                selection = selected
            else:
                selection = np.array(selection, int)
            if selection.shape != (len(selected),):
                raise ValueError('selection must be shape %s got shape %s'
                                 % (selected.shape, selection.shape))
            self.selection = selection
            if drop_log is None:
                self.drop_log = tuple(
                    () if k in self.selection else ('IGNORED',)
                    for k in range(max(len(self.events),
                                   max(self.selection) + 1)))
            else:
                self.drop_log = drop_log

            self.events = self.events[selected]

            self.events, self.event_id, self.selection, self.drop_log = \
                _handle_event_repeated(
                    self.events, self.event_id, event_repeated,
                    self.selection, self.drop_log)

            # then subselect
            sub = np.where(np.in1d(selection, self.selection))[0]
            if isinstance(metadata, list):
                metadata = [metadata[s] for s in sub]
            elif metadata is not None:
                metadata = metadata.iloc[sub]
            self.metadata = metadata
            del metadata

            n_events = len(self.events)
            if n_events > 1:
                if np.diff(self.events.astype(np.int64)[:, 0]).min() <= 0:
                    warn('The events passed to the Epochs constructor are not '
                         'chronologically ordered.', RuntimeWarning)

            if n_events > 0:
                logger.info('%d matching events found' % n_events)
            else:
                raise ValueError('No desired events found.')
        else:
            self.drop_log = list()
            self.selection = np.array([], int)
            self.metadata = metadata
            # do not set self.events here, let subclass do it

        if (detrend not in [None, 0, 1]) or isinstance(detrend, bool):
            raise ValueError('detrend must be None, 0, or 1')
        self.detrend = detrend

        self._raw = raw
        info._check_consistency()
        self.picks = _picks_to_idx(info, picks, none='all', exclude=(),
                                   allow_empty=False)
        self.info = pick_info(info, self.picks)
        del info
        self._current = 0

        if data is None:
            self.preload = False
            self._data = None
            self._do_baseline = True
        else:
            assert decim == 1
            if data.ndim != 3 or data.shape[2] != \
                    round((tmax - tmin) * self.info['sfreq']) + 1:
                raise RuntimeError('bad data shape')
            if data.shape[0] != len(self.events):
                raise ValueError(
                    'The number of epochs and the number of events must match')
            self.preload = True
            self._data = data
            self._do_baseline = False
        self._offset = None

        if tmin > tmax:
            raise ValueError('tmin has to be less than or equal to tmax')

        # Handle times
        sfreq = float(self.info['sfreq'])
        start_idx = int(round(tmin * sfreq))
        self._raw_times = np.arange(start_idx,
                                    int(round(tmax * sfreq)) + 1) / sfreq
        self._set_times(self._raw_times)

        # check reject_tmin and reject_tmax
        if reject_tmin is not None:
            if (np.isclose(reject_tmin, tmin)):
                # adjust for potential small deviations due to sampling freq
                reject_tmin = self.tmin
            elif reject_tmin < tmin:
                raise ValueError(f'reject_tmin needs to be None or >= tmin '
                                 f'(got {reject_tmin})')

        if reject_tmax is not None:
            if (np.isclose(reject_tmax, tmax)):
                # adjust for potential small deviations due to sampling freq
                reject_tmax = self.tmax
            elif reject_tmax > tmax:
                raise ValueError(f'reject_tmax needs to be None or <= tmax '
                                 f'(got {reject_tmax})')

        if (reject_tmin is not None) and (reject_tmax is not None):
            if reject_tmin >= reject_tmax:
                raise ValueError(f'reject_tmin ({reject_tmin}) needs to be '
                                 f' < reject_tmax ({reject_tmax})')

        self.reject_tmin = reject_tmin
        self.reject_tmax = reject_tmax

        # decimation
        self._decim = 1
        self.decimate(decim)

        # baseline correction: replace `None` tuple elements  with actual times
        self.baseline = _check_baseline(baseline, times=self.times,
                                        sfreq=self.info['sfreq'])
        if self.baseline is not None and self.baseline != baseline:
            logger.info(f'Setting baseline interval to '
                        f'[{self.baseline[0]}, {self.baseline[1]}] sec')

        logger.info(_log_rescale(self.baseline))

        # setup epoch rejection
        self.reject = None
        self.flat = None
        self._reject_setup(reject, flat)

        # do the rest
        valid_proj = [True, 'delayed', False]
        if proj not in valid_proj:
            raise ValueError('"proj" must be one of %s, not %s'
                             % (valid_proj, proj))
        if proj == 'delayed':
            self._do_delayed_proj = True
            logger.info('Entering delayed SSP mode.')
        else:
            self._do_delayed_proj = False
        activate = False if self._do_delayed_proj else proj
        self._projector, self.info = setup_proj(self.info, False,
                                                activate=activate)
        if preload_at_end:
            assert self._data is None
            assert self.preload is False
            self.load_data()  # this will do the projection
        elif proj is True and self._projector is not None and data is not None:
            # let's make sure we project if data was provided and proj
            # requested
            # we could do this with np.einsum, but iteration should be
            # more memory safe in most instances
            for ii, epoch in enumerate(self._data):
                self._data[ii] = np.dot(self._projector, epoch)
        self._filename = str(filename) if filename is not None else filename
        self._check_consistency()