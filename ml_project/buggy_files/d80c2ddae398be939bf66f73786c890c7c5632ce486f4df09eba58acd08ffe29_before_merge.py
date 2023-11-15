    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject) 

        if isinstance(terms, basestring):
            terms = [ terms ] 

        ret = []
        for term in terms:
            p = subprocess.Popen(term, cwd=self.basedir, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (stdout, stderr) = p.communicate()
            if p.returncode == 0:
                ret.append(stdout.decode("utf-8").rstrip())
            else:
                raise errors.AnsibleError("lookup_plugin.pipe(%s) returned %d" % (term, p.returncode))
        return ret