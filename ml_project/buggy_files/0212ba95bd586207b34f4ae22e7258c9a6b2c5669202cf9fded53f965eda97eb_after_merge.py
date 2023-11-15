    def _check_response_finished(self, graph_url, timeout=None):
        import requests
        try:
            resp = self._req_session.get(graph_url, params={'wait_timeout': timeout})
        except requests.ConnectionError as ex:
            err_msg = str(ex)
            if 'ConnectionResetError' in err_msg or 'Connection refused' in err_msg or \
                    'Connection aborted' in err_msg:
                return False
            raise

        if resp.status_code == 504:
            logging.debug('Gateway Time-out, try again')
            return False
        if resp.status_code >= 400:
            raise SystemError(f'Failed to obtain execution status. Code: {resp.status_code}, '
                              f'Reason: {resp.reason}, Content:\n{resp.text}')

        resp_json = self._handle_json_response(resp, raises=False)
        if resp_json['state'] == 'succeeded':
            return True
        elif resp_json['state'] in ('running', 'preparing'):
            return False
        elif resp_json['state'] in ('cancelled', 'cancelling'):
            raise ExecutionInterrupted
        elif resp_json['state'] == 'failed':
            if 'exc_info' in resp_json:
                exc_info = pickle.loads(base64.b64decode(resp_json['exc_info']))
                exc = exc_info[1].with_traceback(exc_info[2])
                raise ExecutionFailed('Graph execution failed.') from exc
            else:
                raise ExecutionFailed('Graph execution failed with unknown reason.')
        raise ExecutionStateUnknown('Unknown graph execution state ' + resp_json['state'])