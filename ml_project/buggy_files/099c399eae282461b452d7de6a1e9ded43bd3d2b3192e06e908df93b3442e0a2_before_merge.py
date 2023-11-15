    def addChange(self, who=None, files=None, comments=None, **kwargs):
        # deprecated in 0.9.0; will be removed in 1.0.0
        log.msg("WARNING: change source is using deprecated "
                "self.master.addChange method; this method will disappear in "
                "Buildbot-1.0.0")
        # handle positional arguments
        kwargs['who'] = who
        kwargs['files'] = files
        kwargs['comments'] = comments

        def handle_deprec(oldname, newname):
            if oldname in kwargs:
                old = kwargs.pop(oldname)
                if old is not None:
                    if kwargs.get(newname) is None:
                        log.msg("WARNING: change source is using deprecated "
                                "addChange parameter '%s'" % oldname)
                        return old
                    raise TypeError("Cannot provide '%s' and '%s' to addChange"
                                    % (oldname, newname))
            return kwargs.get(newname)

        kwargs['author'] = handle_deprec("who", "author")
        kwargs['when_timestamp'] = handle_deprec("when", "when_timestamp")

        # timestamp must be an epoch timestamp now
        if isinstance(kwargs.get('when_timestamp'), datetime.datetime):
            kwargs['when_timestamp'] = datetime2epoch(kwargs['when_timestamp'])

        # unicodify stuff
        for k in ('comments', 'author', 'revision', 'branch', 'category',
                  'revlink', 'repository', 'codebase', 'project'):
            if k in kwargs:
                kwargs[k] = ascii2unicode(kwargs[k])
        if kwargs.get('files'):
            kwargs['files'] = [ascii2unicode(f)
                               for f in kwargs['files']]
        if kwargs.get('properties'):
            kwargs['properties'] = dict((ascii2unicode(k), v)
                                        for k, v in iteritems(kwargs['properties']))

        # pass the converted call on to the data API
        changeid = yield self.data.updates.addChange(**kwargs)

        # and turn that changeid into a change object, since that's what
        # callers expected (and why this method was deprecated)
        chdict = yield self.db.changes.getChange(changeid)
        change = yield changes.Change.fromChdict(self, chdict)
        defer.returnValue(change)