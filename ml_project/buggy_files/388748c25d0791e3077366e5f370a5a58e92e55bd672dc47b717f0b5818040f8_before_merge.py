    def install(self, role_filename):
        # the file is a tar, so open it that way and extract it
        # to the specified (or default) roles directory

        if not tarfile.is_tarfile(role_filename):
            display.error("the file downloaded was not a tar.gz")
            return False
        else:
            if role_filename.endswith('.gz'):
                role_tar_file = tarfile.open(role_filename, "r:gz")
            else:
                role_tar_file = tarfile.open(role_filename, "r")
            # verify the role's meta file
            meta_file = None
            members = role_tar_file.getmembers()
            # next find the metadata file
            for member in members:
                if self.META_MAIN in member.name:
                    meta_file = member
                    break
            if not meta_file:
                display.error("this role does not appear to have a meta/main.yml file.")
                return False
            else:
                try:
                    self._metadata = yaml.safe_load(role_tar_file.extractfile(meta_file))
                except:
                    display.error("this role does not appear to have a valid meta/main.yml file.")
                    return False

            # we strip off the top-level directory for all of the files contained within
            # the tar file here, since the default is 'github_repo-target', and change it
            # to the specified role's name
            display.display("- extracting %s to %s" % (self.name, self.path))
            try:
                if os.path.exists(self.path):
                    if not os.path.isdir(self.path):
                        display.error("the specified roles path exists and is not a directory.")
                        return False
                    elif not getattr(self.options, "force", False):
                        display.error("the specified role %s appears to already exist. Use --force to replace it." % self.name)
                        return False
                    else:
                        # using --force, remove the old path
                        if not self.remove():
                            display.error("%s doesn't appear to contain a role." % self.path)
                            display.error("  please remove this directory manually if you really want to put the role here.")
                            return False
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
                display.error("Could not update files in %s: %s" % (self.path, str(e)))
                return False

            # return the parsed yaml metadata
            display.display("- %s was installed successfully" % self.name)
            return True