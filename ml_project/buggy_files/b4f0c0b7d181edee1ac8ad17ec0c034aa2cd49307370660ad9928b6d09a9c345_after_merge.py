    def getChanges(self, request):
        """
        Reponds only to POST events and starts the build process

        :arguments:
            request
                the http request object
        """
        expected_secret = isinstance(self.options, dict) and self.options.get('secret')
        if expected_secret:
            received_secret = request.getHeader(_HEADER_GITLAB_TOKEN)
            received_secret = bytes2unicode(received_secret)
            if received_secret != expected_secret:
                raise ValueError("Invalid secret")
        try:
            content = request.content.read()
            payload = json.loads(bytes2unicode(content))
        except Exception as e:
            raise ValueError("Error loading JSON: " + str(e))
        event_type = request.getHeader(_HEADER_EVENT)
        event_type = bytes2unicode(event_type)
        # newer version of gitlab have a object_kind parameter,
        # which allows not to use the http header
        event_type = payload.get('object_kind', event_type)
        project = request.args.get('project', [''])[0]
        codebase = request.args.get('codebase', [None])[0]
        if event_type in ("push", "tag_push", "Push Hook"):
            user = payload['user_name']
            repo = payload['repository']['name']
            repo_url = payload['repository']['url']
            changes = self._process_change(
                payload, user, repo, repo_url, project, event_type, codebase=codebase)
        elif event_type == 'merge_request':
            changes = self._process_merge_request_change(
                payload, project, event_type, codebase=codebase)
        else:
            changes = []
        if changes:
            log.msg("Received {} changes from {} gitlab event".format(
                len(changes), event_type))
        return (changes, 'git')