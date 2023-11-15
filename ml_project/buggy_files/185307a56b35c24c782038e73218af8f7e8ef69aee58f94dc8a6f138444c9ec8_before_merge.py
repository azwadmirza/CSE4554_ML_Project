def load_command_table(self, _):

    role_users_sdk = CliCommandType(
        operations_tmpl='azure.graphrbac.operations#UsersOperations.{}',
        client_factory=get_graph_client_users
    )

    role_group_sdk = CliCommandType(
        operations_tmpl='azure.graphrbac.operations#GroupsOperations.{}',
        client_factory=get_graph_client_groups
    )

    signed_in_users_sdk = CliCommandType(
        operations_tmpl='azure.graphrbac.operations#SignedInUserOperations.{}',
        client_factory=get_graph_client_signed_in_users
    )

    identity_sdk = CliCommandType(
        operations_tmpl='azure.mgmt.msi.operations#UserAssignedIdentitiesOperations.{}',
        client_factory=_msi_user_identities_operations
    )

    sp_sdk = CliCommandType(
        operations_tmpl='azure.graphrbac.operations.service_principals_operations#ServicePrincipalsOperations.{}',
        client_factory=get_graph_client_service_principals
    )

    role_custom = CliCommandType(operations_tmpl='azure.cli.command_modules.role.custom#{}')

    with self.command_group('role definition') as g:
        g.custom_command('list', 'list_role_definitions', table_transformer=transform_definition_list)
        g.custom_command('delete', 'delete_role_definition')
        g.custom_command('create', 'create_role_definition')
        g.custom_command('update', 'update_role_definition')

    with self.command_group('role assignment') as g:
        g.custom_command('delete', 'delete_role_assignments', validator=process_assignment_namespace)
        g.custom_command('list', 'list_role_assignments', validator=process_assignment_namespace, table_transformer=transform_assignment_list)
        g.custom_command('create', 'create_role_assignment', validator=process_assignment_namespace)
        g.custom_command('list-changelogs', 'list_role_assignment_change_logs')

    with self.command_group('ad app', client_factory=get_graph_client_applications, resource_type=PROFILE_TYPE,
                            exception_handler=graph_err_handler, transform=transform_graph_objects_with_cred) as g:
        g.custom_command('create', 'create_application')
        g.custom_command('delete', 'delete_application')
        g.custom_command('list', 'list_apps')
        g.custom_show_command('show', 'show_application')
        g.custom_command('permission grant', 'grant_application')
        g.custom_command('permission list', 'list_permissions')
        g.custom_command('permission add', 'add_permission')
        g.custom_command('permission delete', 'delete_permission')
        g.custom_command('permission list-grants', 'list_permission_grants')
        g.custom_command('permission admin-consent', 'admin_consent')
        g.generic_update_command('update', setter_name='patch_application', setter_type=role_custom,
                                 getter_name='show_application', getter_type=role_custom,
                                 custom_func_name='update_application', custom_func_type=role_custom)
        g.custom_command('credential reset', 'reset_service_principal_credential')
        g.custom_command('credential list', 'list_service_principal_credentials')
        g.custom_command('credential delete', 'delete_service_principal_credential')

    with self.command_group('ad app owner', exception_handler=graph_err_handler) as g:
        g.custom_command('list', 'list_application_owners')
        g.custom_command('add', 'add_application_owner')
        g.custom_command('remove', 'remove_application_owner')

    with self.command_group('ad sp', command_type=sp_sdk, resource_type=PROFILE_TYPE, exception_handler=graph_err_handler,
                            transform=transform_graph_objects_with_cred) as g:
        g.custom_command('create', 'create_service_principal')
        g.custom_command('delete', 'delete_service_principal')
        g.custom_command('list', 'list_sps', client_factory=get_graph_client_service_principals)
        g.custom_show_command('show', 'show_service_principal', client_factory=get_graph_client_service_principals)
        g.generic_update_command('update', getter_name='show_service_principal', getter_type=role_custom,
                                 setter_name='patch_service_principal', setter_type=role_custom)

    with self.command_group('ad sp owner', exception_handler=graph_err_handler) as g:
        g.custom_command('list', 'list_service_principal_owners')

    # RBAC related
    with self.command_group('ad sp', exception_handler=graph_err_handler, transform=transform_graph_objects_with_cred) as g:
        g.custom_command('create-for-rbac', 'create_service_principal_for_rbac')
        g.custom_command('credential reset', 'reset_service_principal_credential')
        g.custom_command('credential list', 'list_service_principal_credentials')
        g.custom_command('credential delete', 'delete_service_principal_credential')

    with self.command_group('ad user', role_users_sdk, exception_handler=graph_err_handler) as g:
        g.command('delete', 'delete')
        g.show_command('show', 'get')
        g.custom_command('list', 'list_users', client_factory=get_graph_client_users)
        g.custom_command('get-member-groups', 'get_user_member_groups')
        g.custom_command('create', 'create_user', client_factory=get_graph_client_users, doc_string_source='azure.graphrbac.models#UserCreateParameters')

    with self.command_group('ad signed-in-user', signed_in_users_sdk, exception_handler=graph_err_handler) as g:
        g.command('show', 'get')
        g.custom_command('list-owned-objects', 'list_owned_objects', client_factory=get_graph_client_signed_in_users)

    with self.command_group('ad group', role_group_sdk, exception_handler=graph_err_handler) as g:
        g.command('delete', 'delete')
        g.show_command('show', 'get')
        g.command('get-member-groups', 'get_member_groups')
        g.custom_command('list', 'list_groups', client_factory=get_graph_client_groups)
        g.custom_command('create', 'create_group')

    with self.command_group('ad group owner', exception_handler=graph_err_handler) as g:
        g.custom_command('list', 'list_group_owners')
        g.custom_command('add', 'add_group_owner')
        g.custom_command('remove', 'remove_group_owner')

    with self.command_group('ad group member', role_group_sdk, exception_handler=graph_err_handler) as g:
        g.command('list', 'get_group_members')
        g.command('add', 'add_member')
        g.command('remove', 'remove_member')
        g.custom_command('check', 'check_group_membership', client_factory=get_graph_client_groups)

    with self.command_group('identity', identity_sdk, min_api='2017-12-01') as g:
        g.command('create', 'create_or_update', validator=process_msi_namespace)
        g.show_command('show', 'get')
        g.command('delete', 'delete')
        g.custom_command('list', 'list_user_assigned_identities')
        g.command('list-operations', 'list', operations_tmpl='azure.mgmt.msi.operations.operations#Operations.{}', client_factory=_msi_operations_operations)