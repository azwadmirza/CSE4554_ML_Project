def patch_dmgbuild():
    if not MACOS:
        return
    from dmgbuild import core

    # will not be required after dmgbuild > v1.3.3
    # see https://github.com/al45tair/dmgbuild/pull/18
    with open(core.__file__, 'r') as f:
        src = f.read()
    with open(core.__file__, 'w') as f:
        f.write(
            src.replace(
                "shutil.rmtree(os.path.join(mount_point, '.Trashes'), True)",
                "shutil.rmtree(os.path.join(mount_point, '.Trashes'), True);time.sleep(30)",
            )
        )
        print("patched dmgbuild.core")