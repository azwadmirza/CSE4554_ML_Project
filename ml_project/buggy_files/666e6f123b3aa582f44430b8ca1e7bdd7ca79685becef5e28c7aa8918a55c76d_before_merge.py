def numericFormatter(fmtstr, typedval):
    fmtstr = fmtstr or options['disp_'+type(typedval).__name__+'_fmt']
    if fmtstr:
        if fmtstr[0] == '%':
            return locale.format_string(fmtstr, typedval, grouping=True)
        else:
            return fmtstr.format(typedval)
    return str(typedval)