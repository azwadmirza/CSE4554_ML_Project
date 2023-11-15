    def generate_custom_generator_commands(self, target, parent_node):
        generator_output_files = []
        commands = []
        inputs = []
        outputs = []
        custom_target_include_dirs = []
        custom_target_output_files = []
        target_private_dir = self.relpath(self.get_target_private_dir(target), self.get_target_dir(target))
        down = self.target_to_build_root(target)
        for genlist in target.get_generated_sources():
            if isinstance(genlist, build.CustomTarget):
                for i in genlist.get_outputs():
                    # Path to the generated source from the current vcxproj dir via the build root
                    ipath = os.path.join(down, self.get_target_dir(genlist), i)
                    custom_target_output_files.append(ipath)
                idir = self.relpath(self.get_target_dir(genlist), self.get_target_dir(target))
                if idir not in custom_target_include_dirs:
                    custom_target_include_dirs.append(idir)
            else:
                generator = genlist.get_generator()
                exe = generator.get_exe()
                infilelist = genlist.get_inputs()
                outfilelist = genlist.get_outputs()
                exe_arr = self.exe_object_to_cmd_array(exe)
                base_args = generator.get_arglist()
                for i in range(len(infilelist)):
                    if len(infilelist) == len(outfilelist):
                        sole_output = os.path.join(target_private_dir, outfilelist[i])
                    else:
                        sole_output = ''
                    curfile = infilelist[i]
                    infilename = os.path.join(down, curfile.rel_to_builddir(self.build_to_src))
                    outfiles_rel = genlist.get_outputs_for(curfile)
                    outfiles = [os.path.join(target_private_dir, of) for of in outfiles_rel]
                    generator_output_files += outfiles
                    args = [x.replace("@INPUT@", infilename).replace('@OUTPUT@', sole_output)
                            for x in base_args]
                    args = self.replace_outputs(args, target_private_dir, outfiles_rel)
                    args = [x.replace("@SOURCE_DIR@", self.environment.get_source_dir()).replace("@BUILD_DIR@", target_private_dir)
                            for x in args]
                    fullcmd = exe_arr + self.replace_extra_args(args, genlist)
                    commands.append(' '.join(self.special_quote(fullcmd)))
                    inputs.append(infilename)
                    outputs.extend(outfiles)
        if len(commands) > 0:
            idgroup = ET.SubElement(parent_node, 'ItemDefinitionGroup')
            cbs = ET.SubElement(idgroup, 'CustomBuildStep')
            ET.SubElement(cbs, 'Command').text = '\r\n'.join(commands)
            ET.SubElement(cbs, 'Inputs').text = ";".join(inputs)
            ET.SubElement(cbs, 'Outputs').text = ';'.join(outputs)
            ET.SubElement(cbs, 'Message').text = 'Generating custom sources.'
            pg = ET.SubElement(parent_node, 'PropertyGroup')
            ET.SubElement(pg, 'CustomBuildBeforeTargets').text = 'ClCompile'
        return generator_output_files, custom_target_output_files, custom_target_include_dirs