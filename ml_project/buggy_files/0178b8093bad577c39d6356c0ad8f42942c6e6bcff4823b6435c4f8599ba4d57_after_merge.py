    def _main(self):
        if pyarrow is None:
            self._serial_type = dataserializer.SerialType.PICKLE
        else:
            self._serial_type = dataserializer.SerialType(options.client.serial_type.lower())

        args = self._args.copy()
        args['pyver'] = '.'.join(str(v) for v in sys.version_info[:3])
        args['pickle_protocol'] = self._pickle_protocol
        if pyarrow is not None:
            args['arrow_version'] = pyarrow.__version__

        if self._session_id is None:
            resp = self._req_session.post(self._endpoint + '/api/session', data=args)

            if resp.status_code >= 400:
                raise SystemError('Failed to create mars session: ' + resp.reason)
        else:
            resp = self._req_session.get(self._endpoint + '/api/session/' + self._session_id, params=args)
            if resp.status_code == 404:
                raise ValueError(f'The session with id = {self._session_id} doesn\'t exist')
            if resp.status_code >= 400:
                raise SystemError('Failed to check mars session.')

        content = json.loads(resp.text)
        self._session_id = content['session_id']
        self._pickle_protocol = content.get('pickle_protocol', pickle.HIGHEST_PROTOCOL)

        # as pyarrow will use pickle.HIGHEST_PROTOCOL to pickle, we need to use
        # SerialType.PICKLE when pickle protocol between client and server
        # does not agree with each other
        if not content.get('arrow_compatible') or self._pickle_protocol != pickle.HIGHEST_PROTOCOL:
            self._serial_type = dataserializer.SerialType.PICKLE