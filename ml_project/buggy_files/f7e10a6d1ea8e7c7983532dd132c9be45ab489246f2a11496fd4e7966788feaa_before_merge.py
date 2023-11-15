    def _spawn_wheel_build(self, built_wheels_dir, build_request):
        build_result = build_request.result(built_wheels_dir)
        build_job = get_pip().spawn_build_wheels(
            distributions=[build_request.source_path],
            wheel_dir=build_result.build_dir,
            cache=self._cache,
            indexes=self._indexes,
            find_links=self._find_links,
            network_configuration=self._network_configuration,
            interpreter=build_request.target.get_interpreter(),
        )
        return SpawnedJob.wait(job=build_job, result=build_result)