def write_config(resx, resy):
    wrd = bpy.data.worlds['Arm']
    p = arm.utils.get_fp() + '/Bundled'
    if not os.path.exists(p):
        os.makedirs(p)
    output = {}
    output['window_mode'] = get_winmode(wrd.arm_winmode)
    output['window_w'] = int(resx)
    output['window_h'] = int(resy)
    output['window_resizable'] = wrd.arm_winresize
    output['window_maximizable'] = wrd.arm_winresize and wrd.arm_winmaximize
    output['window_minimizable'] = wrd.arm_winminimize
    output['window_vsync'] = wrd.arm_vsync
    rpdat = arm.utils.get_rp()
    output['window_msaa'] = int(rpdat.arm_samples_per_pixel)
    output['window_scale'] = 1.0
    output['rp_supersample'] = float(rpdat.rp_supersampling)
    rp_shadowmap_cube = int(rpdat.rp_shadowmap_cube) if rpdat.rp_shadows else 0
    output['rp_shadowmap_cube'] = rp_shadowmap_cube
    rp_shadowmap_cascade = arm.utils.get_cascade_size(rpdat) if rpdat.rp_shadows else 0
    output['rp_shadowmap_cascade'] = rp_shadowmap_cascade
    output['rp_ssgi'] = rpdat.rp_ssgi != 'Off'
    output['rp_ssr'] = rpdat.rp_ssr != 'Off'
    output['rp_bloom'] = rpdat.rp_bloom != 'Off'
    output['rp_motionblur'] = rpdat.rp_motionblur != 'Off'
    output['rp_gi'] = rpdat.rp_voxelao
    output['rp_dynres'] = rpdat.rp_dynres
    with open(p + '/config.arm', 'w') as f:
        f.write(json.dumps(output, sort_keys=True, indent=4))