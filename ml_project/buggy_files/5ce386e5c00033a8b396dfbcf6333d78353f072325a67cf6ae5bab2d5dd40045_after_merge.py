def get_env_patch(
        venv: str,
        language_version: str,
) -> PatchesT:
    patches: PatchesT = (
        ('GEM_HOME', os.path.join(venv, 'gems')),
        ('GEM_PATH', UNSET),
        ('BUNDLE_IGNORE_CONFIG', '1'),
    )
    if language_version == 'system':
        patches += (
            (
                'PATH', (
                    os.path.join(venv, 'gems', 'bin'), os.pathsep,
                    Var('PATH'),
                ),
            ),
        )
    else:  # pragma: win32 no cover
        patches += (
            ('RBENV_ROOT', venv),
            (
                'PATH', (
                    os.path.join(venv, 'gems', 'bin'), os.pathsep,
                    os.path.join(venv, 'shims'), os.pathsep,
                    os.path.join(venv, 'bin'), os.pathsep, Var('PATH'),
                ),
            ),
        )
    if language_version not in {'system', 'default'}:  # pragma: win32 no cover
        patches += (('RBENV_VERSION', language_version),)

    return patches