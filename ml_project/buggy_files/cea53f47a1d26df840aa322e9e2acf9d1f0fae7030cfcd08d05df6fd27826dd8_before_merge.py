    def setup_rbac(self) -> None:
        """
        Setup the client application for the OneFuzz instance.

        By default, Service Principals do not have access to create
        client applications in AAD.
        """
        if self.results["client_id"] and self.results["client_secret"]:
            logger.info("using existing client application")
            return

        client = get_client_from_cli_profile(GraphRbacManagementClient)
        logger.info("checking if RBAC already exists")

        try:
            existing = list(
                client.applications.list(
                    filter="displayName eq '%s'" % self.application_name
                )
            )
        except GraphErrorException:
            logger.error("unable to query RBAC. Provide client_id and client_secret")
            sys.exit(1)

        app_roles = [
            AppRole(
                allowed_member_types=["Application"],
                display_name=OnefuzzAppRole.CliClient.value,
                id=str(uuid.uuid4()),
                is_enabled=True,
                description="Allows access from the CLI.",
                value=OnefuzzAppRole.CliClient.value,
            ),
            AppRole(
                allowed_member_types=["Application"],
                display_name=OnefuzzAppRole.ManagedNode.value,
                id=str(uuid.uuid4()),
                is_enabled=True,
                description="Allow access from a lab machine.",
                value=OnefuzzAppRole.ManagedNode.value,
            ),
        ]

        app: Optional[Application] = None

        if not existing:
            logger.info("creating Application registration")
            url = "https://%s.azurewebsites.net" % self.application_name

            params = ApplicationCreateParameters(
                display_name=self.application_name,
                identifier_uris=[url],
                reply_urls=[url + "/.auth/login/aad/callback"],
                optional_claims=OptionalClaims(id_token=[], access_token=[]),
                required_resource_access=[
                    RequiredResourceAccess(
                        resource_access=[
                            ResourceAccess(id=USER_IMPERSONATION, type="Scope")
                        ],
                        resource_app_id="00000002-0000-0000-c000-000000000000",
                    )
                ],
                app_roles=app_roles,
            )
            app = client.applications.create(params)

            logger.info("creating service principal")
            service_principal_params = ServicePrincipalCreateParameters(
                account_enabled=True,
                app_role_assignment_required=False,
                service_principal_type="Application",
                app_id=app.app_id,
            )
            client.service_principals.create(service_principal_params)
        else:
            app = existing[0]
            existing_role_values = [app_role.value for app_role in app.app_roles]
            has_missing_roles = any(
                [role.value not in existing_role_values for role in app_roles]
            )

            if has_missing_roles:
                # disabling the existing app role first to allow the update
                # this is a requirement to update the application roles
                for role in app.app_roles:
                    role.is_enabled = False

                client.applications.patch(
                    app.object_id, ApplicationUpdateParameters(app_roles=app.app_roles)
                )

                # overriding the list of app roles
                client.applications.patch(
                    app.object_id, ApplicationUpdateParameters(app_roles=app_roles)
                )

            creds = list(client.applications.list_password_credentials(app.object_id))
            client.applications.update_password_credentials(app.object_id, creds)

        (password_id, password) = self.create_password(app.object_id)

        cli_app = client.applications.list(filter="appId eq '%s'" % ONEFUZZ_CLI_APP)

        onefuzz_cli_app_uuid = uuid.UUID(ONEFUZZ_CLI_APP)

        if not cli_app:
            logger.info(
                "Could not find the default CLI application under the current "
                "subscription, creating a new one"
            )
            app_info = register_application(
                "onefuzz-cli", self.application_name, OnefuzzAppRole.CliClient
            )
            self.cli_config = {
                "client_id": app_info.client_id,
                "authority": app_info.authority,
            }

        else:
            authorize_application(onefuzz_cli_app_uuid, app.app_id)

        self.results["client_id"] = app.app_id
        self.results["client_secret"] = password

        # Log `client_secret` for consumption by CI.
        if self.log_service_principal:
            logger.info("client_id: %s client_secret: %s", app.app_id, password)
        else:
            logger.debug("client_id: %s client_secret: %s", app.app_id, password)