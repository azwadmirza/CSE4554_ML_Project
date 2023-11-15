    def _setup_cmake_dir(self, cmake_file: str) -> str:
        # Setup the CMake build environment and return the "build" directory
        build_dir = self._get_build_dir()

        # Insert language parameters into the CMakeLists.txt and write new CMakeLists.txt
        src_cmake = Path(__file__).parent / 'data' / cmake_file
        cmake_txt = src_cmake.read_text()

        # In general, some Fortran CMake find_package() also require C language enabled,
        # even if nothing from C is directly used. An easy Fortran example that fails
        # without C language is
        #   find_package(Threads)
        # To make this general to
        # any other language that might need this, we use a list for all
        # languages and expand in the cmake Project(... LANGUAGES ...) statement.
        from ..cmake import language_map
        cmake_language = [language_map[x] for x in self.language_list if x in language_map]
        if not cmake_language:
            cmake_language += ['NONE']

        cmake_txt = """
cmake_minimum_required(VERSION ${{CMAKE_VERSION}})
project(MesonTemp LANGUAGES {})
""".format(' '.join(cmake_language)) + cmake_txt

        cm_file = Path(build_dir) / 'CMakeLists.txt'
        cm_file.write_text(cmake_txt)
        mlog.cmd_ci_include(cm_file.absolute().as_posix())

        return build_dir