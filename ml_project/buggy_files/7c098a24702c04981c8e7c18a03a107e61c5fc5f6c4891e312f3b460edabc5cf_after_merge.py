    def _get_ssh_client(self, host):
        """
        Create a SSH Client based on host, username and password if provided.
        If there is any AuthenticationException/SSHException, raise HTTP Error 403 as permission denied.

        :param host:
        :return: ssh client instance
        """
        ssh = None

        global remote_user
        global remote_pwd
        if remote_user is None:
            remote_user = os.getenv('EG_REMOTE_USER', getpass.getuser())
            remote_pwd = os.getenv('EG_REMOTE_PWD')  # this should use password-less ssh

        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
            host_ip = gethostbyname(host)
            if remote_pwd:
                ssh.connect(host_ip, port=ssh_port, username=remote_user, password=remote_pwd)
            else:
                ssh.connect(host_ip, port=ssh_port, username=remote_user)
        except Exception as e:
            http_status_code = 500
            current_host = gethostbyname(gethostname())
            error_message = "Exception '{}' occurred when creating a SSHClient at {} connecting " \
                            "to '{}:{}' with user '{}', message='{}'.".\
                format(type(e).__name__, current_host, host, ssh_port, remote_user, e)
            if e is paramiko.SSHException or paramiko.AuthenticationException:
                http_status_code = 403
                error_message_prefix = "Failed to authenticate SSHClient with password"
                error_message = error_message_prefix + (" provided" if remote_pwd else "-less SSH")

            self.log_and_raise(http_status_code=http_status_code, reason=error_message)
        return ssh