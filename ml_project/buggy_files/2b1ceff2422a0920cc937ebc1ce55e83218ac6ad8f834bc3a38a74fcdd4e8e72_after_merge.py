    def __getattr__(self, attr):
        attr = attr.lstrip('$')
        try:
            # Seriously, gdb? Only accepts uint32.
            if 'eflags' in attr or 'cpsr' in attr:
                value = gdb77_get_register(attr)
                value = value.cast(pwndbg.typeinfo.uint32)
            else:
                if attr.lower() == 'xpsr':
                    attr = 'xPSR'
                value = get_register(attr)
                value = value.cast(pwndbg.typeinfo.ptrdiff)

            value = int(value)
            return value & pwndbg.arch.ptrmask
        except (ValueError, gdb.error):
            return None