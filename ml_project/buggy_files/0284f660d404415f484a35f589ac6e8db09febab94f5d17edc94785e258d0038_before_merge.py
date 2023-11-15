    def hadoop_fs(self, cmd, user=None):
        cmd = 'hadoop fs -' + cmd
        if user:
            cmd = 'HADOOP_USER_NAME={} '.format(user) + cmd
        p = Popen(cmd,
                  shell=True,
                  close_fds=True,
                  executable=os.getenv('SHELL'),
                  stdin=PIPE,
                  stdout=PIPE,
                  stderr=PIPE)
        out, err = p.communicate()
        if p.returncode != 0:
            raise DvcException('HDFS command failed: {}: {}'.format(cmd, err))
        return out.decode('utf-8')