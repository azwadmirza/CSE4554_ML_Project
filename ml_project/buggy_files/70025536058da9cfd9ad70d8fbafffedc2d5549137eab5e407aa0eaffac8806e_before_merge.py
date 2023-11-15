    def to_node_dict(self):
        d = syaml_dict()

        if self.versions:
            d.update(self.versions.to_dict())

        if self.compiler:
            d.update(self.compiler.to_dict())

        if self.namespace:
            d['namespace'] = self.namespace

        params = syaml_dict(sorted(
            (name, v.value) for name, v in self.variants.items()))
        params.update(sorted(self.compiler_flags.items()))
        if params:
            d['parameters'] = params

        if self.architecture:
            d['arch'] = self.architecture.to_dict()

        deps = self.dependencies_dict(deptype=('link', 'run'))
        if deps:
            d['dependencies'] = syaml_dict([
                (name,
                 syaml_dict([
                     ('hash', dspec.spec.dag_hash()),
                     ('type', sorted(str(s) for s in dspec.deptypes))])
                 ) for name, dspec in sorted(deps.items())
            ])

        return syaml_dict([(self.name, d)])