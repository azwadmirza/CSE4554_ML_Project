    def manage(self):
        rc, out = self._exec(["list"])
        if rc != 0:
            self.module.fail_json(msg="Unable to list icinga2 features. "
                                      "Ensure icinga2 is installed and present in binary path.")

        else:
            # If feature is already in good state, just exit
            if re.search("Disabled features:.* %s[ \n]" % self.module.params["name"], out) \
                    and self.module.params["state"] == "absent" or \
                    re.search("Enabled features:.* %s[ \n]" % self.module.params["name"], out) \
                    and self.module.params["state"] == "present":
                self.module.exit_json(changed=False)

            if self.module.check_mode:
                self.module.exit_json(changed=True)

        if self.module.params["state"] == "present":
            feature_enable_str = "enable"
        else:
            feature_enable_str = "disable"

        rc, out = self._exec([feature_enable_str, self.module.params["name"]])

        if self.module.params["state"] == "present":
            if rc != 0:
                self.module.fail_json(msg="Fail to %s feature %s. icinga2 command returned %s"
                                      % (feature_enable_str, self.module.params["name"], out))

            if re.search("already enabled", out) is None:
                change_applied = True
            else:
                change_applied = False
        else:
            if rc == 0:
                change_applied = True
            # RC is not 0 for this already disabled feature, handle it as no change applied
            elif re.search("Cannot disable feature '%s'. Target file .* does not exist"
                           % self.module.params["name"]):
                change_applied = False
            else:
                self.module.fail_json(msg="Fail to disable feature. Command returns %s" % out)

        self.module.exit_json(changed=change_applied)