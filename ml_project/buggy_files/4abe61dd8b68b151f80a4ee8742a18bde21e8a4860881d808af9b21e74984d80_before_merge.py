    def __init__(self, protocol, *args):
        self.protocol = protocol
        self.args = list(args)
        self.environ = self.protocol.cmdstack[0].environ
        self.fs = self.protocol.fs
        self.data = None  # output data
        self.input_data = None  # used to store STDIN data passed via PIPE
        self.writefn = self.protocol.pp.outReceived
        self.errorWritefn = self.protocol.pp.errReceived
        # MS-DOS style redirect handling, inside the command
        # TODO: handle >>, 2>, etc
        if '>' in self.args or '>>' in self.args:
            self.writtenBytes = 0
            self.writefn = self.write_to_file
            if '>>' in self.args:
                index = self.args.index('>>')
                b_append = True
            else:
                index = self.args.index('>')
                b_append = False
            self.outfile = self.fs.resolve_path(str(self.args[(index + 1)]), self.protocol.cwd)
            del self.args[index:]
            p = self.fs.getfile(self.outfile)
            if not p or not p[fs.A_REALFILE] or p[fs.A_REALFILE].startswith('honeyfs') or not b_append:
                tmp_fname = '%s-%s-%s-redir_%s' % \
                            (time.strftime('%Y%m%d-%H%M%S'),
                             self.protocol.getProtoTransport().transportId,
                             self.protocol.terminal.transport.session.id,
                             re.sub('[^A-Za-z0-9]', '_', self.outfile))
                self.safeoutfile = os.path.join(CowrieConfig().get('honeypot', 'download_path'), tmp_fname)
                perm = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                try:
                    self.fs.mkfile(self.outfile, 0, 0, 0, stat.S_IFREG | perm)
                except fs.FileNotFound:
                    # The outfile locates at a non-existing directory.
                    self.errorWrite('-bash: %s: No such file or directory\n' % self.outfile)
                    self.writefn = self.write_to_failed
                    self.outfile = None
                    self.safeoutfile = None
                except fs.PermissionDenied:
                    # The outfile locates in a file-system that doesn't allow file creation
                    self.errorWrite('-bash: %s: Permission denied\n' % self.outfile)
                    self.writefn = self.write_to_failed
                    self.outfile = None
                    self.safeoutfile = None

                else:
                    with open(self.safeoutfile, 'ab'):
                        self.fs.update_realfile(self.fs.getfile(self.outfile), self.safeoutfile)
            else:
                self.safeoutfile = p[fs.A_REALFILE]