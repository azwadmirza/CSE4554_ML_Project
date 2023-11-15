    def print_help(event, module_name, help_text):
        """Print the help text for a module"""
        printer = wx.html.HtmlEasyPrinting("Printing %s" % module_name)
        printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        printer.PrintText(help_text)