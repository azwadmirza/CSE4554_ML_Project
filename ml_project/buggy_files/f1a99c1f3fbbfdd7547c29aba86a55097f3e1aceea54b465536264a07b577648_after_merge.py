def explore(layer=None):
    """Function used to discover the Scapy layers and protocols.
    It helps to see which packets exists in contrib or layer files.

    params:
     - layer: If specified, the function will explore the layer. If not,
              the GUI mode will be activated, to browse the available layers

    examples:
      >>> explore()  # Launches the GUI
      >>> explore("dns")  # Explore scapy.layers.dns
      >>> explore("http2")  # Explore scapy.contrib.http2
      >>> explore(scapy.layers.bluetooth4LE)

    Note: to search a packet by name, use ls("name") rather than explore.
    """
    if layer is None:  # GUI MODE
        if not conf.interactive:
            raise Scapy_Exception("explore() GUI-mode cannot be run in "
                                  "interactive mode. Please provide a "
                                  "'layer' parameter !")
        # 0 - Imports
        try:
            import prompt_toolkit
        except ImportError:
            raise ImportError("prompt_toolkit is not installed ! "
                              "You may install IPython, which contains it, via"
                              " `pip install ipython`")
        if not _version_checker(prompt_toolkit, (2, 0)):
            raise ImportError("prompt_toolkit >= 2.0.0 is required !")
        # Only available with prompt_toolkit > 2.0, not released on PyPi yet
        from prompt_toolkit.shortcuts.dialogs import radiolist_dialog, \
            button_dialog
        from prompt_toolkit.formatted_text import HTML
        # Check for prompt_toolkit >= 3.0.0
        if _version_checker(prompt_toolkit, (3, 0)):
            call_ptk = lambda x: x.run()
        else:
            call_ptk = lambda x: x
        # 1 - Ask for layer or contrib
        btn_diag = button_dialog(
            title=six.text_type("Scapy v%s" % conf.version),
            text=HTML(
                six.text_type(
                    '<style bg="white" fg="red">Chose the type of packets'
                    ' you want to explore:</style>'
                )
            ),
            buttons=[
                (six.text_type("Layers"), "layers"),
                (six.text_type("Contribs"), "contribs"),
                (six.text_type("Cancel"), "cancel")
            ])
        action = call_ptk(btn_diag)
        # 2 - Retrieve list of Packets
        if action == "layers":
            # Get all loaded layers
            _radio_values = conf.layers.layers()
            # Restrict to layers-only (not contribs) + packet.py and asn1*.py
            _radio_values = [x for x in _radio_values if ("layers" in x[0] or
                                                          "packet" in x[0] or
                                                          "asn1" in x[0])]
        elif action == "contribs":
            # Get all existing contribs
            from scapy.main import list_contrib
            _radio_values = list_contrib(ret=True)
            _radio_values = [(x['name'], x['description'])
                             for x in _radio_values]
            # Remove very specific modules
            _radio_values = [x for x in _radio_values if not ("can" in x[0])]
        else:
            # Escape/Cancel was pressed
            return
        # Python 2 compat
        if six.PY2:
            _radio_values = [(six.text_type(x), six.text_type(y))
                             for x, y in _radio_values]
        # 3 - Ask for the layer/contrib module to explore
        rd_diag = radiolist_dialog(
            values=_radio_values,
            title=six.text_type("Scapy v%s" % conf.version),
            text=HTML(
                six.text_type(
                    '<style bg="white" fg="red">Please select a layer among'
                    ' the following, to see all packets contained in'
                    ' it:</style>'
                )
            ))
        result = call_ptk(rd_diag)
        if result is None:
            return  # User pressed "Cancel"
        # 4 - (Contrib only): load contrib
        if action == "contribs":
            from scapy.main import load_contrib
            load_contrib(result)
            result = "scapy.contrib." + result
    else:  # NON-GUI MODE
        # We handle layer as a short layer name, full layer name
        # or the module itself
        if isinstance(layer, types.ModuleType):
            layer = layer.__name__
        if isinstance(layer, str):
            if layer.startswith("scapy.layers."):
                result = layer
            else:
                if layer.startswith("scapy.contrib."):
                    layer = layer.replace("scapy.contrib.", "")
                from scapy.main import load_contrib
                load_contrib(layer)
                result_layer, result_contrib = (("scapy.layers.%s" % layer),
                                                ("scapy.contrib.%s" % layer))
                if result_layer in conf.layers.ldict:
                    result = result_layer
                elif result_contrib in conf.layers.ldict:
                    result = result_contrib
                else:
                    raise Scapy_Exception("Unknown scapy module '%s'" % layer)
        else:
            warning("Wrong usage ! Check out help(explore)")
            return

    # COMMON PART
    # Get the list of all Packets contained in that module
    try:
        all_layers = conf.layers.ldict[result]
    except KeyError:
        raise Scapy_Exception("Unknown scapy module '%s'" % layer)
    # Print
    print(conf.color_theme.layer_name("Packets contained in %s:" % result))
    rtlst = [(lay.__name__ or "", lay._name or "") for lay in all_layers]
    print(pretty_list(rtlst, [("Class", "Name")], borders=True))