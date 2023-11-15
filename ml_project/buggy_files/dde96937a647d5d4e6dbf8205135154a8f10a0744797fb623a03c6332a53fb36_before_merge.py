def macrosheet(vd):
    macrospath = Path(os.path.join(options.visidata_dir, 'macros.tsv'))
    macrosheet = vd.loadInternalSheet(TsvSheet, macrospath, columns=(ColumnItem('command', 0), ColumnItem('filename', 1))) or vd.error('error loading macros')

    real_macrosheet = IndexSheet('user_macros', rows=[])
    for ks, fn in macrosheet.rows:
        vs = vd.loadInternalSheet(CommandLog, Path(fn))
        vd.status(f"setting {ks}")
        setMacro(ks, vs)
        real_macrosheet.addRow(vs)

    return real_macrosheet