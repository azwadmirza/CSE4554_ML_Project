def get_push_commits_body(payload):
    # type: (Dict[str, Any]) -> Text
    commits_data = [{
        'name': (commit.get('author').get('username') or
                 commit.get('author').get('name')),
        'sha': commit['id'],
        'url': commit['url'],
        'message': commit['message']
    } for commit in payload['commits']]
    return get_push_commits_event_message(
        get_sender_name(payload),
        payload['compare'],
        get_branch_name_from_ref(payload['ref']),
        commits_data,
        deleted=payload['deleted']
    )