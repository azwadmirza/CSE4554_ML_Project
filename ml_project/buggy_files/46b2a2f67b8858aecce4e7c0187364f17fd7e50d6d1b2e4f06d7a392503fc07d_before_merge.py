    def _get_ready_pod_count(self, label_selector):
        query = self._core_api.list_namespaced_pod(
            namespace=self._namespace, label_selector=label_selector).to_dict()
        cnt = 0
        for el in query['items']:
            if el['status']['phase'] in ('Error', 'Failed'):
                raise SystemError(el['status']['message'])
            if 'status' not in el or 'conditions' not in el['status']:
                cnt += 1
            if any(cond['type'] == 'Ready' and cond['status'] == 'True'
                   for cond in el['status'].get('conditions') or ()):
                cnt += 1
        return cnt