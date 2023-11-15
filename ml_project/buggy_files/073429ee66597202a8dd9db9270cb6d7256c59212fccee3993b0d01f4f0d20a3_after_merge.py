    def create_dockerfile_object(self, directory: str = None) -> None:
        """
        Writes a dockerfile to the provided directory using the specified
        arguments on this Docker storage object.

        In order for the docker python library to build a container it needs a
        Dockerfile that it can use to define the container. This function takes the
        specified arguments then writes them to a temporary file called Dockerfile.

        *Note*: if `files` are added to this container, they will be copied to this directory as well.

        Args:
            - directory (str, optional): A directory where the Dockerfile will be created,
                if no directory is specified is will be created in the current working directory
        """
        directory = directory or "./"

        with open(os.path.join(directory, "Dockerfile"), "w+") as dockerfile:

            # Generate RUN pip install commands for python dependencies
            pip_installs = ""
            if self.python_dependencies:
                for dependency in self.python_dependencies:
                    pip_installs += "RUN pip install {}\n".format(dependency)

            # Generate ENV variables to load into the image
            env_vars = ""
            if self.env_vars:
                white_space = " " * 20
                env_vars = "ENV " + " \ \n{}".format(white_space).join(
                    "{k}={v}".format(k=k, v=v) for k, v in self.env_vars.items()
                )

            # Copy user specified files into the image
            copy_files = ""
            if self.files:
                for src, dest in self.files.items():
                    fname = os.path.basename(src)
                    full_fname = os.path.join(directory, fname)
                    if (
                        os.path.exists(full_fname)
                        and filecmp.cmp(src, full_fname) is False
                    ):
                        raise ValueError(
                            "File {fname} already exists in {directory}".format(
                                fname=full_fname, directory=directory
                            )
                        )
                    else:
                        shutil.copy2(src, full_fname)
                    copy_files += "COPY {fname} {dest}\n".format(fname=fname, dest=dest)

            # Write all flows to file and load into the image
            copy_flows = ""
            for flow_name, flow_location in self.flows.items():
                clean_name = slugify(flow_name)
                flow_path = os.path.join(directory, "{}.flow".format(clean_name))
                with open(flow_path, "wb") as f:
                    cloudpickle.dump(self._flows[flow_name], f)
                copy_flows += "COPY {source} {dest}\n".format(
                    source="{}.flow".format(clean_name), dest=flow_location
                )

            # Write a healthcheck script into the image
            healthcheck = textwrap.dedent(
                """\
            print('Beginning health check...')
            import cloudpickle

            for flow_file in [{flow_file_paths}]:
                with open(flow_file, 'rb') as f:
                    flow = cloudpickle.load(f)
            print('Healthcheck: OK')
            """.format(
                    flow_file_paths=", ".join(
                        ["'{}'".format(k) for k in self.flows.values()]
                    )
                )
            )

            with open(os.path.join(directory, "healthcheck.py"), "w") as health_file:
                health_file.write(healthcheck)

            file_contents = textwrap.dedent(
                """\
                FROM {base_image}

                RUN pip install pip --upgrade
                RUN pip install wheel
                {pip_installs}

                RUN mkdir /root/.prefect/
                {copy_flows}
                COPY healthcheck.py /root/.prefect/healthcheck.py
                {copy_files}

                ENV PREFECT__USER_CONFIG_PATH="/root/.prefect/config.toml"
                {env_vars}

                RUN pip install git+https://github.com/PrefectHQ/prefect.git@master#egg=prefect[kubernetes]
                # RUN pip install prefect

                RUN python /root/.prefect/healthcheck.py
                """.format(
                    base_image=self.base_image,
                    pip_installs=pip_installs,
                    copy_flows=copy_flows,
                    copy_files=copy_files,
                    env_vars=env_vars,
                )
            )

            dockerfile.write(file_contents)