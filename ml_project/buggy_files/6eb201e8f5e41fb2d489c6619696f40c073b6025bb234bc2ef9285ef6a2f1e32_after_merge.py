    def manage(self):
        rc, out = self._exec(["list"])
        if rc != 0:
            self.module.fail_json(msg="Unable to list icinga2 features. "
                                      "Ensure icinga2 is installed and present in binary path.")

        # If feature is already in good state, just exit
        if (re.search("Disabled features:.* %s[ \n]" % self.feature_name, out) and self.state == "absent") or \
                (re.search("Enabled features:.* %s[ \n]" % self.feature_name, out) and self.state == "present"):
            self.module.exit_json(changed=False)

        if self.module.check_mode:
            self.module.exit_json(changed=True)

        feature_enable_str = "enable" if self.state == "present" else "disable"

        rc, out = self._exec([feature_enable_str, self.feature_name])

        change_applied = False
        if self.state == "present":
            if rc != 0:
                self.module.fail_json(msg="Failed to %s feature %s."
                                          " icinga2 command returned %s" % (feature_enable_str,
                                                                            self.feature_name,
                                                                            out))

            if re.search("already enabled", out) is None:
                change_applied = True
        else:
            if rc == 0:
                change_applied = True
            # RC is not 0 for this already disabled feature, handle it as no change applied
            elif re.search("Cannot disable feature '%s'. Target file .* does not exist" % self.feature_name, out):
                change_applied = False
            else:
                self.module.fail_json(msg="Failed to disable feature. Command returns %s" % out)

        self.module.exit_json(changed=change_applied)