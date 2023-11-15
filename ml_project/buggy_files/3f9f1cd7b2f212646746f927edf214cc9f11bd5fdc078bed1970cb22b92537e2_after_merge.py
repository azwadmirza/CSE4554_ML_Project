def write_khafilejs(is_play, export_physics: bool, export_navigation: bool, export_ui: bool, is_publish: bool,
                    enable_dce: bool, import_traits: List[str], import_logicnodes) -> None:
    wrd = bpy.data.worlds['Arm']

    sdk_path = arm.utils.get_sdk_path()
    rel_path = arm.utils.get_relative_paths()  # Convert absolute paths to relative
    project_path = arm.utils.get_fp()
    build_dir = arm.utils.build_dir()

    # Whether to use relative paths for paths inside the SDK
    do_relpath_sdk = rel_path and on_same_drive(sdk_path, project_path)

    with open('khafile.js', 'w', encoding="utf-8") as khafile:
        khafile.write(
"""// Auto-generated
let project = new Project('""" + arm.utils.safesrc(wrd.arm_project_name + '-' + wrd.arm_project_version) + """');

project.addSources('Sources');
""")

        # Auto-add assets located in Bundled directory
        if os.path.exists('Bundled'):
            for file in glob.glob("Bundled/**", recursive=True):
                if os.path.isfile(file):
                    assets.add(file)

        # Add project shaders
        if os.path.exists('Shaders'):
            # Copy to enable includes
            shader_path = os.path.join(build_dir, 'compiled', 'Shaders', 'Project')
            if os.path.exists(shader_path):
                shutil.rmtree(shader_path, onerror=remove_readonly)
            shutil.copytree('Shaders', shader_path)

            khafile.write("project.addShaders('" + build_dir + "/compiled/Shaders/Project/**');\n")
            # for file in glob.glob("Shaders/**", recursive=True):
            #     if os.path.isfile(file):
            #         assets.add_shader(file)

        # Add engine sources if the project does not use its own armory/iron versions
        if not os.path.exists(os.path.join('Libraries', 'armory')):
            khafile.write(add_armory_library(sdk_path, 'armory', rel_path=do_relpath_sdk))
        if not os.path.exists(os.path.join('Libraries', 'iron')):
            khafile.write(add_armory_library(sdk_path, 'iron', rel_path=do_relpath_sdk))

        # Project libraries
        if os.path.exists('Libraries'):
            libs = os.listdir('Libraries')
            for lib in libs:
                if os.path.isdir('Libraries/' + lib):
                    khafile.write('project.addLibrary("{0}");\n'.format(lib.replace('//', '/')))

        # Subprojects, merge this with libraries
        if os.path.exists('Subprojects'):
            libs = os.listdir('Subprojects')
            for lib in libs:
                if os.path.isdir('Subprojects/' + lib):
                    khafile.write('await project.addProject("Subprojects/{0}");\n'.format(lib))

        if export_physics:
            assets.add_khafile_def('arm_physics')
            if wrd.arm_physics_engine == 'Bullet':
                assets.add_khafile_def('arm_bullet')
                if not os.path.exists('Libraries/haxebullet'):
                    khafile.write(add_armory_library(sdk_path + '/lib/', 'haxebullet', rel_path=do_relpath_sdk))
                if state.target.startswith('krom'):
                    ammojs_path = sdk_path + '/lib/haxebullet/ammo/ammo.wasm.js'
                    ammojs_path = ammojs_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_path, rel_path=do_relpath_sdk))
                    ammojs_wasm_path = sdk_path + '/lib/haxebullet/ammo/ammo.wasm.wasm'
                    ammojs_wasm_path = ammojs_wasm_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_wasm_path, rel_path=do_relpath_sdk))
                elif state.target == 'html5' or state.target == 'node':
                    ammojs_path = sdk_path + '/lib/haxebullet/ammo/ammo.js'
                    ammojs_path = ammojs_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_path, rel_path=do_relpath_sdk))
            elif wrd.arm_physics_engine == 'Oimo':
                assets.add_khafile_def('arm_oimo')
                if not os.path.exists('Libraries/oimo'):
                    khafile.write(add_armory_library(sdk_path + '/lib/', 'oimo', rel_path=do_relpath_sdk))

        if export_navigation:
            assets.add_khafile_def('arm_navigation')
            if not os.path.exists('Libraries/haxerecast'):
                khafile.write(add_armory_library(sdk_path + '/lib/', 'haxerecast', rel_path=do_relpath_sdk))
            if state.target.startswith('krom') or state.target == 'html5':
                recastjs_path = sdk_path + '/lib/haxerecast/js/recast/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/').replace('//', '/')
                khafile.write(add_assets(recastjs_path, rel_path=do_relpath_sdk))

        if is_publish:
            assets.add_khafile_def('arm_published')
            if wrd.arm_asset_compression:
                assets.add_khafile_def('arm_compress')
        else:
            pass
            # khafile.write("""project.addParameter("--macro include('armory.trait')");\n""")
            # khafile.write("""project.addParameter("--macro include('armory.trait.internal')");\n""")
            # if export_physics:
            #     khafile.write("""project.addParameter("--macro include('armory.trait.physics')");\n""")
            #     if wrd.arm_physics_engine == 'Bullet':
            #         khafile.write("""project.addParameter("--macro include('armory.trait.physics.bullet')");\n""")
            #     else:
            #         khafile.write("""project.addParameter("--macro include('armory.trait.physics.oimo')");\n""")
            # if export_navigation:
            #     khafile.write("""project.addParameter("--macro include('armory.trait.navigation')");\n""")

        # if import_logicnodes: # Live patching for logic nodes
            # khafile.write("""project.addParameter("--macro include('armory.logicnode')");\n""")

        if not wrd.arm_compiler_inline:
            khafile.write("project.addParameter('--no-inline');\n")

        if enable_dce:
            khafile.write("project.addParameter('-dce full');\n")

        live_patch = wrd.arm_live_patch and state.target == 'krom'
        if wrd.arm_debug_console or live_patch:
            import_traits.append('armory.trait.internal.Bridge')
            if live_patch:
                assets.add_khafile_def('arm_patch')

        import_traits = list(set(import_traits))
        for i in range(0, len(import_traits)):
            khafile.write("project.addParameter('" + import_traits[i] + "');\n")
            khafile.write("""project.addParameter("--macro keep('""" + import_traits[i] + """')");\n""")

        noembed = wrd.arm_cache_build and not is_publish and state.target == 'krom'
        if noembed:
            # Load shaders manually
            assets.add_khafile_def('arm_noembed')

        noembed = False # TODO: always embed shaders for now, check compatibility with haxe compile server

        shaders_path = build_dir + '/compiled/Shaders/*.glsl'
        if rel_path:
            shaders_path = os.path.relpath(shaders_path, project_path).replace('\\', '/')
        khafile.write('project.addShaders("' + shaders_path + '", { noembed: ' + str(noembed).lower() + '});\n')

        if arm.utils.get_gapi() == 'direct3d11':
            # noprocessing flag - gets renamed to .d3d11
            shaders_path = build_dir + '/compiled/Hlsl/*.glsl'
            if rel_path:
                shaders_path = os.path.relpath(shaders_path, project_path).replace('\\', '/')
            khafile.write('project.addShaders("' + shaders_path + '", { noprocessing: true, noembed: ' + str(noembed).lower() + ' });\n')

        # Move assets for published game to /data folder
        use_data_dir = is_publish and (state.target == 'krom-windows' or state.target == 'krom-linux' or state.target == 'windows-hl' or state.target == 'linux-hl')
        if use_data_dir:
            assets.add_khafile_def('arm_data_dir')

        ext = 'arm' if wrd.arm_minimize else 'json'
        assets_path = build_dir + '/compiled/Assets/**'
        assets_path_sh = build_dir + '/compiled/Shaders/*.' + ext
        if rel_path:
            assets_path = os.path.relpath(assets_path, project_path).replace('\\', '/')
            assets_path_sh = os.path.relpath(assets_path_sh, project_path).replace('\\', '/')
        dest = ''
        if use_data_dir:
            dest += ', destination: "data/{name}"'
        khafile.write('project.addAssets("' + assets_path + '", { notinlist: true ' + dest + '});\n')
        khafile.write('project.addAssets("' + assets_path_sh + '", { notinlist: true ' + dest + '});\n')

        shader_data_references = sorted(list(set(assets.shader_datas)))
        for ref in shader_data_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if '/compiled/' in ref: # Asset already included
                continue
            do_relpath_shaders = rel_path and on_same_drive(ref, project_path)
            khafile.write(add_assets(ref, use_data_dir=use_data_dir, rel_path=do_relpath_shaders))

        asset_references = sorted(list(set(assets.assets)))
        for ref in asset_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if '/compiled/' in ref: # Asset already included
                continue
            quality = 1.0
            s = ref.lower()
            if s.endswith('.wav'):
                quality = wrd.arm_sound_quality
            elif s.endswith('.png') or s.endswith('.jpg'):
                quality = wrd.arm_texture_quality

            do_relpath_assets = rel_path and on_same_drive(ref, project_path)
            khafile.write(add_assets(ref, quality=quality, use_data_dir=use_data_dir, rel_path=do_relpath_assets))

        if wrd.arm_sound_quality < 1.0 or state.target == 'html5':
            assets.add_khafile_def('arm_soundcompress')

        if wrd.arm_audio == 'Disabled':
            assets.add_khafile_def('kha_no_ogg')
        else:
            assets.add_khafile_def('arm_audio')

        if wrd.arm_texture_quality < 1.0:
            assets.add_khafile_def('arm_texcompress')

        if wrd.arm_debug_console:
            assets.add_khafile_def('arm_debug')
            khafile.write(add_shaders(sdk_path + "/armory/Shaders/debug_draw/**", rel_path=do_relpath_sdk))

        if wrd.arm_verbose_output:
            khafile.write("project.addParameter('--times');\n")

        if export_ui:
            if not os.path.exists('Libraries/zui'):
                khafile.write(add_armory_library(sdk_path, 'lib/zui', rel_path=do_relpath_sdk))
            p = sdk_path + '/armory/Assets/font_default.ttf'
            p = p.replace('//', '/')
            khafile.write(add_assets(p.replace('\\', '/'), use_data_dir=use_data_dir, rel_path=do_relpath_sdk))
            assets.add_khafile_def('arm_ui')

        if not wrd.arm_minimize:
            assets.add_khafile_def('arm_json')

        if wrd.arm_deinterleaved_buffers:
            assets.add_khafile_def('arm_deinterleaved')

        if wrd.arm_batch_meshes:
            assets.add_khafile_def('arm_batch')

        if wrd.arm_stream_scene:
            assets.add_khafile_def('arm_stream')

        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin != 'Off':
            assets.add_khafile_def('arm_skin')

        if rpdat.arm_particles != 'Off':
            assets.add_khafile_def('arm_particles')

        if rpdat.rp_draw_order == 'Shader':
            assets.add_khafile_def('arm_draworder_shader')

        if arm.utils.get_viewport_controls() == 'azerty':
            assets.add_khafile_def('arm_azerty')

        if os.path.exists(project_path + '/Bundled/config.arm'):
            assets.add_khafile_def('arm_config')

        if is_publish and wrd.arm_loadscreen:
            assets.add_khafile_def('arm_loadscreen')

        if wrd.arm_winresize or state.target == 'html5':
            assets.add_khafile_def('arm_resizable')

        # if bpy.data.scenes[0].unit_settings.system_rotation == 'DEGREES':
            # assets.add_khafile_def('arm_degrees')

        for d in assets.khafile_defs:
            khafile.write("project.addDefine('" + d + "');\n")

        for p in assets.khafile_params:
            khafile.write("project.addParameter('" + p + "');\n")

        # Let libraries differentiate between Armory and pure Kha
        assets.add_khafile_def('armory')

        if state.target.startswith('android'):
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            khafile.write("project.targetOptions.android_native.package = '{0}';\n".format(arm.utils.safestr(bundle)))
            if wrd.arm_winorient != 'Multi':
                khafile.write("project.targetOptions.android_native.screenOrientation = '{0}';\n".format(wrd.arm_winorient.lower()))
            # Android SDK Versions
            khafile.write("project.targetOptions.android_native.compileSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_compile))
            khafile.write("project.targetOptions.android_native.minSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_min))
            khafile.write("project.targetOptions.android_native.targetSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_target))
            # Permissions
            if len(wrd.arm_exporter_android_permission_list) > 0:
                perms = ''
                for item in wrd.arm_exporter_android_permission_list:
                    perm = "'android.permission."+ item.arm_android_permissions + "'"
                    # Checking In
                    if perms.find(perm) == -1:
                        if len(perms) > 0:
                            perms = perms + ', ' + perm
                        else:
                            perms = perm
                if len(perms) > 0:
                    khafile.write("project.targetOptions.android_native.permissions = [{0}];\n".format(perms))
            # Android ABI Filters
            if len(wrd.arm_exporter_android_abi_list) > 0:
                abis = ''
                for item in wrd.arm_exporter_android_abi_list:
                    abi = "'"+ item.arm_android_abi + "'"
                    # Checking In
                    if abis.find(abi) == -1:
                        if len(abis) > 0:
                            abis = abis + ', ' + abi
                        else:
                            abis = abi
                if len(abis) > 0:
                    khafile.write("project.targetOptions.android_native.abiFilters = [{0}];\n".format(abis))
        elif state.target.startswith('ios'):
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            khafile.write("project.targetOptions.ios.bundle = '{0}';\n".format(arm.utils.safestr(bundle)))

        if wrd.arm_project_icon != '':
            shutil.copy(bpy.path.abspath(wrd.arm_project_icon), project_path + '/icon.png')

        if wrd.arm_khafile is not None:
            khafile.write(wrd.arm_khafile.as_string())

        khafile.write("\n\nresolve(project);\n")