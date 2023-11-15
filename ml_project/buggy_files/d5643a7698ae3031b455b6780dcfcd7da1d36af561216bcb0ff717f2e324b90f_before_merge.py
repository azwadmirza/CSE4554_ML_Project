def api_github_v2(user_profile, event, payload, branches, default_stream,
                  commit_stream, issue_stream, topic_focus = None):
    # type: (UserProfile, Text, Mapping[Text, Any], Text, Text, Text, Text, Optional[Text]) -> Tuple[Text, Text, Text]
    """
    processes github payload with version 2 field specification
    `payload` comes in unmodified from github
    `default_stream` is set to what `stream` is in v1 above
    `commit_stream` and `issue_stream` fall back to `default_stream` if they are empty
    This and allowing alternative endpoints is what distinguishes v1 from v2 of the github configuration
    """
    target_stream = commit_stream if commit_stream else default_stream
    issue_stream = issue_stream if issue_stream else default_stream
    repository = payload['repository']
    topic_focus = topic_focus if topic_focus else repository['name']

    # Event Handlers
    if event == 'pull_request':
        subject = get_pull_request_or_issue_subject(repository, payload['pull_request'], 'PR')
        content = github_pull_request_content(payload)
    elif event == 'issues':
        # in v1, we assume that this stream exists since it is
        # deprecated and the few realms that use it already have the
        # stream
        target_stream = issue_stream
        subject = get_pull_request_or_issue_subject(repository, payload['issue'], 'Issue')
        content = github_issues_content(payload)
    elif event == 'issue_comment':
        # Comments on both issues and pull requests come in as issue_comment events
        issue = payload['issue']
        if 'pull_request' not in issue or issue['pull_request']['diff_url'] is None:
            # It's an issues comment
            target_stream = issue_stream
            type = 'Issue'
            subject = get_pull_request_or_issue_subject(repository, payload['issue'], type)
        else:
            # It's a pull request comment
            type = 'PR'
            subject = get_pull_request_or_issue_subject(repository, payload['issue'], type)

        content = github_object_commented_content(payload, type)

    elif event == 'push':
        subject, content = build_message_from_gitlog(user_profile, topic_focus,
                                                     payload['ref'], payload['commits'],
                                                     payload['before'], payload['after'],
                                                     payload['compare'],
                                                     payload['pusher']['name'],
                                                     forced=payload['forced'],
                                                     created=payload['created'])
    elif event == 'commit_comment':
        subject = topic_focus

        comment = payload.get('comment')
        action = u'[commented]({})'.format(comment['html_url'])
        content = get_commits_comment_action_message(
            comment['user']['login'],
            action,
            comment['html_url'].split('#', 1)[0],
            comment['commit_id'],
            comment['body'],
        )

    else:
        raise UnknownEventType(force_str(u'Event %s is unknown and cannot be handled' % (event,)))

    return target_stream, subject, content