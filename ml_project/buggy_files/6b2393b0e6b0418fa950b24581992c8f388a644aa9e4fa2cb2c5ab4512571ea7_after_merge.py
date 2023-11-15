def _playbook_items(pb_data: dict) -> ItemsView:
    if isinstance(pb_data, dict):
        return pb_data.items()
    elif not pb_data:
        return []
    else:
        # "if play" prevents failure if the play sequence containes None,
        # which is weird but currently allowed by Ansible
        # https://github.com/ansible-community/ansible-lint/issues/849
        return [item for play in pb_data if play for item in play.items()]