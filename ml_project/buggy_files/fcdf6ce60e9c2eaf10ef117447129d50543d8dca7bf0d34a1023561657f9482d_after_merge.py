    def _preprocess_role_spec(self, ds):
        if 'role' in ds:
            # Old style: {role: "galaxy.role,version,name", other_vars: "here" }
            role_info = RoleRequirement.role_spec_parse(ds['role'])
            if isinstance(role_info, dict):
                # Warning: Slight change in behaviour here.  name may be being
                # overloaded.  Previously, name was only a parameter to the role.
                # Now it is both a parameter to the role and the name that
                # ansible-galaxy will install under on the local system.
                if 'name' in ds and 'name' in role_info:
                    del role_info['name']
                ds.update(role_info)
        else:
            # New style: { src: 'galaxy.role,version,name', other_vars: "here" }
            if 'github.com' in ds["src"] and 'http' in ds["src"] and '+' not in ds["src"] and not ds["src"].endswith('.tar.gz'):
                ds["src"] = "git+" + ds["src"]

            if '+' in ds["src"]:
                (scm, src) = ds["src"].split('+')
                ds["scm"] = scm
                ds["src"] = src

            if 'name' in ds:
                ds["role"] = ds["name"]
                del ds["name"]
            else:
                ds["role"] = RoleRequirement.repo_url_to_role_name(ds["src"])

            # set some values to a default value, if none were specified
            ds.setdefault('version', '')
            ds.setdefault('scm', None)

        return ds