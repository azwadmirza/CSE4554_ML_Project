def get_push_commits_event_message(user_name, compare_url, branch_name, commits_data, is_truncated=False):
    # type: (Text, Optional[Text], Text, List[Dict[str, Any]], Optional[bool]) -> Text
    pushed_message_template = PUSH_PUSHED_TEXT_WITH_URL if compare_url else PUSH_PUSHED_TEXT_WITHOUT_URL

    pushed_text_message = pushed_message_template.format(
        compare_url=compare_url,
        number_of_commits=len(commits_data),
        commit_or_commits=COMMIT_OR_COMMITS.format(u's' if len(commits_data) > 1 else u''))

    committers_items = get_all_committers(commits_data)  # type: List[Tuple[str, int]]
    if len(committers_items) == 1 and user_name == committers_items[0][0]:
        return PUSH_COMMITS_MESSAGE_TEMPLATE_WITHOUT_COMMITTERS.format(
            user_name=user_name,
            pushed_text=pushed_text_message,
            branch_name=branch_name,
            commits_data=get_commits_content(commits_data, is_truncated),
        ).rstrip()
    else:
        committers_details = "{} ({})".format(*committers_items[0])

        for name, number_of_commits in committers_items[1:-1]:
            committers_details = "{}, {} ({})".format(committers_details, name, number_of_commits)

        if len(committers_items) > 1:
            committers_details = "{} and {} ({})".format(committers_details, *committers_items[-1])

        return PUSH_COMMITS_MESSAGE_TEMPLATE_WITH_COMMITTERS.format(
            user_name=user_name,
            pushed_text=pushed_text_message,
            branch_name=branch_name,
            committers_details=PUSH_COMMITS_MESSAGE_EXTENSION.format(committers_details),
            commits_data=get_commits_content(commits_data, is_truncated),
        ).rstrip()