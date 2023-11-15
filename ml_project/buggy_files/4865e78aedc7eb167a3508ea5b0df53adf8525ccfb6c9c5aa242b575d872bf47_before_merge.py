    def dag_hash(self, length=None):
        """
        Return a hash of the entire spec DAG, including connectivity.
        """
        if self._hash:
            return self._hash[:length]
        else:
            # XXX(deptype): ignore 'build' dependencies here
            yaml_text = syaml.dump(
                self.to_node_dict(), default_flow_style=True, width=sys.maxint)
            sha = hashlib.sha1(yaml_text)
            b32_hash = base64.b32encode(sha.digest()).lower()[:length]
            if self.concrete:
                self._hash = b32_hash
            return b32_hash