def main():

    print("%s (server) #v%s\n" % (NAME, VERSION))

    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("-c", dest="config_file", default=CONFIG_FILE, help="Configuration file (default: '%s')" % os.path.split(CONFIG_FILE)[-1])
    options, _ = parser.parse_args()

    read_config(options.config_file)

    if config.USE_SSL:
        try:
            import OpenSSL
        except ImportError:
            if subprocess.mswindows:
                exit("[!] please install 'pyopenssl' (e.g. 'pip install pyopenssl')")
            else:
                msg, _ = "[!] please install 'pyopenssl'", platform.linux_distribution()[0].lower()
                for distro, install in {("fedora", "centos"): "sudo yum install pyOpenSSL", ("debian", "ubuntu"): "sudo apt-get install python-openssl"}.items():
                    if _ in distro:
                        msg += " (e.g. '%s')" % install
                        break
                exit(msg)

        if not config.SSL_PEM or not os.path.isfile(config.SSL_PEM):
            hint = "openssl req -new -x509 -keyout %s -out %s -days 365 -nodes -subj '/O=%s CA/C=EU'" % (config.SSL_PEM or "server.pem", config.SSL_PEM or "server.pem", NAME)
            exit("[!] invalid configuration value for 'SSL_PEM' ('%s')\n[?] (hint: \"%s\")" % (config.SSL_PEM, hint))

    def update_timer():
        if config.USE_SERVER_UPDATE_TRAILS:
            update_trails()

        update_ipcat()

        thread = threading.Timer(config.UPDATE_PERIOD, update_timer)
        thread.daemon = True
        thread.start()

    if config.UDP_ADDRESS and config.UDP_PORT:
        if check_sudo() is False:
            exit("[!] please run '%s' with sudo/Administrator privileges when using 'UDP_ADDRESS' configuration value" % __file__)

        start_logd(address=config.UDP_ADDRESS, port=config.UDP_PORT, join=False)

    try:
        update_timer()
        start_httpd(address=config.HTTP_ADDRESS, port=config.HTTP_PORT, pem=config.SSL_PEM if config.USE_SSL else None, join=True)
    except KeyboardInterrupt:
        print("\r[x] stopping (Ctrl-C pressed)")