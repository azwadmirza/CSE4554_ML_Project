    def _get_updated_schema(
        old_config: _OldConfigSchema,
    ) -> Tuple[_NewConfigSchema, _NewConfigSchema]:
        # Prior to 1.0.0, the schema was in this form for both global
        # and guild-based rules:
        # "owner_models"
        # -> "cogs"
        #   -> Cog names...
        #     -> "allow"
        #       -> [Model IDs...]
        #     -> "deny"
        #       -> [Model IDs...]
        #     -> "default"
        #       -> "allow"|"deny"
        # -> "commands"
        #   -> Command names...
        #     -> "allow"
        #       -> [Model IDs...]
        #     -> "deny"
        #       -> [Model IDs...]
        #     -> "default"
        #       -> "allow"|"deny"

        new_cog_rules = {}
        new_cmd_rules = {}
        for guild_id, old_rules in old_config.items():
            if "owner_models" not in old_rules:
                continue
            old_rules = old_rules["owner_models"]
            for category, new_rules in zip(("cogs", "commands"), (new_cog_rules, new_cmd_rules)):
                if category in old_rules:
                    for name, rules in old_rules[category].items():
                        these_rules = new_rules.setdefault(name, {})
                        guild_rules = these_rules.setdefault(str(guild_id), {})
                        # Since allow rules would take precedence if the same model ID
                        # sat in both the allow and deny list, we add the deny entries
                        # first and let any conflicting allow entries overwrite.
                        for model_id in rules.get("deny", []):
                            guild_rules[str(model_id)] = False
                        for model_id in rules.get("allow", []):
                            guild_rules[str(model_id)] = True
                        if "default" in rules:
                            default = rules["default"]
                            if default == "allow":
                                guild_rules["default"] = True
                            elif default == "deny":
                                guild_rules["default"] = False
        return new_cog_rules, new_cmd_rules