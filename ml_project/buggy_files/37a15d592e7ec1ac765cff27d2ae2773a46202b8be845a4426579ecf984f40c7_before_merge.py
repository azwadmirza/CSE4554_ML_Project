def create_group_with_given_permissions(perm_pks, group_name, Group):
    """Create new group with given set of permissions."""
    group = Group.objects.create(name=group_name)
    group.permissions.add(*perm_pks)
    return group