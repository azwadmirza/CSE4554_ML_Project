def write_config(resx, resy):
    wrd = bpy.data.worlds['Arm']
    p = os.path.join(arm.utils.get_fp(), 'Bundled')
    if not os.path.exists(p):
        os.makedirs(p)

    rpdat = arm.utils.get_rp()
    rp_shadowmap_cube = int(rpdat.rp_shadowmap_cube) if rpdat.rp_shadows else 0
    rp_shadowmap_cascade = arm.utils.get_cascade_size(rpdat) if rpdat.rp_shadows else 0

    output = {
        'window_mode': get_winmode(wrd.arm_winmode),
        'window_w': int(resx),
        'window_h': int(resy),
        'window_resizable': wrd.arm_winresize,
        'window_maximizable': wrd.arm_winresize and wrd.arm_winmaximize,
        'window_minimizable': wrd.arm_winminimize,
        'window_vsync': wrd.arm_vsync,
        'window_msaa': int(rpdat.arm_samples_per_pixel),
        'window_scale': 1.0,
        'rp_supersample': float(rpdat.rp_supersampling),
        'rp_shadowmap_cube': rp_shadowmap_cube,
        'rp_shadowmap_cascade': rp_shadowmap_cascade,
        'rp_ssgi': rpdat.rp_ssgi != 'Off',
        'rp_ssr': rpdat.rp_ssr != 'Off',
        'rp_bloom': rpdat.rp_bloom != 'Off',
        'rp_motionblur': rpdat.rp_motionblur != 'Off',
        'rp_gi': rpdat.rp_voxelao,
        'rp_dynres': rpdat.rp_dynres
    }

    with open(os.path.join(p, 'config.arm'), 'w') as configfile:
        configfile.write(json.dumps(output, sort_keys=True, indent=4))