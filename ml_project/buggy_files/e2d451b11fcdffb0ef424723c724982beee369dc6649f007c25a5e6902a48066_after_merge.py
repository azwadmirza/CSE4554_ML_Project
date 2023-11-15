    def _update(self, id, body, state, **kwargs):
        """Update state in a conflict free manner.

        If state is defined (not None), this will not update ES server if either:
        * existing state is success
        * existing state is a ready state and current state in not a ready state

        This way, a Retry state cannot override a Success or Failure, and chord_unlock
        will not retry indefinitely.
        """
        body = {bytes_to_str(k): v for k, v in items(body)}

        try:
            res_get = self._get(key=id)
            if not res_get.get('found'):
                return self._index(id, body, **kwargs)
            # document disappeared between index and get calls.
        except elasticsearch.exceptions.NotFoundError:
            return self._index(id, body, **kwargs)

        try:
            meta_present_on_backend = self.decode_result(res_get['_source']['result'])
        except (TypeError, KeyError):
            pass
        else:
            if meta_present_on_backend['status'] == states.SUCCESS:
                # if stored state is already in success, do nothing
                return {'result': 'noop'}
            elif meta_present_on_backend['status'] in states.READY_STATES and state in states.UNREADY_STATES:
                # if stored state is in ready state and current not, do nothing
                return {'result': 'noop'}

        # get current sequence number and primary term
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/optimistic-concurrency-control.html
        seq_no = res_get.get('_seq_no', 1)
        prim_term = res_get.get('_primary_term', 1)

        # try to update document with current seq_no and primary_term
        res = self.server.update(
            id=bytes_to_str(id),
            index=self.index,
            doc_type=self.doc_type,
            body={'doc': body},
            params={'if_primary_term': prim_term, 'if_seq_no': seq_no},
            **kwargs
        )
        # result is elastic search update query result
        # noop = query did not update any document
        # updated = at least one document got updated
        if res['result'] == 'noop':
            raise elasticsearch.exceptions.ConflictError(409, 'conflicting update occurred concurrently', {})
        return res