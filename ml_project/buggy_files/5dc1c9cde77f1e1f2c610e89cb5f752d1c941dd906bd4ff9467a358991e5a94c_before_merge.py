def create_permissions_mapping(User, GroupData):
    """Create mapping permissions to users and potential new group name."""
    mapping = {}
    users = User.objects.filter(user_permissions__isnull=False).prefetch_related(
        "user_permissions"
    )
    for user in users:
        permissions = user.user_permissions.all()
        perm_pks = (perm.pk for perm in permissions)
        if perm_pks not in mapping:
            group_name = create_group_name(permissions)
            mapping[perm_pks] = GroupData({user.pk}, group_name)
        else:
            mapping[perm_pks].users.add(user.pk)
        user.user_permissions.clear()
    return mapping