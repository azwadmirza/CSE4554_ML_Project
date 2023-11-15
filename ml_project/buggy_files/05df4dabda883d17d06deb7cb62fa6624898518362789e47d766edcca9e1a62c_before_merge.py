    def setup_page(self):
        template_btn = self.create_button(_("Edit template for new modules"),
                                    self.plugin.edit_template)
        
        interface_group = QGroupBox(_("Interface"))
        font_group = self.create_fontgroup(option=None,
                                    text=_("Text and margin font style"),
                                    fontfilters=QFontComboBox.MonospacedFonts)
        newcb = self.create_checkbox
        fpsorting_box = newcb(_("Sort files according to full path"),
                              'fullpath_sorting')
        showtabbar_box = newcb(_("Show tab bar"), 'show_tab_bar')

        interface_layout = QVBoxLayout()
        interface_layout.addWidget(fpsorting_box)
        interface_layout.addWidget(showtabbar_box)
        interface_group.setLayout(interface_layout)
        
        display_group = QGroupBox(_("Source code"))
        linenumbers_box = newcb(_("Show line numbers"), 'line_numbers')
        blanks_box = newcb(_("Show blank spaces"), 'blank_spaces')
        edgeline_box = newcb(_("Show vertical line after"), 'edge_line')
        edgeline_spin = self.create_spinbox("", _("characters"),
                                            'edge_line_column', 79, 1, 500)
        edgeline_box.toggled.connect(edgeline_spin.setEnabled)
        edgeline_spin.setEnabled(self.get_option('edge_line'))
        edgeline_layout = QHBoxLayout()
        edgeline_layout.addWidget(edgeline_box)
        edgeline_layout.addWidget(edgeline_spin)
        currentline_box = newcb(_("Highlight current line"),
                                'highlight_current_line')
        currentcell_box = newcb(_("Highlight current cell"),
                                'highlight_current_cell')
        occurence_box = newcb(_("Highlight occurences after"),
                              'occurence_highlighting')
        occurence_spin = self.create_spinbox("", " ms",
                                             'occurence_highlighting/timeout',
                                             min_=100, max_=1000000, step=100)
        occurence_box.toggled.connect(occurence_spin.setEnabled)
        occurence_spin.setEnabled(self.get_option('occurence_highlighting'))
        occurence_layout = QHBoxLayout()
        occurence_layout.addWidget(occurence_box)
        occurence_layout.addWidget(occurence_spin)
        wrap_mode_box = newcb(_("Wrap lines"), 'wrap')
        names = CONF.get('color_schemes', 'names')
        choices = list(zip(names, names))
        cs_combo = self.create_combobox(_("Syntax color scheme: "),
                                        choices, 'color_scheme_name')
        
        display_layout = QVBoxLayout()
        display_layout.addWidget(linenumbers_box)
        display_layout.addWidget(blanks_box)
        display_layout.addLayout(edgeline_layout)
        display_layout.addWidget(currentline_box)
        display_layout.addWidget(currentcell_box)
        display_layout.addLayout(occurence_layout)
        display_layout.addWidget(wrap_mode_box)
        display_layout.addWidget(cs_combo)
        display_group.setLayout(display_layout)

        run_group = QGroupBox(_("Run"))
        saveall_box = newcb(_("Save all files before running script"),
                            'save_all_before_run')
        
        run_selection_group = QGroupBox(_("Run selection"))
        focus_box = newcb(_("Maintain focus in the Editor after running cells or selections"),
                            'focus_to_editor')
        
        introspection_group = QGroupBox(_("Introspection"))
        rope_is_installed = programs.is_module_installed('rope')
        if rope_is_installed:
            completion_box = newcb(_("Automatic code completion"),
                                   'codecompletion/auto')
            case_comp_box = newcb(_("Case sensitive code completion"),
                                  'codecompletion/case_sensitive')
            comp_enter_box = newcb(_("Enter key selects completion"),
                                   'codecompletion/enter_key')
            calltips_box = newcb(_("Display balloon tips"), 'calltips')
            gotodef_box = newcb(_("Link to object definition"),
                  'go_to_definition',
                  tip=_("If this option is enabled, clicking on an object\n"
                        "name (left-click + Ctrl key) will go this object\n"
                        "definition (if resolved)."))
        else:
            rope_label = QLabel(_("<b>Warning:</b><br>"
                                  "The Python module <i>rope</i> is not "
                                  "installed on this computer: calltips, "
                                  "code completion and go-to-definition "
                                  "features won't be available."))
            rope_label.setWordWrap(True)
        
        sourcecode_group = QGroupBox(_("Source code"))
        closepar_box = newcb(_("Automatic insertion of parentheses, braces "
                                                               "and brackets"),
                             'close_parentheses')
        close_quotes_box = newcb(_("Automatic insertion of closing quotes"),
                             'close_quotes')
        add_colons_box = newcb(_("Automatic insertion of colons after 'for', "
                                                          "'if', 'def', etc"),
                               'add_colons')
        autounindent_box = newcb(_("Automatic indentation after 'else', "
                                   "'elif', etc."), 'auto_unindent')
        indent_chars_box = self.create_combobox(_("Indentation characters: "),
                                        ((_("4 spaces"), '*    *'),
                                         (_("2 spaces"), '*  *'),
                                         (_("tab"), '*\t*')), 'indent_chars')
        tabwidth_spin = self.create_spinbox(_("Tab stop width:"), _("pixels"),
                                            'tab_stop_width', 40, 10, 1000, 10)
        tab_mode_box = newcb(_("Tab always indent"),
                      'tab_always_indent', default=False,
                      tip=_("If enabled, pressing Tab will always indent,\n"
                            "even when the cursor is not at the beginning\n"
                            "of a line (when this option is enabled, code\n"
                            "completion may be triggered using the alternate\n"
                            "shortcut: Ctrl+Space)"))
        ibackspace_box = newcb(_("Intelligent backspace"),
                               'intelligent_backspace', default=True)
        removetrail_box = newcb(_("Automatically remove trailing spaces "
                                  "when saving files"),
                               'always_remove_trailing_spaces', default=False)
        
        analysis_group = QGroupBox(_("Analysis"))
        pep8_url = '<a href="http://www.python.org/dev/peps/pep-0008/">PEP8</a>'
        analysis_label = QLabel(_("<u>Note</u>: add <b>analysis:ignore</b> in "
                                  "a comment to ignore code/style analysis "
                                  "warnings. For more informations on style "
                                  "guide for Python code, please refer to the "
                                  "%s page.") % pep8_url)
        analysis_label.setWordWrap(True)
        is_pyflakes = codeanalysis.is_pyflakes_installed()
        is_pep8 = codeanalysis.get_checker_executable('pep8') is not None
        analysis_label.setEnabled(is_pyflakes or is_pep8)
        pyflakes_box = newcb(_("Code analysis")+" (pyflakes)",
                      'code_analysis/pyflakes', default=True,
                      tip=_("If enabled, Python source code will be analyzed\n"
                            "using pyflakes, lines containing errors or \n"
                            "warnings will be highlighted"))
        pyflakes_box.setEnabled(is_pyflakes)
        if not is_pyflakes:
            pyflakes_box.setToolTip(_("Code analysis requires pyflakes %s+") %
                                    codeanalysis.PYFLAKES_REQVER)
        pep8_box = newcb(_("Style analysis")+' (pep8)',
                      'code_analysis/pep8', default=False,
                      tip=_('If enabled, Python source code will be analyzed\n'
                            'using pep8, lines that are not following PEP8\n'
                            'style guide will be highlighted'))
        pep8_box.setEnabled(is_pep8)
        ancb_layout = QHBoxLayout()
        ancb_layout.addWidget(pyflakes_box)
        ancb_layout.addWidget(pep8_box)
        todolist_box = newcb(_("Tasks (TODO, FIXME, XXX, HINT, TIP, @todo)"),
                             'todo_list', default=True)
        realtime_radio = self.create_radiobutton(
                                            _("Perform analysis when "
                                                    "saving file and every"),
                                            'realtime_analysis', True)
        saveonly_radio = self.create_radiobutton(
                                            _("Perform analysis only "
                                                    "when saving file"),
                                            'onsave_analysis')
        af_spin = self.create_spinbox("", " ms", 'realtime_analysis/timeout',
                                      min_=100, max_=1000000, step=100)
        af_layout = QHBoxLayout()
        af_layout.addWidget(realtime_radio)
        af_layout.addWidget(af_spin)
        
        run_layout = QVBoxLayout()
        run_layout.addWidget(saveall_box)
        run_group.setLayout(run_layout)
        
        run_selection_layout = QVBoxLayout()
        run_selection_layout.addWidget(focus_box)
        run_selection_group.setLayout(run_selection_layout)
        
        introspection_layout = QVBoxLayout()
        if rope_is_installed:
            introspection_layout.addWidget(calltips_box)
            introspection_layout.addWidget(completion_box)
            introspection_layout.addWidget(case_comp_box)
            introspection_layout.addWidget(comp_enter_box)
            introspection_layout.addWidget(gotodef_box)
        else:
            introspection_layout.addWidget(rope_label)
        introspection_group.setLayout(introspection_layout)
        
        analysis_layout = QVBoxLayout()
        analysis_layout.addWidget(analysis_label)
        analysis_layout.addLayout(ancb_layout)
        analysis_layout.addWidget(todolist_box)
        analysis_layout.addLayout(af_layout)
        analysis_layout.addWidget(saveonly_radio)
        analysis_group.setLayout(analysis_layout)
        
        sourcecode_layout = QVBoxLayout()
        sourcecode_layout.addWidget(closepar_box)
        sourcecode_layout.addWidget(autounindent_box)
        sourcecode_layout.addWidget(add_colons_box)
        sourcecode_layout.addWidget(close_quotes_box)
        sourcecode_layout.addWidget(indent_chars_box)
        sourcecode_layout.addWidget(tabwidth_spin)
        sourcecode_layout.addWidget(tab_mode_box)
        sourcecode_layout.addWidget(ibackspace_box)
        sourcecode_layout.addWidget(removetrail_box)
        sourcecode_group.setLayout(sourcecode_layout)

        eol_group = QGroupBox(_("End-of-line characters"))
        eol_label = QLabel(_("When opening a text file containing "
                             "mixed end-of-line characters (this may "
                             "raise syntax errors in the consoles "
                             "on Windows platforms), Spyder may fix the "
                             "file automatically."))
        eol_label.setWordWrap(True)
        check_eol_box = newcb(_("Fix automatically and show warning "
                                "message box"),
                              'check_eol_chars', default=True)

        eol_layout = QVBoxLayout()
        eol_layout.addWidget(eol_label)
        eol_layout.addWidget(check_eol_box)
        eol_group.setLayout(eol_layout)
        
        tabs = QTabWidget()
        tabs.addTab(self.create_tab(font_group, interface_group, display_group),
                    _("Display"))
        tabs.addTab(self.create_tab(introspection_group, analysis_group),
                    _("Code Introspection/Analysis"))
        tabs.addTab(self.create_tab(template_btn, run_group, run_selection_group,
                                    sourcecode_group, eol_group),
                    _("Advanced settings"))
        
        vlayout = QVBoxLayout()
        vlayout.addWidget(tabs)
        self.setLayout(vlayout)