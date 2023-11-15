def build(target_python, requirements):
    """
    Builds an APK given a target Python and a set of requirements.
    """
    if not requirements:
        return
    testapp = 'setup_testapp_python2.py'
    android_sdk_home = os.environ['ANDROID_SDK_HOME']
    android_ndk_home = os.environ['ANDROID_NDK_HOME']
    if target_python == TargetPython.python3:
        testapp = 'setup_testapp_python3.py'
    requirements.add(target_python.name)
    requirements = ','.join(requirements)
    print('requirements:', requirements)
    with current_directory('testapps/'):
        try:
            for line in sh.python(
                    testapp, 'apk', '--sdk-dir', android_sdk_home,
                    '--ndk-dir', android_ndk_home, '--bootstrap', 'sdl2', '--requirements',
                    requirements, _err_to_out=True, _iter=True):
                print(line)
        except sh.ErrorReturnCode as e:
            raise