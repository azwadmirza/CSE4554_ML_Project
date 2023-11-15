def elf_analysis(app_dir: str) -> list:
    """Perform the elf analysis."""
    try:
        logger.info("Static Android Binary Analysis Started")
        elf_desc = {
            'elf_no_pi':
                (
                    'Found elf built without Position Independent Executable (PIE) flag',
                    'high',
                    'In order to prevent an attacker from reliably jumping to, for example, a particular'
                    ' exploited function in memory, Address space layout randomization (ASLR) randomly '
                    'arranges the address space positions of key data areas of a process, including the '
                    'base of the executable and the positions of the stack, heap and libraries. Built with'
                    ' option <strong>-pie</strong>.'
                )
        }
        elf_an_dic = {}
        for k in list(elf_desc.keys()):
            elf_an_dic[k] = []
        libdir = os.path.join(app_dir, "lib")
        if os.path.exists(libdir):
            for pdir, dirl, filel in os.walk(libdir):
                for filename in filel:
                    if filename.endswith(".so"):
                        try:
                            filepath = os.path.join(pdir, filename)
                            f = io.open(filepath, mode='rb')
                            has_pie, has_sg = check_elf_built(f)
                            f.close()
                            if not has_pie:
                                if not any(pie_str in ["nopie", "nonpie", "no-pie"] for pie_str in filename):
                                    elf_an_dic['elf_no_pi'].append(
                                        filepath.replace(libdir, "lib"))
                        except Exception as e:
                            pass
        res = []
        for k, filelist in list(elf_an_dic.items()):
            if len(filelist):
                descs = elf_desc.get(k)
                res.append({'title': descs[0],
                            'stat': descs[1],
                            'desc': descs[2],
                            'file': " ".join(filelist),
                            })
        return res

    except:
        PrintException("Performing Binary Analysis")