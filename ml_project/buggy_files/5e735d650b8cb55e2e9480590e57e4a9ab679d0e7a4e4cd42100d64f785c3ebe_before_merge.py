def add_users_to_groups_based_on_users_permissions(apps, schema_editor):
    """Add every user to group with "user_permissions" if exists, else create new one.

    For each user, if the group with the exact scope of permissions exists,
    add the user to it, else create a new group with this scope of permissions
    and add the user to it.
    """
    User = apps.get_model("account", "User")
    Group = apps.get_model("auth", "Group")
    GroupData = namedtuple("GroupData", ["users", "group_name"])

    groups = Group.objects.all().prefetch_related("permissions")

    mapping = create_permissions_mapping(User, GroupData)
    for perms, group_data in mapping.items():
        group = get_group_with_given_permissions(perms, groups)
        users = group_data.users
        if group:
            group.user_set.add(*users)
            continue
        group = create_group_with_given_permissions(perms, group_data.group_name, Group)
        group.user_set.add(*users)