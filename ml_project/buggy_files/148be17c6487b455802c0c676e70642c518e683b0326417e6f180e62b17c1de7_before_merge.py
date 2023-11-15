def lock_options(f):
    f = install_base_options(f)
    f = lock_dev_option(f)
    f = emit_requirements_flag(f)
    f = dev_only_flag(f)
    return f