def check_elf_built(f):
    has_pi = False
    has_sp = False
    has_pi_fg = {
        3: [8],  # EM_386=3,    R_386_RELATIVE=8,
        62: [8],  # EM_X86_64=62,    R_X86_64_RELATIVE=8,
        40: [23, 3],  # EM_ARM=40,    R_ARM_RELATIVE=23,R_ARM_REL32=3,
        183: [1027, 3],  # EM_AARCH64=183,
                         # R_AARCH64_RELATIVE=1027,R_ARM_REL32=3,
        8: [3],  # EM_MIPS=8,    R_MIPS_REL32=3,
    }
    elffile = TinyELFFile(f)
    for i in range(elffile.header['e_shnum']):
        section_header = elffile.decode_shdr(
            elffile.header['e_shoff'] + i * elffile.header['e_shentsize'])
        sectype = section_header['sh_type']
        if sectype in (4, 9):  # SHT_RELA=4,SHT_REL=9,
            if section_header['sh_entsize'] > 0:
                siz = section_header['sh_size'] // section_header['sh_entsize']
                for i in range(siz):
                    elffile.stream.seek(
                        section_header['sh_offset']
                        + i
                        * section_header['sh_entsize'])
                    if section_header['sh_type'] == 9:
                        entry = elffile.decode_rel(
                            section_header['sh_offset']
                            + i
                            * section_header['sh_entsize'])
                    elif section_header['sh_type'] == 4:
                        entry = elffile.decode_rela(
                            section_header['sh_offset']
                            + i
                            * section_header['sh_entsize'])
                    else:
                        continue
                    if (entry['r_info_type']
                            in has_pi_fg.get(elffile.header['e_machine'], [])):
                        if entry['r_info_sym'] == 0:
                            has_pi = True
                            break
    return has_pi, has_sp