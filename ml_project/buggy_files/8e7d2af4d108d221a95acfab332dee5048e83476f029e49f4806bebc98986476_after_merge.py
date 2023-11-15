    def gen_vcxproj(self, target, ofname, guid):
        mlog.debug('Generating vcxproj %s.' % target.name)
        entrypoint = 'WinMainCRTStartup'
        subsystem = 'Windows'
        if isinstance(target, build.Executable):
            conftype = 'Application'
            if not target.gui_app:
                subsystem = 'Console'
                entrypoint = 'mainCRTStartup'
        elif isinstance(target, build.StaticLibrary):
            conftype = 'StaticLibrary'
        elif isinstance(target, build.SharedLibrary):
            conftype = 'DynamicLibrary'
            entrypoint = '_DllMainCrtStartup'
        elif isinstance(target, build.CustomTarget):
            return self.gen_custom_target_vcxproj(target, ofname, guid)
        elif isinstance(target, build.RunTarget):
            return self.gen_run_target_vcxproj(target, ofname, guid)
        else:
            raise MesonException('Unknown target type for %s' % target.get_basename())
        # Prefix to use to access the build root from the vcxproj dir
        down = self.target_to_build_root(target)
        # Prefix to use to access the source tree's root from the vcxproj dir
        proj_to_src_root = os.path.join(down, self.build_to_src)
        # Prefix to use to access the source tree's subdir from the vcxproj dir
        proj_to_src_dir = os.path.join(proj_to_src_root, target.subdir)
        (sources, headers, objects, languages) = self.split_sources(target.sources)
        if self.is_unity(target):
            sources = self.generate_unity_files(target, sources)
        compiler = self._get_cl_compiler(target)
        buildtype_args = compiler.get_buildtype_args(self.buildtype)
        buildtype_link_args = compiler.get_buildtype_linker_args(self.buildtype)
        project_name = target.name
        target_name = target.name
        root = ET.Element('Project', {'DefaultTargets': "Build",
                                      'ToolsVersion': '4.0',
                                      'xmlns': 'http://schemas.microsoft.com/developer/msbuild/2003'})
        confitems = ET.SubElement(root, 'ItemGroup', {'Label': 'ProjectConfigurations'})
        prjconf = ET.SubElement(confitems, 'ProjectConfiguration',
                                {'Include': self.buildtype + '|' + self.platform})
        p = ET.SubElement(prjconf, 'Configuration')
        p.text = self.buildtype
        pl = ET.SubElement(prjconf, 'Platform')
        pl.text = self.platform
        # Globals
        globalgroup = ET.SubElement(root, 'PropertyGroup', Label='Globals')
        guidelem = ET.SubElement(globalgroup, 'ProjectGuid')
        guidelem.text = '{%s}' % guid
        kw = ET.SubElement(globalgroup, 'Keyword')
        kw.text = self.platform + 'Proj'
        ns = ET.SubElement(globalgroup, 'RootNamespace')
        ns.text = target_name
        p = ET.SubElement(globalgroup, 'Platform')
        p.text = self.platform
        pname = ET.SubElement(globalgroup, 'ProjectName')
        pname.text = project_name
        if self.windows_target_platform_version:
            ET.SubElement(globalgroup, 'WindowsTargetPlatformVersion').text = self.windows_target_platform_version
        ET.SubElement(root, 'Import', Project='$(VCTargetsPath)\Microsoft.Cpp.Default.props')
        # Start configuration
        type_config = ET.SubElement(root, 'PropertyGroup', Label='Configuration')
        ET.SubElement(type_config, 'ConfigurationType').text = conftype
        ET.SubElement(type_config, 'CharacterSet').text = 'MultiByte'
        if self.platform_toolset:
            ET.SubElement(type_config, 'PlatformToolset').text = self.platform_toolset
        # FIXME: Meson's LTO support needs to be integrated here
        ET.SubElement(type_config, 'WholeProgramOptimization').text = 'false'
        # Let VS auto-set the RTC level
        ET.SubElement(type_config, 'BasicRuntimeChecks').text = 'Default'
        o_flags = split_o_flags_args(buildtype_args)
        if '/Oi' in o_flags:
            ET.SubElement(type_config, 'IntrinsicFunctions').text = 'true'
        if '/Ob1' in o_flags:
            ET.SubElement(type_config, 'InlineFunctionExpansion').text = 'OnlyExplicitInline'
        elif '/Ob2' in o_flags:
            ET.SubElement(type_config, 'InlineFunctionExpansion').text = 'AnySuitable'
        # Size-preserving flags
        if '/Os' in o_flags:
            ET.SubElement(type_config, 'FavorSizeOrSpeed').text = 'Size'
        else:
            ET.SubElement(type_config, 'FavorSizeOrSpeed').text = 'Speed'
        # Incremental linking increases code size
        if '/INCREMENTAL:NO' in buildtype_link_args:
            ET.SubElement(type_config, 'LinkIncremental').text = 'false'
        # CRT type; debug or release
        if '/MDd' in buildtype_args:
            ET.SubElement(type_config, 'UseDebugLibraries').text = 'true'
            ET.SubElement(type_config, 'RuntimeLibrary').text = 'MultiThreadedDebugDLL'
        else:
            ET.SubElement(type_config, 'UseDebugLibraries').text = 'false'
            ET.SubElement(type_config, 'RuntimeLibrary').text = 'MultiThreadedDLL'
        # Debug format
        if '/ZI' in buildtype_args:
            ET.SubElement(type_config, 'DebugInformationFormat').text = 'EditAndContinue'
        elif '/Zi' in buildtype_args:
            ET.SubElement(type_config, 'DebugInformationFormat').text = 'ProgramDatabase'
        elif '/Z7' in buildtype_args:
            ET.SubElement(type_config, 'DebugInformationFormat').text = 'OldStyle'
        # Runtime checks
        if '/RTC1' in buildtype_args:
            ET.SubElement(type_config, 'BasicRuntimeChecks').text = 'EnableFastChecks'
        elif '/RTCu' in buildtype_args:
            ET.SubElement(type_config, 'BasicRuntimeChecks').text = 'UninitializedLocalUsageCheck'
        elif '/RTCs' in buildtype_args:
            ET.SubElement(type_config, 'BasicRuntimeChecks').text = 'StackFrameRuntimeCheck'
        # Optimization flags
        if '/Ox' in o_flags:
            ET.SubElement(type_config, 'Optimization').text = 'Full'
        elif '/O2' in o_flags:
            ET.SubElement(type_config, 'Optimization').text = 'MaxSpeed'
        elif '/O1' in o_flags:
            ET.SubElement(type_config, 'Optimization').text = 'MinSpace'
        elif '/Od' in o_flags:
            ET.SubElement(type_config, 'Optimization').text = 'Disabled'
        # End configuration
        ET.SubElement(root, 'Import', Project='$(VCTargetsPath)\Microsoft.Cpp.props')
        generated_files, custom_target_output_files, generated_files_include_dirs = self.generate_custom_generator_commands(target, root)
        (gen_src, gen_hdrs, gen_objs, gen_langs) = self.split_sources(generated_files)
        (custom_src, custom_hdrs, custom_objs, custom_langs) = self.split_sources(custom_target_output_files)
        gen_src += custom_src
        gen_hdrs += custom_hdrs
        gen_langs += custom_langs
        # Project information
        direlem = ET.SubElement(root, 'PropertyGroup')
        fver = ET.SubElement(direlem, '_ProjectFileVersion')
        fver.text = self.project_file_version
        outdir = ET.SubElement(direlem, 'OutDir')
        outdir.text = '.\\'
        intdir = ET.SubElement(direlem, 'IntDir')
        intdir.text = target.get_id() + '\\'
        tfilename = os.path.splitext(target.get_filename())
        ET.SubElement(direlem, 'TargetName').text = tfilename[0]
        ET.SubElement(direlem, 'TargetExt').text = tfilename[1]

        # Build information
        compiles = ET.SubElement(root, 'ItemDefinitionGroup')
        clconf = ET.SubElement(compiles, 'ClCompile')
        # Arguments, include dirs, defines for all files in the current target
        target_args = []
        target_defines = []
        target_inc_dirs = []
        # Arguments, include dirs, defines passed to individual files in
        # a target; perhaps because the args are language-specific
        #
        # file_args is also later split out into defines and include_dirs in
        # case someone passed those in there
        file_args = dict((lang, CompilerArgs(comp)) for lang, comp in target.compilers.items())
        file_defines = dict((lang, []) for lang in target.compilers)
        file_inc_dirs = dict((lang, []) for lang in target.compilers)
        # The order in which these compile args are added must match
        # generate_single_compile() and generate_basic_compiler_args()
        for l, comp in target.compilers.items():
            if l in file_args:
                file_args[l] += compilers.get_base_compile_args(self.environment.coredata.base_options, comp)
                file_args[l] += comp.get_option_compile_args(self.environment.coredata.compiler_options)
        # Add compile args added using add_project_arguments()
        for l, args in self.build.projects_args.get(target.subproject, {}).items():
            if l in file_args:
                file_args[l] += args
        # Add compile args added using add_global_arguments()
        # These override per-project arguments
        for l, args in self.build.global_args.items():
            if l in file_args:
                file_args[l] += args
        if not target.is_cross:
            # Compile args added from the env: CFLAGS/CXXFLAGS, etc. We want these
            # to override all the defaults, but not the per-target compile args.
            for l, args in self.environment.coredata.external_args.items():
                if l in file_args:
                    file_args[l] += args
        for args in file_args.values():
            # This is where Visual Studio will insert target_args, target_defines,
            # etc, which are added later from external deps (see below).
            args += ['%(AdditionalOptions)', '%(PreprocessorDefinitions)', '%(AdditionalIncludeDirectories)']
            # Add custom target dirs as includes automatically, but before
            # target-specific include dirs. See _generate_single_compile() in
            # the ninja backend for caveats.
            args += ['-I' + arg for arg in generated_files_include_dirs]
            # Add include dirs from the `include_directories:` kwarg on the target
            # and from `include_directories:` of internal deps of the target.
            #
            # Target include dirs should override internal deps include dirs.
            # This is handled in BuildTarget.process_kwargs()
            #
            # Include dirs from internal deps should override include dirs from
            # external deps and must maintain the order in which they are
            # specified. Hence, we must reverse so that the order is preserved.
            #
            # These are per-target, but we still add them as per-file because we
            # need them to be looked in first.
            for d in reversed(target.get_include_dirs()):
                for i in d.get_incdirs():
                    curdir = os.path.join(d.get_curdir(), i)
                    args.append('-I' + self.relpath(curdir, target.subdir)) # build dir
                    args.append('-I' + os.path.join(proj_to_src_root, curdir)) # src dir
                for i in d.get_extra_build_dirs():
                    curdir = os.path.join(d.get_curdir(), i)
                    args.append('-I' + self.relpath(curdir, target.subdir))  # build dir
        # Add per-target compile args, f.ex, `c_args : ['/DFOO']`. We set these
        # near the end since these are supposed to override everything else.
        for l, args in target.extra_args.items():
            if l in file_args:
                file_args[l] += args
        # The highest priority includes. In order of directory search:
        # target private dir, target build dir, target source dir
        for args in file_args.values():
            t_inc_dirs = [self.relpath(self.get_target_private_dir(target),
                                       self.get_target_dir(target))]
            if target.implicit_include_directories:
                t_inc_dirs += ['.']
            if target.implicit_include_directories:
                t_inc_dirs += [proj_to_src_dir]
            args += ['-I' + arg for arg in t_inc_dirs]

        # Split preprocessor defines and include directories out of the list of
        # all extra arguments. The rest go into %(AdditionalOptions).
        for l, args in file_args.items():
            for arg in args[:]:
                if arg.startswith(('-D', '/D')) or arg == '%(PreprocessorDefinitions)':
                    file_args[l].remove(arg)
                    # Don't escape the marker
                    if arg == '%(PreprocessorDefinitions)':
                        define = arg
                    else:
                        define = arg[2:]
                    # De-dup
                    if define in file_defines[l]:
                        file_defines[l].remove(define)
                    file_defines[l].append(define)
                elif arg.startswith(('-I', '/I')) or arg == '%(AdditionalIncludeDirectories)':
                    file_args[l].remove(arg)
                    # Don't escape the marker
                    if arg == '%(AdditionalIncludeDirectories)':
                        inc_dir = arg
                    else:
                        inc_dir = arg[2:]
                    # De-dup
                    if inc_dir not in file_inc_dirs[l]:
                        file_inc_dirs[l].append(inc_dir)

        # Split compile args needed to find external dependencies
        # Link args are added while generating the link command
        for d in reversed(target.get_external_deps()):
            # Cflags required by external deps might have UNIX-specific flags,
            # so filter them out if needed
            d_compile_args = compiler.unix_args_to_native(d.get_compile_args())
            for arg in d_compile_args:
                if arg.startswith(('-D', '/D')):
                    define = arg[2:]
                    # De-dup
                    if define in target_defines:
                        target_defines.remove(define)
                    target_defines.append(define)
                elif arg.startswith(('-I', '/I')):
                    inc_dir = arg[2:]
                    # De-dup
                    if inc_dir not in target_inc_dirs:
                        target_inc_dirs.append(inc_dir)
                else:
                    target_args.append(arg)

        languages += gen_langs
        if len(target_args) > 0:
            target_args.append('%(AdditionalOptions)')
            ET.SubElement(clconf, "AdditionalOptions").text = ' '.join(target_args)

        target_inc_dirs.append('%(AdditionalIncludeDirectories)')
        ET.SubElement(clconf, 'AdditionalIncludeDirectories').text = ';'.join(target_inc_dirs)
        target_defines.append('%(PreprocessorDefinitions)')
        ET.SubElement(clconf, 'PreprocessorDefinitions').text = ';'.join(target_defines)
        ET.SubElement(clconf, 'MinimalRebuild').text = 'true'
        ET.SubElement(clconf, 'FunctionLevelLinking').text = 'true'
        pch_node = ET.SubElement(clconf, 'PrecompiledHeader')
        # Warning level
        warning_level = self.get_option_for_target('warning_level', target)
        ET.SubElement(clconf, 'WarningLevel').text = 'Level' + str(1 + int(warning_level))
        if self.get_option_for_target('werror', target):
            ET.SubElement(clconf, 'TreatWarningAsError').text = 'true'
        # Note: SuppressStartupBanner is /NOLOGO and is 'true' by default
        pch_sources = {}
        for lang in ['c', 'cpp']:
            pch = target.get_pch(lang)
            if not pch:
                continue
            pch_node.text = 'Use'
            if compiler.id == 'msvc':
                if len(pch) != 2:
                    raise MesonException('MSVC requires one header and one source to produce precompiled headers.')
                pch_sources[lang] = [pch[0], pch[1], lang]
            else:
                # I don't know whether its relevant but let's handle other compilers
                # used with a vs backend
                pch_sources[lang] = [pch[0], None, lang]
        if len(pch_sources) == 1:
            # If there is only 1 language with precompiled headers, we can use it for the entire project, which
            # is cleaner than specifying it for each source file.
            pch_source = list(pch_sources.values())[0]
            header = os.path.join(proj_to_src_dir, pch_source[0])
            pch_file = ET.SubElement(clconf, 'PrecompiledHeaderFile')
            pch_file.text = header
            pch_include = ET.SubElement(clconf, 'ForcedIncludeFiles')
            pch_include.text = header + ';%(ForcedIncludeFiles)'
            pch_out = ET.SubElement(clconf, 'PrecompiledHeaderOutputFile')
            pch_out.text = '$(IntDir)$(TargetName)-%s.pch' % pch_source[2]

        resourcecompile = ET.SubElement(compiles, 'ResourceCompile')
        ET.SubElement(resourcecompile, 'PreprocessorDefinitions')

        # Linker options
        link = ET.SubElement(compiles, 'Link')
        extra_link_args = CompilerArgs(compiler)
        # FIXME: Can these buildtype linker args be added as tags in the
        # vcxproj file (similar to buildtype compiler args) instead of in
        # AdditionalOptions?
        extra_link_args += compiler.get_buildtype_linker_args(self.buildtype)
        # Generate Debug info
        if self.buildtype.startswith('debug'):
            self.generate_debug_information(link)
        if not isinstance(target, build.StaticLibrary):
            if isinstance(target, build.SharedModule):
                extra_link_args += compiler.get_std_shared_module_link_args()
            # Add link args added using add_project_link_arguments()
            extra_link_args += self.build.get_project_link_args(compiler, target.subproject)
            # Add link args added using add_global_link_arguments()
            # These override per-project link arguments
            extra_link_args += self.build.get_global_link_args(compiler)
            if not target.is_cross:
                # Link args added from the env: LDFLAGS. We want these to
                # override all the defaults but not the per-target link args.
                extra_link_args += self.environment.coredata.external_link_args[compiler.get_language()]
            # Only non-static built targets need link args and link dependencies
            extra_link_args += target.link_args
            # External deps must be last because target link libraries may depend on them.
            for dep in target.get_external_deps():
                # Extend without reordering or de-dup to preserve `-L -l` sets
                # https://github.com/mesonbuild/meson/issues/1718
                extra_link_args.extend_direct(dep.get_link_args())
            for d in target.get_dependencies():
                if isinstance(d, build.StaticLibrary):
                    for dep in d.get_external_deps():
                        extra_link_args.extend_direct(dep.get_link_args())
        # Add link args for c_* or cpp_* build options. Currently this only
        # adds c_winlibs and cpp_winlibs when building for Windows. This needs
        # to be after all internal and external libraries so that unresolved
        # symbols from those can be found here. This is needed when the
        # *_winlibs that we want to link to are static mingw64 libraries.
        extra_link_args += compiler.get_option_link_args(self.environment.coredata.compiler_options)
        (additional_libpaths, additional_links, extra_link_args) = self.split_link_args(extra_link_args.to_native())

        # Add more libraries to be linked if needed
        for t in target.get_dependencies():
            lobj = self.build.targets[t.get_id()]
            linkname = os.path.join(down, self.get_target_filename_for_linking(lobj))
            if t in target.link_whole_targets:
                # /WHOLEARCHIVE:foo must go into AdditionalOptions
                extra_link_args += compiler.get_link_whole_for(linkname)
                # To force Visual Studio to build this project even though it
                # has no sources, we include a reference to the vcxproj file
                # that builds this target. Technically we should add this only
                # if the current target has no sources, but it doesn't hurt to
                # have 'extra' references.
                trelpath = self.get_target_dir_relative_to(t, target)
                tvcxproj = os.path.join(trelpath, t.get_id() + '.vcxproj')
                tid = self.environment.coredata.target_guids[t.get_id()]
                self.add_project_reference(root, tvcxproj, tid)
            else:
                # Other libraries go into AdditionalDependencies
                additional_links.append(linkname)
        for lib in self.get_custom_target_provided_libraries(target):
            additional_links.append(self.relpath(lib, self.get_target_dir(target)))
        additional_objects = []
        for o in self.flatten_object_list(target, down):
            assert(isinstance(o, str))
            additional_objects.append(o)
        for o in custom_objs:
            additional_objects.append(o)

        if len(extra_link_args) > 0:
            extra_link_args.append('%(AdditionalOptions)')
            ET.SubElement(link, "AdditionalOptions").text = ' '.join(extra_link_args)
        if len(additional_libpaths) > 0:
            additional_libpaths.insert(0, '%(AdditionalLibraryDirectories)')
            ET.SubElement(link, 'AdditionalLibraryDirectories').text = ';'.join(additional_libpaths)
        if len(additional_links) > 0:
            additional_links.append('%(AdditionalDependencies)')
            ET.SubElement(link, 'AdditionalDependencies').text = ';'.join(additional_links)
        ofile = ET.SubElement(link, 'OutputFile')
        ofile.text = '$(OutDir)%s' % target.get_filename()
        subsys = ET.SubElement(link, 'SubSystem')
        subsys.text = subsystem
        if (isinstance(target, build.SharedLibrary) or isinstance(target, build.Executable)) and target.get_import_filename():
            # DLLs built with MSVC always have an import library except when
            # they're data-only DLLs, but we don't support those yet.
            ET.SubElement(link, 'ImportLibrary').text = target.get_import_filename()
        if isinstance(target, build.SharedLibrary):
            # Add module definitions file, if provided
            if target.vs_module_defs:
                relpath = os.path.join(down, target.vs_module_defs.rel_to_builddir(self.build_to_src))
                ET.SubElement(link, 'ModuleDefinitionFile').text = relpath
        if '/ZI' in buildtype_args or '/Zi' in buildtype_args:
            pdb = ET.SubElement(link, 'ProgramDataBaseFileName')
            pdb.text = '$(OutDir}%s.pdb' % target_name
        if isinstance(target, build.Executable):
            ET.SubElement(link, 'EntryPointSymbol').text = entrypoint
        targetmachine = ET.SubElement(link, 'TargetMachine')
        targetplatform = self.platform.lower()
        if targetplatform == 'win32':
            targetmachine.text = 'MachineX86'
        elif targetplatform == 'x64':
            targetmachine.text = 'MachineX64'
        elif targetplatform == 'arm':
            targetmachine.text = 'MachineARM'
        else:
            raise MesonException('Unsupported Visual Studio target machine: ' + targetmachine)

        extra_files = target.extra_files
        if len(headers) + len(gen_hdrs) + len(extra_files) > 0:
            inc_hdrs = ET.SubElement(root, 'ItemGroup')
            for h in headers:
                relpath = os.path.join(down, h.rel_to_builddir(self.build_to_src))
                ET.SubElement(inc_hdrs, 'CLInclude', Include=relpath)
            for h in gen_hdrs:
                ET.SubElement(inc_hdrs, 'CLInclude', Include=h)
            for h in target.extra_files:
                relpath = os.path.join(down, h.rel_to_builddir(self.build_to_src))
                ET.SubElement(inc_hdrs, 'CLInclude', Include=relpath)

        if len(sources) + len(gen_src) + len(pch_sources) > 0:
            inc_src = ET.SubElement(root, 'ItemGroup')
            for s in sources:
                relpath = os.path.join(down, s.rel_to_builddir(self.build_to_src))
                inc_cl = ET.SubElement(inc_src, 'CLCompile', Include=relpath)
                lang = Vs2010Backend.lang_from_source_file(s)
                self.add_pch(inc_cl, proj_to_src_dir, pch_sources, s)
                self.add_additional_options(lang, inc_cl, file_args)
                self.add_preprocessor_defines(lang, inc_cl, file_defines)
                self.add_include_dirs(lang, inc_cl, file_inc_dirs)
                ET.SubElement(inc_cl, 'ObjectFileName').text = "$(IntDir)" + self.object_filename_from_source(target, s, False)
            for s in gen_src:
                inc_cl = ET.SubElement(inc_src, 'CLCompile', Include=s)
                lang = Vs2010Backend.lang_from_source_file(s)
                self.add_pch(inc_cl, proj_to_src_dir, pch_sources, s)
                self.add_additional_options(lang, inc_cl, file_args)
                self.add_preprocessor_defines(lang, inc_cl, file_defines)
                self.add_include_dirs(lang, inc_cl, file_inc_dirs)
            for lang in pch_sources:
                header, impl, suffix = pch_sources[lang]
                if impl:
                    relpath = os.path.join(proj_to_src_dir, impl)
                    inc_cl = ET.SubElement(inc_src, 'CLCompile', Include=relpath)
                    pch = ET.SubElement(inc_cl, 'PrecompiledHeader')
                    pch.text = 'Create'
                    pch_out = ET.SubElement(inc_cl, 'PrecompiledHeaderOutputFile')
                    pch_out.text = '$(IntDir)$(TargetName)-%s.pch' % suffix
                    pch_file = ET.SubElement(inc_cl, 'PrecompiledHeaderFile')
                    # MSBuild searches for the header relative from the implementation, so we have to use
                    # just the file name instead of the relative path to the file.
                    pch_file.text = os.path.split(header)[1]
                    self.add_additional_options(lang, inc_cl, file_args)
                    self.add_preprocessor_defines(lang, inc_cl, file_defines)
                    self.add_include_dirs(lang, inc_cl, file_inc_dirs)

        if self.has_objects(objects, additional_objects, gen_objs):
            inc_objs = ET.SubElement(root, 'ItemGroup')
            for s in objects:
                relpath = os.path.join(down, s.rel_to_builddir(self.build_to_src))
                ET.SubElement(inc_objs, 'Object', Include=relpath)
            for s in additional_objects:
                ET.SubElement(inc_objs, 'Object', Include=s)
            self.add_generated_objects(inc_objs, gen_objs)

        ET.SubElement(root, 'Import', Project='$(VCTargetsPath)\Microsoft.Cpp.targets')
        # Reference the regen target.
        regen_vcxproj = os.path.join(self.environment.get_build_dir(), 'REGEN.vcxproj')
        self.add_project_reference(root, regen_vcxproj, self.environment.coredata.regen_guid)
        self._prettyprint_vcxproj_xml(ET.ElementTree(root), ofname)