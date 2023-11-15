    def gen_custom_target_vcxproj(self, target, ofname, guid):
        root = self.create_basic_crap(target)
        action = ET.SubElement(root, 'ItemDefinitionGroup')
        customstep = ET.SubElement(action, 'CustomBuildStep')
        # We need to always use absolute paths because our invocation is always
        # from the target dir, not the build root.
        target.absolute_paths = True
        (srcs, ofilenames, cmd) = self.eval_custom_target_command(target, True)
        ET.SubElement(customstep, 'Command').text = ' '.join(self.quote_arguments(cmd))
        ET.SubElement(customstep, 'Outputs').text = ';'.join(ofilenames)
        ET.SubElement(customstep, 'Inputs').text = ';'.join(srcs)
        ET.SubElement(root, 'Import', Project='$(VCTargetsPath)\Microsoft.Cpp.targets')
        self.generate_custom_generator_commands(target, root)
        tree = ET.ElementTree(root)
        tree.write(ofname, encoding='utf-8', xml_declaration=True)