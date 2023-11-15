    def update_password_policy(self, module, policy):
        min_pw_length = module.params.get('min_pw_length')
        require_symbols = module.params.get('require_symbols')
        require_numbers = module.params.get('require_numbers')
        require_uppercase = module.params.get('require_uppercase')
        require_lowercase = module.params.get('require_lowercase')
        allow_pw_change = module.params.get('allow_pw_change')
        pw_max_age = module.params.get('pw_max_age')
        pw_reuse_prevent = module.params.get('pw_reuse_prevent')
        pw_expire = module.params.get('pw_expire')

        try:
            results = policy.update(
                MinimumPasswordLength=min_pw_length,
                RequireSymbols=require_symbols,
                RequireNumbers=require_numbers,
                RequireUppercaseCharacters=require_uppercase,
                RequireLowercaseCharacters=require_lowercase,
                AllowUsersToChangePassword=allow_pw_change,
                MaxPasswordAge=pw_max_age,
                PasswordReusePrevention=pw_reuse_prevent,
                HardExpiry=pw_expire
            )
            policy.reload()
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Couldn't update IAM Password Policy")
        return camel_dict_to_snake_dict(results)