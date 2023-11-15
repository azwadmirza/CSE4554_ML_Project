    def checksec(self):
        elf_dict = {}
        elf_dict['name'] = self.elf_rel
        is_nx = self.is_nx()
        if is_nx:
            severity = 'info'
            desc = (
                'The shared object has NX bit set. This marks a '
                'memory page non-executable making attacker '
                'injected shellcode non-executable.')
        else:
            severity = 'high'
            desc = (
                'The shared object does not have NX bit set. NX bit '
                'offer protection against exploitation of memory corruption '
                'vulnerabilities by marking memory page as non-executable. '
                'Use option --noexecstack or -z noexecstack to mark stack as '
                'non executable.')
        elf_dict['nx'] = {
            'is_nx': is_nx,
            'severity': severity,
            'description': desc,
        }
        severity = 'info'
        is_pie = self.is_pie()
        if is_pie == 'dso':
            is_pie = 'Dynamic Shared Object (DSO)'
            desc = (
                'The shared object is build with -fPIC flag which '
                'enables Position independent code. This makes Return '
                'Oriented Programming (ROP) attacks much more difficult '
                'to execute reliably.')
        elif is_pie:
            desc = (
                'The shared object is build with -fPIC flag which '
                'enables Position independent code. This makes Return '
                'Oriented Programming (ROP) attacks much more difficult '
                'to execute reliably.')
        else:
            severity = 'high'
            desc = (
                'The shared object is built without Position '
                'Independent Code flag. In order to prevent '
                'an attacker from reliably jumping to, for example, a '
                'particular exploited function in memory, Address '
                'space layout randomization (ASLR) randomly arranges '
                'the address space positions of key data areas of a '
                'process, including the base of the executable and the '
                'positions of the stack,heap and libraries. Use compiler '
                'option -fPIC to enable Position Independent Code.')
        elf_dict['pie'] = {
            'is_pie': is_pie,
            'severity': severity,
            'description': desc,
        }
        has_canary = self.has_canary()
        if has_canary:
            severity = 'info'
            desc = (
                'This shared object has a stack canary value '
                'added to the stack so that it will be overwritten by '
                'a stack buffer that overflows the return address. '
                'This allows detection of overflows by verifying the '
                'integrity of the canary before function return.')
        else:
            severity = 'high'
            desc = (
                'This shared object does not have a stack '
                'canary value added to the stack. Stack canraies '
                'are used to detect and prevent exploits from '
                'overwriting return address. Use the option '
                '-fstack-protector-all to enable stack canaries.')
        elf_dict['stack_canary'] = {
            'has_canary': has_canary,
            'severity': severity,
            'description': desc,
        }
        relro = self.relro()
        if relro == 'Full':
            severity = 'info'
            desc = (
                'This shared object has full RELRO '
                'enabled. RELRO ensures that the GOT cannot be '
                'overwritten in vulnerable ELF binaries. '
                'In Full RELRO, the entire GOT (.got and '
                '.got.plt both) is marked as read-only.')
        elif relro == 'Partial':
            severity = 'warning'
            desc = (
                'This shared object has partial RELRO '
                'enabled. RELRO ensures that the GOT cannot be '
                'overwritten in vulnerable ELF binaries. '
                'In partial RELRO, the non-PLT part of the GOT '
                'section is read only but .got.plt is still '
                'writeable. Use the option -z,relro,-z,now to '
                'enable full RELRO.')
        else:
            severity = 'high'
            desc = (
                'This shared object does not have RELRO '
                'enabled. The entire GOT (.got and '
                '.got.plt both) are writable. Without this compiler '
                'flag, buffer overflows on a global variable can '
                'overwrite GOT entries. Use the option '
                '-z,relro,-z,now to enable full RELRO and only '
                '-z,relro to enable partial RELRO.')
        elf_dict['relocation_readonly'] = {
            'relro': relro,
            'severity': severity,
            'description': desc,
        }
        rpath = self.rpath()
        if rpath:
            severity = 'high'
            desc = (
                'The shared object has RPATH set. In certain cases '
                'an attacker can abuse this feature to run arbitrary '
                'shared objects for code execution and privilege '
                'escalation. The only time a shared library in '
                'should set RPATH is if it is linked to private '
                'shared libraries in the same package. Remove the '
                'compiler option -rpath to remove RPATH.')
        else:
            severity = 'info'
            desc = (
                'The shared object does not have run-time search path '
                'or RPATH set.')
        elf_dict['rpath'] = {
            'rpath': rpath,
            'severity': severity,
            'description': desc,
        }
        runpath = self.runpath()
        if runpath:
            severity = 'high'
            desc = (
                'The shared object has RUNPATH set. In certain cases '
                'an attacker can abuse this feature and or modify '
                'environment variables to run arbitrary '
                'shared objects for code execution and privilege '
                'escalation. The only time a shared library in should '
                'set RUNPATH is if it is linked to private shared '
                'libraries in the same package. Remove the compiler '
                'option --enable-new-dtags,-rpath to remove RUNPATH.')
            rnp = runpath.runpath
        else:
            severity = 'info'
            desc = (
                'The shared object does not have RUNPATH set.')
            rnp = runpath
        elf_dict['runpath'] = {
            'runpath': rnp,
            'severity': severity,
            'description': desc,
        }
        fortified_functions = self.fortify()
        if fortified_functions:
            severity = 'info'
            desc = ('The shared object has the '
                    f'following fortifed functions: {fortified_functions}')
        else:
            severity = 'warning'
            desc = ('The shared object does not have any '
                    'fortified functions. Fortified functions '
                    'provides buffer overflow checks against '
                    'glibc\'s commons insecure functions like '
                    'strcpy, gets etc. Use the compiler option '
                    '-D_FORTIFY_SOURCE=2 to fority functions.')
        elf_dict['fortify'] = {
            'is_fortified': bool(fortified_functions),
            'severity': severity,
            'description': desc,
        }
        is_stripped = self.is_symbols_stripped()
        if is_stripped:
            severity = 'info'
            desc = 'Symbols are stripped.'
        else:
            severity = 'warning'
            desc = 'Symbols are available.'
        elf_dict['symbol'] = {
            'is_stripped': is_stripped,
            'severity': severity,
            'description': desc,
        }
        return elf_dict