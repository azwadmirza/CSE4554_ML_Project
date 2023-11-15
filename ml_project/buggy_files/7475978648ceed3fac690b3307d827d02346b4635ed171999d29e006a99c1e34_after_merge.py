def pyinstall(source_folder):
    pyinstaller_path = os.path.join(os.getcwd(), 'pyinstaller')
    _install_pyintaller(pyinstaller_path)

    for folder in ("conan", "conan_server", "conan_build_info"):
        try:
            shutil.rmtree(os.path.join(pyinstaller_path, folder))
        except Exception as e:
            print("Unable to remove old folder", e)

    conan_path = os.path.join(source_folder, 'conans', 'conan.py')
    conan_server_path = os.path.join(source_folder, 'conans', 'conan_server.py')
    conan_build_info_path = os.path.join(source_folder, "conans/build_info/command.py")
    hidden = "--hidden-import=glob --hidden-import=pylint.reporters.text"
    if platform.system() != "Windows":
        hidden += " --hidden-import=setuptools.msvc"
    subprocess.call('python pyinstaller.py -y -p %s --console %s %s'
                    % (source_folder, conan_path, hidden),
                    cwd=pyinstaller_path, shell=True)
    _run_bin(pyinstaller_path)

    subprocess.call('python pyinstaller.py -y -p %s --console %s'
                    % (source_folder, conan_server_path),
                    cwd=pyinstaller_path, shell=True)

    subprocess.call('python pyinstaller.py -y -p %s --console %s -n conan_build_info'
                    % (source_folder, conan_build_info_path),
                    cwd=pyinstaller_path, shell=True)

    conan_bin = os.path.join(pyinstaller_path, 'conan', 'dist', 'conan')
    conan_server_folder = os.path.join(pyinstaller_path, 'conan_server', 'dist', 'conan_server')

    conan_build_info_folder = os.path.join(pyinstaller_path, 'conan_build_info', 'dist',
                                           'conan_build_info')
    dir_util.copy_tree(conan_server_folder, conan_bin)
    dir_util.copy_tree(conan_build_info_folder, conan_bin)
    _run_bin(pyinstaller_path)

    return os.path.abspath(os.path.join(pyinstaller_path, 'conan', 'dist', 'conan'))