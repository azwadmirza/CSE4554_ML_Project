    def GET(self, jid=None, timeout=''):
        '''
        A convenience URL for getting lists of previously run jobs or getting
        the return from a single job

        .. http:get:: /jobs/(jid)

            List jobs or show a single job from the job cache.

            :reqheader X-Auth-Token: |req_token|
            :reqheader Accept: |req_accept|

            :status 200: |200|
            :status 401: |401|
            :status 406: |406|

        **Example request:**

        .. code-block:: bash

            curl -i localhost:8000/jobs

        .. code-block:: http

            GET /jobs HTTP/1.1
            Host: localhost:8000
            Accept: application/x-yaml

        **Example response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Length: 165
            Content-Type: application/x-yaml

            return:
            - '20121130104633606931':
                Arguments:
                - '3'
                Function: test.fib
                Start Time: 2012, Nov 30 10:46:33.606931
                Target: jerry
                Target-type: glob

        **Example request:**

        .. code-block:: bash

            curl -i localhost:8000/jobs/20121130104633606931

        .. code-block:: http

            GET /jobs/20121130104633606931 HTTP/1.1
            Host: localhost:8000
            Accept: application/x-yaml

        **Example response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Length: 73
            Content-Type: application/x-yaml

            info:
            - Arguments:
                - '3'
                Function: test.fib
                Minions:
                - jerry
                Start Time: 2012, Nov 30 10:46:33.606931
                Target: '*'
                Target-type: glob
                User: saltdev
                jid: '20121130104633606931'
            return:
            - jerry:
                - - 0
                - 1
                - 1
                - 2
                - 6.9141387939453125e-06
        '''
        lowstate = {'client': 'runner'}
        if jid:
            lowstate.update({'fun': 'jobs.list_job', 'jid': jid})
        else:
            lowstate.update({'fun': 'jobs.list_jobs'})

        cherrypy.request.lowstate = [lowstate]
        job_ret_info = list(self.exec_lowstate(
            token=cherrypy.session.get('token')))

        ret = {}
        if jid:
            ret['info'] = [job_ret_info[0]]
            minion_ret = {}
            returns = job_ret_info[0].get('Result')
            for minion in returns.keys():
                if u'return' in returns[minion]:
                    minion_ret[minion] = returns[minion].get(u'return')
                else:
                    minion_ret[minion] = returns[minion].get('return')
            ret['return'] = [minion_ret]
        else:
            ret['return'] = [job_ret_info[0]]

        return ret