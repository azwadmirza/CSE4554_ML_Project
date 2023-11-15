    def process_template(self, cfg, minimize=None):
        """
        Process the Policy Sentry template as a dict. This auto-detects whether or not the file is in CRUD mode or
        Actions mode.

        Arguments:
            cfg: The loaded YAML as a dict. Must follow Policy Sentry dictated format.
            minimize: Minimize the resulting statement with *safe* usage of wildcards to reduce policy length. Set this to the character length you want - for example, 0, or 4. Defaults to none.
        Returns:
            Dictionary: The rendered IAM JSON Policy
        """
        if "mode" in cfg.keys():
            if cfg["mode"] == "crud":
                logger.debug("CRUD mode selected")
                check_crud_schema(cfg)
                if "exclude-actions" in cfg:
                    if cfg["exclude-actions"]:
                        if cfg["exclude-actions"][0] != "":
                            self.add_exclude_actions(cfg["exclude-actions"])
                if "wildcard-only" in cfg.keys():
                    if "single-actions" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["single-actions"]:
                            if cfg["wildcard-only"]["single-actions"][0] != "":
                                provided_wildcard_actions = cfg["wildcard-only"][
                                    "single-actions"
                                ]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(provided_wildcard_actions)}"
                                )
                                self.wildcard_only_single_actions = provided_wildcard_actions
                    if "service-read" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["service-read"]:
                            if cfg["wildcard-only"]["service-read"][0] != "":
                                service_read = cfg["wildcard-only"]["service-read"]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(service_read)}"
                                )
                                self.wildcard_only_service_read = service_read
                    if "service-write" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["service-write"]:
                            if cfg["wildcard-only"]["service-write"][0] != "":
                                service_write = cfg["wildcard-only"]["service-write"]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(service_write)}"
                                )
                                self.wildcard_only_service_write = service_write
                    if "service-list" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["service-list"]:
                            if cfg["wildcard-only"]["service-list"][0] != "":
                                service_list = cfg["wildcard-only"]["service-list"]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(service_list)}"
                                )
                                self.wildcard_only_service_list = service_list
                    if "service-tagging" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["service-tagging"]:
                            if cfg["wildcard-only"]["service-tagging"][0] != "":
                                service_tagging = cfg["wildcard-only"][
                                    "service-tagging"
                                ]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(service_tagging)}"
                                )
                                self.wildcard_only_service_tagging = service_tagging
                    if "service-permissions-management" in cfg["wildcard-only"]:
                        if cfg["wildcard-only"]["service-permissions-management"]:
                            if (
                                cfg["wildcard-only"]["service-permissions-management"][
                                    0
                                ]
                                != ""
                            ):

                                service_permissions_management = cfg["wildcard-only"][
                                    "service-permissions-management"
                                ]
                                logger.debug(
                                    f"Requested wildcard-only actions: {str(service_permissions_management)}"
                                )
                                self.wildcard_only_service_permissions_management = service_permissions_management
                    self.process_wildcard_only_actions()
                if "read" in cfg.keys():
                    if cfg["read"] is not None and cfg["read"][0] != "":
                        logger.debug(f"Requested access to arns: {str(cfg['read'])}")
                        self.add_by_arn_and_access_level(cfg["read"], "Read")
                if "write" in cfg.keys():
                    if cfg["write"] is not None and cfg["write"][0] != "":
                        logger.debug(f"Requested access to arns: {str(cfg['write'])}")
                        self.add_by_arn_and_access_level(cfg["write"], "Write")
                if "list" in cfg.keys():
                    if cfg["list"] is not None and cfg["list"][0] != "":
                        logger.debug(f"Requested access to arns: {str(cfg['list'])}")
                        self.add_by_arn_and_access_level(cfg["list"], "List")
                if "permissions-management" in cfg.keys():
                    if (
                        cfg["permissions-management"] is not None
                        and cfg["permissions-management"][0] != ""
                    ):
                        logger.debug(
                            f"Requested access to arns: {str(cfg['permissions-management'])}"
                        )
                        self.add_by_arn_and_access_level(
                            cfg["permissions-management"], "Permissions management",
                        )
                if "tagging" in cfg.keys():
                    if cfg["tagging"] is not None and cfg["tagging"][0] != "":
                        logger.debug(f"Requested access to arns: {str(cfg['tagging'])}")
                        self.add_by_arn_and_access_level(cfg["tagging"], "Tagging")
                if "skip-resource-constraints" in cfg.keys():
                    if cfg["skip-resource-constraints"]:
                        if cfg["skip-resource-constraints"][0] != "":
                            logger.debug(
                                f"Requested override: the actions {str(cfg['skip-resource-constraints'])} will "
                                f"skip resource constraints."
                            )
                            self.add_skip_resource_constraints(cfg["skip-resource-constraints"])
                            for skip_resource_constraints_action in self.skip_resource_constraints:
                                self.add_action_without_resource_constraint(
                                    skip_resource_constraints_action, "SkipResourceConstraints"
                                )
            if cfg["mode"] == "actions":
                check_actions_schema(cfg)
                if "actions" in cfg.keys():
                    if cfg["actions"] is not None and cfg["actions"][0] != "":
                        self.add_by_list_of_actions(cfg["actions"])

        rendered_policy = self.get_rendered_policy(minimize)
        return rendered_policy