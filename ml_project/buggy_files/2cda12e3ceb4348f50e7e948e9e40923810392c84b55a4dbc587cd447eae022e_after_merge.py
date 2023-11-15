    def submit_errors(self):  # pylint: disable=too-many-branches,too-many-locals
        """Submit errors to github."""
        submitter_result = ''
        issue_id = None

        if not (sickbeard.GIT_USERNAME and sickbeard.GIT_PASSWORD and
                sickbeard.DEBUG and len(classes.ErrorViewer.errors) > 0):
            submitter_result = ('Please set your GitHub username and password in the config and enable debug. '
                                'Unable to submit issue ticket to GitHub!')
            return submitter_result, issue_id

        try:
            from sickbeard.versionChecker import CheckVersion
            checkversion = CheckVersion()
            checkversion.check_for_new_version()
            commits_behind = checkversion.updater.get_num_commits_behind()
        except Exception:  # pylint: disable=broad-except
            submitter_result = 'Could not check if your SickRage is updated, unable to submit issue ticket to GitHub!'
            return submitter_result, issue_id

        if commits_behind is None or commits_behind > 0:
            submitter_result = ('Please update SickRage, '
                                'unable to submit issue ticket to GitHub with an outdated version!')
            return submitter_result, issue_id

        if self.submitter_running:
            submitter_result = 'Issue submitter is running, please wait for it to complete'
            return submitter_result, issue_id

        self.submitter_running = True

        gh_org = sickbeard.GIT_ORG
        gh_repo = sickbeard.GIT_REPO

        git = Github(login_or_token=sickbeard.GIT_USERNAME, password=sickbeard.GIT_PASSWORD, user_agent='SickRage')

        try:
            # read log file
            log_data = None

            if ek(os.path.isfile, self.log_file):
                with io.open(self.log_file, encoding='utf-8') as log_f:
                    log_data = log_f.readlines()

            for i in range(1, int(sickbeard.LOG_NR)):
                f_name = '%s.%i' % (self.log_file, i)
                if ek(os.path.isfile, f_name) and (len(log_data) <= 500):
                    with io.open(f_name, encoding='utf-8') as log_f:
                        log_data += log_f.readlines()

            log_data = [line for line in reversed(log_data)]

            # parse and submit errors to issue tracker
            for cur_error in sorted(classes.ErrorViewer.errors, key=lambda error: error.time, reverse=True)[:500]:
                try:
                    title_error = ss(str(cur_error.title))
                    if not title_error or title_error == 'None':
                        # Match: SEARCHQUEUE-FORCEDSEARCH-262407 :: [HDTorrents] :: [ea015c6] Error1
                        # Match: MAIN :: [ea015c6] Error1
                        # We only need Error title
                        title_error = re.match(r'^(?:.*)(?:\[[\w]{7}\]\s*)(.*)$', ss(cur_error.message)).group(1)

                    if len(title_error) > 1000:
                        title_error = title_error[0:1000]

                except Exception as err_msg:  # pylint: disable=broad-except
                    self.log('Unable to get error title : %s' % ex(err_msg), ERROR)
                    continue

                gist = None
                regex = r'^(%s)\s*([A-Z]+)\s*(.*)\s*::\s*(\[[\w]{7}\])\s*(.*)$' % cur_error.time
                for i, data in enumerate(log_data):
                    match = re.match(regex, data)
                    if match:
                        level = match.group(2)
                        if LOGGING_LEVELS[level] == ERROR:
                            paste_data = ''.join(log_data[i:i + 50])
                            if paste_data:
                                gist = git.get_user().create_gist(False, {'sickrage.log': InputFileContent(paste_data)})
                            break
                    else:
                        gist = 'No ERROR found'

                try:
                    locale_name = locale.getdefaultlocale()[1]
                except Exception:  # pylint: disable=broad-except
                    locale_name = 'unknown'

                if gist and gist != 'No ERROR found':
                    log_link = 'Link to Log: %s' % gist.html_url
                else:
                    log_link = 'No Log available with ERRORS:'

                msg = [
                    '### INFO',
                    'Python Version: **%s**' % sys.version[:120].replace('\n', ''),
                    'Operating System: **%s**' % platform.platform(),
                    'Locale: %s' % locale_name,
                    'Branch: **%s**' % sickbeard.BRANCH,
                    'Commit: PyMedusa/SickRage@%s' % sickbeard.CUR_COMMIT_HASH,
                    log_link,
                    '### ERROR',
                    '```',
                    cur_error.message,
                    '```',
                    '---',
                    '_STAFF NOTIFIED_: @pymedusa/support @pymedusa/moderators',
                ]

                message = '\n'.join(msg)
                title_error = '[APP SUBMITTED]: %s' % title_error
                reports = git.get_organization(gh_org).get_repo(gh_repo).get_issues(state='all')

                def is_ascii_error(title):
                    # [APP SUBMITTED]:
                    #   'ascii' codec can't encode characters in position 00-00: ordinal not in range(128)
                    # [APP SUBMITTED]:
                    #   'charmap' codec can't decode byte 0x00 in position 00: character maps to <undefined>
                    return re.search(r'.* codec can\'t .*code .* in position .*:', title) is not None

                def is_malformed_error(title):
                    # [APP SUBMITTED]: not well-formed (invalid token): line 0, column 0
                    return re.search(r'.* not well-formed \(invalid token\): line .* column .*', title) is not None

                ascii_error = is_ascii_error(title_error)
                malformed_error = is_malformed_error(title_error)

                issue_found = False
                for report in reports:
                    if title_error.rsplit(' :: ')[-1] in report.title or (
                            malformed_error and is_malformed_error(report.title)) or (
                            ascii_error and is_ascii_error(report.title)):

                        issue_id = report.number
                        if not report.raw_data['locked']:
                            if report.create_comment(message):
                                submitter_result = 'Commented on existing issue #%s successfully!' % issue_id
                            else:
                                submitter_result = 'Failed to comment on found issue #%s!' % issue_id
                        else:
                            submitter_result = ('Issue #%s is locked, '
                                                'check GitHub to find info about the error.' % issue_id)

                        issue_found = True
                        break

                if not issue_found:
                    issue = git.get_organization(gh_org).get_repo(gh_repo).create_issue(title_error, message)
                    if issue:
                        issue_id = issue.number
                        submitter_result = 'Your issue ticket #%s was submitted successfully!' % issue_id
                    else:
                        submitter_result = 'Failed to create a new issue!'

                if issue_id and cur_error in classes.ErrorViewer.errors:
                    # clear error from error list
                    classes.ErrorViewer.errors.remove(cur_error)
        except (GithubException.BadCredentialsException, GithubException.RateLimitExceededException) as e:
            self.log('Error while accessing github: {0}'.format(e), WARNING)
        except Exception:  # pylint: disable=broad-except
            self.log(traceback.format_exc(), ERROR)
            submitter_result = 'Exception generated in issue submitter, please check the log'
            issue_id = None
        finally:
            self.submitter_running = False

        return submitter_result, issue_id