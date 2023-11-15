def main():
    log = logging.getLogger("zulip-provisioner")

    if platform.architecture()[0] == '64bit':
        arch = 'amd64'
        phantomjs_arch = 'x86_64'
    elif platform.architecture()[0] == '32bit':
        arch = "i386"
        phantomjs_arch = 'i686'
    else:
        log.critical("Only x86 is supported; ping zulip-devel@googlegroups.com if you want another architecture.")
        sys.exit(1)

    vendor, version, codename = platform.dist()

    if not (vendor in SUPPORTED_PLATFORMS and codename in SUPPORTED_PLATFORMS[vendor]):
        log.critical("Unsupported platform: {} {}".format(vendor, codename))

    with sh.sudo:
        sh.apt_get.update(**LOUD)

        sh.apt_get.install(*APT_DEPENDENCIES["trusty"], assume_yes=True, **LOUD)

    temp_deb_path = sh.mktemp("package_XXXXXX.deb", tmpdir=True)

    sh.wget(
        "{}/{}_{}_{}.deb".format(
            TSEARCH_URL_BASE,
            TSEARCH_PACKAGE_NAME["trusty"],
            TSEARCH_VERSION,
            arch,
        ),
        output_document=temp_deb_path,
        **LOUD
    )

    with sh.sudo:
        sh.dpkg("--install", temp_deb_path, **LOUD)

    with sh.sudo:
        PHANTOMJS_PATH = "/srv/phantomjs"
        PHANTOMJS_BASENAME = "phantomjs-1.9.8-linux-%s" % (phantomjs_arch,)
        PHANTOMJS_TARBALL_BASENAME = PHANTOMJS_BASENAME + ".tar.bz2"
        PHANTOMJS_TARBALL = os.path.join(PHANTOMJS_PATH, PHANTOMJS_TARBALL_BASENAME)
        PHANTOMJS_URL = "https://bitbucket.org/ariya/phantomjs/downloads/%s" % (PHANTOMJS_TARBALL_BASENAME,)
        sh.mkdir("-p", PHANTOMJS_PATH, **LOUD)
        if not os.path.exists(PHANTOMJS_TARBALL):
            sh.wget(PHANTOMJS_URL, output_document=PHANTOMJS_TARBALL, **LOUD)
        sh.tar("xj", directory=PHANTOMJS_PATH, file=PHANTOMJS_TARBALL, **LOUD)
        sh.ln("-sf", os.path.join(PHANTOMJS_PATH, PHANTOMJS_BASENAME, "bin", "phantomjs"),
              "/usr/local/bin/phantomjs", **LOUD)

    with sh.sudo:
        sh.rm("-rf", VENV_PATH, **LOUD)
        sh.mkdir("-p", VENV_PATH, **LOUD)
        sh.chown("{}:{}".format(os.getuid(), os.getgid()), VENV_PATH, **LOUD)

    sh.virtualenv(VENV_PATH, **LOUD)

    # Add the ./tools and ./scripts/setup directories inside the repository root to
    # the system path; we'll reference them later.
    orig_path = os.environ["PATH"]
    os.environ["PATH"] = os.pathsep.join((
            os.path.join(ZULIP_PATH, "tools"),
            os.path.join(ZULIP_PATH, "scripts", "setup"),
            orig_path
    ))


    # Put Python virtualenv activation in our .bash_profile.
    with open(os.path.expanduser('~/.bash_profile'), 'w+') as bash_profile:
        bash_profile.writelines([
            "source .bashrc\n",
            "source %s\n" % (os.path.join(VENV_PATH, "bin", "activate"),),
        ])

    # Switch current Python context to the virtualenv.
    activate_this = os.path.join(VENV_PATH, "bin", "activate_this.py")
    execfile(activate_this, dict(__file__=activate_this))

    sh.pip.install(requirement=os.path.join(ZULIP_PATH, "requirements.txt"), **LOUD)

    with sh.sudo:
        sh.cp(REPO_STOPWORDS_PATH, TSEARCH_STOPWORDS_PATH, **LOUD)

    # npm install and management commands expect to be run from the root of the project.
    os.chdir(ZULIP_PATH)

    sh.npm.install(**LOUD)

    os.system("tools/download-zxcvbn")
    os.system("tools/emoji_dump/build_emoji")
    os.system("generate_secrets.py -d")
    if "--travis" in sys.argv:
        os.system("sudo service rabbitmq-server restart")
        os.system("sudo service redis-server restart")
        os.system("sudo service memcached restart")
    elif "--docker" in sys.argv:
        os.system("sudo service rabbitmq-server restart")
        os.system("sudo pg_dropcluster --stop 9.3 main")
        os.system("sudo pg_createcluster -e utf8 --start 9.3 main")
        os.system("sudo service redis-server restart")
        os.system("sudo service memcached restart")
    sh.configure_rabbitmq(**LOUD)
    sh.postgres_init_dev_db(**LOUD)
    sh.do_destroy_rebuild_database(**LOUD)
    sh.postgres_init_test_db(**LOUD)
    sh.do_destroy_rebuild_test_database(**LOUD)
    return 0