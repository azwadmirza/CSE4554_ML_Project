    def issues(self):
        email = self.username
        # TODO -- doing something with blockedby would be nice.

        if self.query_url:
            query = self.bz.url_to_query(self.query_url)
            query['column_list'] = self.COLUMN_LIST
        else:
            query = dict(
                column_list=self.COLUMN_LIST,
                bug_status=self.open_statuses,
                email1=email,
                emailreporter1=1,
                emailassigned_to1=1,
                emailqa_contact1=1,
                emailtype1="substring",
            )

            if not self.ignore_cc:
                query['emailcc1'] = 1

        if self.advanced:
            # Required for new bugzilla
            # https://bugzilla.redhat.com/show_bug.cgi?id=825370
            query['query_format'] = 'advanced'

        bugs = self.bz.query(query)

        if self.include_needinfos:
            needinfos = self.bz.query(dict(
                column_list=self.COLUMN_LIST,
                quicksearch='flag:needinfo?%s' % email,
            ))
            exists = [b.id for b in bugs]
            for bug in needinfos:
                # don't double-add bugs that have already been found
                if bug.id in exists:
                    continue
                bugs.append(bug)

        # Convert to dicts
        bugs = [
            dict(
                ((col, _get_bug_attr(bug, col)) for col in self.COLUMN_LIST)
            ) for bug in bugs
        ]

        issues = [(self.target, bug) for bug in bugs]
        log.debug(" Found %i total.", len(issues))

        # Build a url for each issue
        base_url = "https://%s/show_bug.cgi?id=" % (self.base_uri)
        for tag, issue in issues:
            issue_obj = self.get_issue_for_record(issue)
            extra = {
                'url': base_url + six.text_type(issue['id']),
                'annotations': self.annotations(tag, issue, issue_obj),
            }

            needinfos = [f for f in issue['flags'] if (
                f['name'] == 'needinfo' and
                f['status'] == '?' and
                f.get('requestee', self.username) == self.username
            )]
            if needinfos:
                last_mod = needinfos[0]['modification_date']
                # convert from RPC DateTime string to datetime.datetime object
                mod_date = datetime.datetime.fromtimestamp(
                    time.mktime(last_mod.timetuple()))

                extra['needinfo_since'] = pytz.UTC.localize(mod_date).isoformat()

            if issue['status'] == 'ASSIGNED':
                extra['assigned_on'] = self._get_assigned_date(issue)
            else:
                extra['assigned_on'] = None

            issue_obj.update_extra(extra)
            yield issue_obj