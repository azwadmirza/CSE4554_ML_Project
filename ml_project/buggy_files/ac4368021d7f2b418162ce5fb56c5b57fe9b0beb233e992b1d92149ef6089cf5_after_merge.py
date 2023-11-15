    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        self.chroot = self._play_context.remote_addr

        if os.geteuid() != 0:
            raise AnsibleError("chroot connection requires running as root")

        # we're running as root on the local system so do some
        # trivial checks for ensuring 'host' is actually a chroot'able dir
        if not os.path.isdir(self.chroot):
            raise AnsibleError("%s is not a directory" % self.chroot)

        chrootsh = os.path.join(self.chroot, 'bin/sh')
        # Want to check for a usable bourne shell inside the chroot.
        # is_executable() == True is sufficient.  For symlinks it
        # gets really complicated really fast.  So we punt on finding that
        # out.  As long as it's a symlink we assume that it will work
        if not (is_executable(chrootsh) or (os.path.lexists(chrootsh) and os.path.islink(chrootsh))):
            raise AnsibleError("%s does not look like a chrootable dir (/bin/sh missing)" % self.chroot)