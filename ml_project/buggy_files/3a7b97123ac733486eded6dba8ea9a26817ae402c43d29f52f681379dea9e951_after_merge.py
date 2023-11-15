  def run(self):
    working_directory = os.path.abspath(os.getcwd() + "/../")
    virtualenv_bin = os.path.dirname(sys.executable)
    pip = "%s/pip" % virtualenv_bin

    # Install the GRR server component to satisfy the dependency below.
    subprocess.check_call(
        [sys.executable, pip, "install", "."],
        cwd=working_directory)

    # Install the grr-response-server metapackage to get the remaining
    # dependencies and the entry points.
    subprocess.check_call(
        [sys.executable, pip, "install", "."],
        cwd=working_directory + "/grr/config/grr-response-server/")

    major_minor_version = ".".join(
        pkg_resources.get_distribution(
            "grr-response-core").version.split(".")[0:2])
    subprocess.check_call(
        [sys.executable, pip, "install", "-f",
         "https://storage.googleapis.com/releases.grr-response.com/index.html",
         "grr-response-templates==%s.*" % major_minor_version],
        cwd=working_directory)