    def __prepare_plot(self):
        try:
            import guiqwt.pyplot   #analysis:ignore
            return True
        except (ImportError, AssertionError):
            try:
                if 'matplotlib' not in sys.modules:
                    import matplotlib
                    matplotlib.use("Qt4Agg")
                return True
            except ImportError:
                QMessageBox.warning(self, _("Import error"),
                                    _("Please install <b>matplotlib</b>"
                                      " or <b>guiqwt</b>."))