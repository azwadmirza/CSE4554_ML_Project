    def run(self):
        # Run build.run function
        build.run(self)
        if getattr(self.distribution, 'running_salt_install', False):
            # If our install attribute is present and set to True, we'll go
            # ahead and write our install time python modules.

            # Write the version file
            version_file_path = os.path.join(
                self.build_lib, 'salt', '_version.py'
            )
            open(version_file_path, 'w').write(
                INSTALL_VERSION_TEMPLATE.format(
                    date=datetime.utcnow(),
                    version=__version__,
                    version_info=__version_info__
                )
            )

            # Write the system paths file
            system_paths_file_path = os.path.join(
                self.build_lib, 'salt', '_syspaths.py'
            )
            open(system_paths_file_path, 'w').write(
                install_syspaths_template.format(
                    date=datetime.utcnow(),
                    root_dir=self.distribution.salt_root_dir,
                    config_dir=self.distribution.salt_config_dir,
                    cache_dir=self.distribution.salt_cache_dir,
                    sock_dir=self.distribution.salt_sock_dir,
                    srv_root_dir=self.distribution.salt_srv_root_dir,
                    base_file_roots_dir=self.distribution.salt_base_file_roots_dir,
                    base_pillar_roots_dir=self.distribution.salt_base_pillar_roots_dir,
                    base_master_roots_dir=self.distribution.salt_base_master_roots_dir,
                    logs_dir=self.distribution.salt_logs_dir,
                    pidfile_dir=self.distribution.salt_pidfile_dir,
                )
            )