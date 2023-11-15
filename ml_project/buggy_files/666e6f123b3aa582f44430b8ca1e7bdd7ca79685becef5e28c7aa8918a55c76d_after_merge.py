def numericFormatter(fmtstr, typedval):
    try:
        fmtstr = fmtstr or options['disp_'+type(typedval).__name__+'_fmt']
        if fmtstr[0] == '%':
            return locale.format_string(fmtstr, typedval, grouping=True)
        else:
            return fmtstr.format(typedval)
    except ValueError:
        return str(typedval)