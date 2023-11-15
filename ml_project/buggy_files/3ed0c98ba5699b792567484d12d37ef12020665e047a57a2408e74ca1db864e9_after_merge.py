def build_message_from_gitlog(user_profile, name, ref, commits, before, after, url, pusher, forced=None, created=None, deleted=False):
    # type: (UserProfile, Text, Text, List[Dict[str, str]], Text, Text, Text, Text, Optional[Text], Optional[Text], Optional[bool]) -> Tuple[Text, Text]
    short_ref = re.sub(r'^refs/heads/', '', ref)
    subject = SUBJECT_WITH_BRANCH_TEMPLATE.format(repo=name, branch=short_ref)

    if re.match(r'^0+$', after):
        content = get_remove_branch_event_message(pusher, short_ref)
    # 'created' and 'forced' are github flags; the second check is for beanstalk
    elif (forced and not created) or (forced is None and len(commits) == 0):
        content = get_force_push_commits_event_message(pusher, url, short_ref, after[:7])
    else:
        commits = _transform_commits_list_to_common_format(commits)
        content = get_push_commits_event_message(pusher, url, short_ref, commits, deleted=deleted)

    return subject, content