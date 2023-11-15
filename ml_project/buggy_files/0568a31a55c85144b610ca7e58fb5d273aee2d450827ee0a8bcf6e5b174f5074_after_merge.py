    def list_parameters(self):
        UNLISTED_PARAMETERS = (
            'bld_path',
            'conda_build',
            'croot',
            'debug',
            'default_python',
            'dry_run',
            'enable_private_envs',
            'error_upload_url',  # should remain undocumented
            'force_32bit',
            'ignore_pinned',
            'migrated_custom_channels',
            'only_dependencies',
            'prune',
            'root_prefix',
            'subdir',
            'subdirs',
# https://conda.io/docs/config.html#disable-updating-of-dependencies-update-dependencies # NOQA
# I don't think this documentation is correct any longer. # NOQA
            'target_prefix_override',  # used to override prefix rewriting, for e.g. building docker containers or RPMs  # NOQA
            'update_dependencies',
            'use_local',
        )
        return tuple(p for p in super(Context, self).list_parameters()
                     if p not in UNLISTED_PARAMETERS)