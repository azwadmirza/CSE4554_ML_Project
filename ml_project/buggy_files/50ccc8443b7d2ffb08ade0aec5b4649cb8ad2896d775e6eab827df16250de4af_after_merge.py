def saveMacro(self, rows, ks):
        vs = copy(self)
        vs.rows = rows
        macropath = Path(fnSuffix(options.visidata_dir+"macro"))
        vd.save_vd(macropath, vs)
        setMacro(ks, vs)
        append_tsv_row(vd.macrosheet.source, (ks, macropath))