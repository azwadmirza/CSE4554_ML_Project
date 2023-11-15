def start_with_computer(enabled):
    """If enabled, create shortcut to start application with computer.
    If disabled, then delete the shortcut."""
    if not enabled:
        # User requests to not automatically start BleachBit
        if os.path.lexists(bleachbit.autostart_path):
            # Delete the shortcut
            FileUtilities.delete(bleachbit.autostart_path)
        return
    # User requests to automatically start BleachBit
    if os.path.lexists(bleachbit.autostart_path):
        # Already automatic, so exit
        return
    if not os.path.exists(bleachbit.launcher_path):
        logger.error('%s does not exist: ', bleachbit.launcher_path)
        return
    import shutil
    General.makedirs(os.path.dirname(bleachbit.autostart_path))
    shutil.copy(bleachbit.launcher_path, bleachbit.autostart_path)
    os.chmod(bleachbit.autostart_path, 0o755)
    if General.sudo_mode():
        General.chownself(bleachbit.autostart_path)