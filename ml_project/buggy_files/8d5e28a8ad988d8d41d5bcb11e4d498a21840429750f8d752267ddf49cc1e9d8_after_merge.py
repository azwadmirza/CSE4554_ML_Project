    def dynamic_branch(self, wildcards, input=True):
        def get_io(rule):
            return (
                (rule.input, rule.dynamic_input)
                if input
                else (rule.output, rule.dynamic_output)
            )

        def partially_expand(f, wildcards):
            """Expand the wildcards in f from the ones present in wildcards

            This is done by replacing all wildcard delimiters by `{{` or `}}`
            that are not in `wildcards.keys()`.
            """
            # perform the partial expansion from f's string representation
            s = str(f).replace("{", "{{").replace("}", "}}")
            for key in wildcards.keys():
                s = s.replace("{{{{{}}}}}".format(key), "{{{}}}".format(key))
            # build result
            anno_s = AnnotatedString(s)
            anno_s.flags = f.flags
            return IOFile(anno_s, f.rule)

        io, dynamic_io = get_io(self)

        branch = Rule(self)
        io_, dynamic_io_ = get_io(branch)

        expansion = collections.defaultdict(list)
        for i, f in enumerate(io):
            if f in dynamic_io:
                f = partially_expand(f, wildcards)
                try:
                    for e in reversed(expand(str(f), zip, **wildcards)):
                        # need to clone the flags so intermediate
                        # dynamic remote file paths are expanded and
                        # removed appropriately
                        ioFile = IOFile(e, rule=branch)
                        ioFile.clone_flags(f)
                        expansion[i].append(ioFile)
                except KeyError:
                    return None

        # replace the dynamic files with the expanded files
        replacements = [(i, io[i], e) for i, e in reversed(list(expansion.items()))]
        for i, old, exp in replacements:
            dynamic_io_.remove(old)
            io_._insert_items(i, exp)

        if not input:
            for i, old, exp in replacements:
                if old in branch.temp_output:
                    branch.temp_output.discard(old)
                    branch.temp_output.update(exp)
                if old in branch.protected_output:
                    branch.protected_output.discard(old)
                    branch.protected_output.update(exp)
                if old in branch.touch_output:
                    branch.touch_output.discard(old)
                    branch.touch_output.update(exp)

            branch.wildcard_names.clear()
            non_dynamic_wildcards = dict(
                (name, values[0])
                for name, values in wildcards.items()
                if len(set(values)) == 1
            )
            # TODO have a look into how to concretize dependencies here
            branch._input, _, branch.dependencies = branch.expand_input(
                non_dynamic_wildcards
            )
            branch._output, _ = branch.expand_output(non_dynamic_wildcards)

            resources = branch.expand_resources(non_dynamic_wildcards, branch._input, 1)
            branch._params = branch.expand_params(
                non_dynamic_wildcards,
                branch._input,
                branch._output,
                resources,
                omit_callable=True,
            )
            branch.resources = dict(resources.items())

            branch._log = branch.expand_log(non_dynamic_wildcards)
            branch._benchmark = branch.expand_benchmark(non_dynamic_wildcards)
            branch._conda_env = branch.expand_conda_env(non_dynamic_wildcards)
            return branch, non_dynamic_wildcards
        return branch