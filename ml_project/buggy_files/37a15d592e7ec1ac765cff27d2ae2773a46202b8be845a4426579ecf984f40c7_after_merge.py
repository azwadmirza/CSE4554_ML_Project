def create_group_with_given_permissions(perm_pks, counter, Group):
    """Create new group with given set of permissions."""
    group_name = f"Group {counter:03d}"
    group = Group.objects.create(name=group_name)
    group.permissions.add(*perm_pks)
    return group