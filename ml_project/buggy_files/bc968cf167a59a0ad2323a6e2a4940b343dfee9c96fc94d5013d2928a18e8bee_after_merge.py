def att_for(args):
    """Returns an attention layer given the program arguments.

    Args:
        args (Namespace): The arguments.

    Returns:
        chainer.Chain: The corresponding attention module.

    """
    if args.atype == 'dot':
        att = AttDot(args.eprojs, args.dunits, args.adim)
    elif args.atype == 'location':
        att = AttLoc(args.eprojs, args.dunits,
                     args.adim, args.aconv_chans, args.aconv_filts)
    elif args.atype == 'noatt':
        att = NoAtt()
    else:
        raise NotImplementedError('chainer supports only noatt, dot, and location attention.')
    return att