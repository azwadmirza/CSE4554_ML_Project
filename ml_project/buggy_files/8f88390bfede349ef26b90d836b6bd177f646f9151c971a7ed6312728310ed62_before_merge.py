def build_block_parser(md, **kwargs):
    """ Build the default block parser used by Markdown. """
    parser = BlockParser(md)
    parser.blockprocessors.register(EmptyBlockProcessor(parser), 'empty', 100)
    parser.blockprocessors.register(ListIndentProcessor(parser), 'indent', 90)
    parser.blockprocessors.register(CodeBlockProcessor(parser), 'code', 80)
    parser.blockprocessors.register(HashHeaderProcessor(parser), 'hashheader', 70)
    parser.blockprocessors.register(SetextHeaderProcessor(parser), 'setextheader', 60)
    parser.blockprocessors.register(HRProcessor(parser), 'hr', 50)
    parser.blockprocessors.register(OListProcessor(parser), 'olist', 40)
    parser.blockprocessors.register(UListProcessor(parser), 'ulist', 30)
    parser.blockprocessors.register(BlockQuoteProcessor(parser), 'quote', 20)
    parser.blockprocessors.register(ParagraphProcessor(parser), 'paragraph', 10)
    return parser