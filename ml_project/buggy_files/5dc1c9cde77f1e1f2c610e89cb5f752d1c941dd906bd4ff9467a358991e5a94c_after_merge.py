def create_permissions_mapping(User):
    """Create mapping permissions to users and potential new group name."""
    mapping = defaultdict(set)
    users = (
        User.objects.filter(user_permissions__isnull=False)
        .distinct()
        .prefetch_related("user_permissions")
    )
    for user in users:
        permissions = user.user_permissions.all().order_by("pk")
        perm_pks = tuple([perm.pk for perm in permissions])
        mapping[perm_pks].add(user.pk)
        user.user_permissions.clear()
    return mapping