    def authenticate_client(self, msg: Dict[str, Any]) -> None:
        if self.authenticated:
            self.session.send_message({'req_id': msg['req_id'], 'type': 'response',
                                       'response': {'result': 'error',
                                                    'msg': 'Already authenticated'}})
            return

        user_profile = get_user_profile(self.browser_session_id)
        if user_profile is None:
            raise JsonableError(_('Unknown or missing session'))
        self.session.user_profile = user_profile

        if 'csrf_token' not in msg['request']:
            # Debugging code to help with understanding #6961
            logging.error("Invalid websockets auth request: %s" % (msg['request'],))
            raise JsonableError(_('CSRF token entry missing from request'))
        if not _compare_salted_tokens(msg['request']['csrf_token'], self.csrf_token):
            raise JsonableError(_('CSRF token does not match that in cookie'))

        if 'queue_id' not in msg['request']:
            raise JsonableError(_("Missing 'queue_id' argument"))

        queue_id = msg['request']['queue_id']
        client = get_client_descriptor(queue_id)
        if client is None:
            raise BadEventQueueIdError(queue_id)

        if user_profile.id != client.user_profile_id:
            raise JsonableError(_("You are not the owner of the queue with id '%s'") % (queue_id,))

        self.authenticated = True
        register_connection(queue_id, self)

        response = {'req_id': msg['req_id'], 'type': 'response',
                    'response': {'result': 'success', 'msg': ''}}

        status_inquiries = msg['request'].get('status_inquiries')
        if status_inquiries is not None:
            results = {}  # type: Dict[str, Dict[str, str]]
            for inquiry in status_inquiries:
                status = redis_client.hgetall(req_redis_key(inquiry))  # type: Dict[bytes, bytes]
                if len(status) == 0:
                    result = {'status': 'not_received'}
                elif b'response' not in status:
                    result = {'status': status[b'status'].decode('utf-8')}
                else:
                    result = {'status': status[b'status'].decode('utf-8'),
                              'response': ujson.loads(status[b'response'])}
                results[str(inquiry)] = result
            response['response']['status_inquiries'] = results

        self.session.send_message(response)
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.remove_timeout(self.timeout_handle)