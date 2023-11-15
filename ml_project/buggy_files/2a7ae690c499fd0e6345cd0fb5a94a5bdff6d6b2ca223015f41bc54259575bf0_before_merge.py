    def _init(self):
        endpoint, kwargs = self._endpoint, self._kws
        if self._backend is None:
            if endpoint is not None:
                if 'http' in endpoint:
                    # connect to web
                    self._init_web_session(endpoint, **kwargs)
                else:
                    # connect to local cluster
                    self._init_cluster_session(endpoint, **kwargs)
            else:
                try:
                    endpoint = os.environ['MARS_SCHEDULER_ADDRESS']
                    session_id = os.environ.get('MARS_SESSION_ID', None)
                    kwargs['session_id'] = session_id
                    self._init_cluster_session(endpoint, **kwargs)
                except KeyError:
                    self._init_local_session(**kwargs)
        elif self._backend == 'ray':
            self._init_ray_session(**kwargs)