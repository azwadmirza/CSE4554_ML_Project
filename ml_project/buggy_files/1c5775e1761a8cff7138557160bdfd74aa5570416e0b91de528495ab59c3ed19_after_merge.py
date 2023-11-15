    def _spawn_download(self, resolved_dists_dir, target):
        download_dir = os.path.join(resolved_dists_dir, target.id)
        download_job = get_pip().spawn_download_distributions(
            download_dir=download_dir,
            requirements=self.requirements,
            requirement_files=self.requirement_files,
            constraint_files=self.constraint_files,
            allow_prereleases=self.allow_prereleases,
            transitive=self.transitive,
            target=target,
            package_index_configuration=self.package_index_configuration,
            cache=self.cache,
            build=self.build,
            manylinux=self.manylinux,
            use_wheel=self.use_wheel,
        )
        return SpawnedJob.wait(job=download_job, result=DownloadResult(target, download_dir))