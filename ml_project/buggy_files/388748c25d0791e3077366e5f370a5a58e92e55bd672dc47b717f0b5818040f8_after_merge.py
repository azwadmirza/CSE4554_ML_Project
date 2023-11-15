    def install(self):
        # the file is a tar, so open it that way and extract it
        # to the specified (or default) roles directory

        if self.scm:
            # create tar file from scm url
            tmp_file = RoleRequirement.scm_archive_role(**self.spec)
        elif self.src:
            if  os.path.isfile(self.src):
                # installing a local tar.gz
                tmp_file = self.src
            elif '://' in self.src:
                role_data = self.src
                tmp_file = self.fetch(role_data)
            else:
                api = GalaxyAPI(self.galaxy, self.options.api_server)
                role_data = api.lookup_role_by_name(self.src)
                if not role_data:
                    raise AnsibleError("- sorry, %s was not found on %s." % (self.src, self.options.api_server))

                role_versions = api.fetch_role_related('versions', role_data['id'])
                if not self.version:
                    # convert the version names to LooseVersion objects
                    # and sort them to get the latest version. If there
                    # are no versions in the list, we'll grab the head
                    # of the master branch
                    if len(role_versions) > 0:
                        loose_versions = [LooseVersion(a.get('name',None)) for a in role_versions]
                        loose_versions.sort()
                        self.version = str(loose_versions[-1])
                    else:
                        self.version = 'master'
                elif self.version != 'master':
                    if role_versions and self.version not in [a.get('name', None) for a in role_versions]:
                        raise AnsibleError("- the specified version (%s) of %s was not found in the list of available versions (%s)." % (self.version, self.name, role_versions))

                tmp_file = self.fetch(role_data)

        else:
           raise AnsibleError("No valid role data found")


        if tmp_file:

            display.display("installing from %s" % tmp_file)

            if not tarfile.is_tarfile(tmp_file):
                raise AnsibleError("the file downloaded was not a tar.gz")
            else:
                if tmp_file.endswith('.gz'):
                    role_tar_file = tarfile.open(tmp_file, "r:gz")
                else:
                    role_tar_file = tarfile.open(tmp_file, "r")
                # verify the role's meta file
                meta_file = None
                members = role_tar_file.getmembers()
                # next find the metadata file
                for member in members:
                    if self.META_MAIN in member.name:
                        meta_file = member
                        break
                if not meta_file:
                    raise AnsibleError("this role does not appear to have a meta/main.yml file.")
                else:
                    try:
                        self._metadata = yaml.safe_load(role_tar_file.extractfile(meta_file))
                    except:
                        raise AnsibleError("this role does not appear to have a valid meta/main.yml file.")

                # we strip off the top-level directory for all of the files contained within
                # the tar file here, since the default is 'github_repo-target', and change it
                # to the specified role's name
                display.display("- extracting %s to %s" % (self.name, self.path))
                try:
                    if os.path.exists(self.path):
                        if not os.path.isdir(self.path):
                            raise AnsibleError("the specified roles path exists and is not a directory.")
                        elif not getattr(self.options, "force", False):
                            raise AnsibleError("the specified role %s appears to already exist. Use --force to replace it." % self.name)
                        else:
                            # using --force, remove the old path
                            if not self.remove():
                                raise AnsibleError("%s doesn't appear to contain a role.\n  please remove this directory manually if you really want to put the role here." % self.path)
                    else:
                        os.makedirs(self.path)

                    # now we do the actual extraction to the path
                    for member in members:
                        # we only extract files, and remove any relative path
                        # bits that might be in the file for security purposes
                        # and drop the leading directory, as mentioned above
                        if member.isreg() or member.issym():
                            parts = member.name.split(os.sep)[1:]
                            final_parts = []
                            for part in parts:
                                if part != '..' and '~' not in part and '$' not in part:
                                    final_parts.append(part)
                            member.name = os.path.join(*final_parts)
                            role_tar_file.extract(member, self.path)

                    # write out the install info file for later use
                    self._write_galaxy_install_info()
                except OSError as e:
                   raise AnsibleError("Could not update files in %s: %s" % (self.path, str(e)))

                # return the parsed yaml metadata
                display.display("- %s was installed successfully" % self.name)
                try:
                    os.unlink(tmp_file)
                except (OSError,IOError) as e:
                    display.warning("Unable to remove tmp file (%s): %s" % (tmp_file, str(e)))
                return True

        return False