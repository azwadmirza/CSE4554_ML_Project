    def get_target_deps(self, t, recursive=False):
        all_deps = {}
        for target in t.values():
            if isinstance(target, build.CustomTarget):
                for d in target.get_target_dependencies():
                    all_deps[d.get_id()] = d
            elif isinstance(target, build.RunTarget):
                for d in [target.command] + target.args:
                    if isinstance(d, (build.BuildTarget, build.CustomTarget)):
                        all_deps[d.get_id()] = d
            # BuildTarget
            else:
                for ldep in target.link_targets:
                    all_deps[ldep.get_id()] = ldep
                for obj_id, objdep in self.get_obj_target_deps(target.objects):
                    all_deps[obj_id] = objdep
                for gendep in target.get_generated_sources():
                    if isinstance(gendep, build.CustomTarget):
                        all_deps[gendep.get_id()] = gendep
                    else:
                        gen_exe = gendep.generator.get_exe()
                        if isinstance(gen_exe, build.Executable):
                            all_deps[gen_exe.get_id()] = gen_exe
        if not t or not recursive:
            return all_deps
        ret = self.get_target_deps(all_deps, recursive)
        ret.update(all_deps)
        return ret