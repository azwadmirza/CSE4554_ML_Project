    def install_jupyter_kernel(self):
        kernel_name = '"Python/Mu ({})"'.format(self.name)
        logger.info("Installing Jupyter Kernel %s", kernel_name)
        return self.run_python(
            "-m",
            "ipykernel",
            "install",
            "--user",
            "--name",
            self.name,
            "--display-name",
            kernel_name,
        )