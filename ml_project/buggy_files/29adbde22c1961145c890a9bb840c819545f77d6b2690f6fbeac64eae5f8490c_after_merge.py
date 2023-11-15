def patch_dmgbuild():
    if not MACOS:
        return
    from dmgbuild import core

    # will not be required after dmgbuild > v1.3.3
    # see https://github.com/al45tair/dmgbuild/pull/18
    with open(core.__file__, 'r') as f:
        src = f.read()
    if (
        'max(total_size / 1024' not in src
        and "all_args = ['/usr/bin/hdiutil', cmd]" not in src
    ):
        return
    with open(core.__file__, 'w') as f:
        f.write(
            src.replace(
                'max(total_size / 1024', 'max(total_size / 1000'
            ).replace(
                "all_args = ['/usr/bin/hdiutil', cmd]",
                "all_args = ['sudo', '/usr/bin/hdiutil', cmd]",
            )
        )
        print("patched dmgbuild.core")