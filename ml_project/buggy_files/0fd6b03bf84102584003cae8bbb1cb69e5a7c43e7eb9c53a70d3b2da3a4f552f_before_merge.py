    def __init__(self, app):
        """
        Create initial default configuration
        """ 
        self.VERSION = self.__class__.CLASS_VERSION
        self.lock = threading.Lock()
        
        self.app = app
        self.folders = []
        self.userCodeDir = None  # type: str
        
        self.configHotkey = GlobalHotkey()
        self.configHotkey.set_hotkey(["<super>"], "k")
        self.configHotkey.enabled = True
        
        self.toggleServiceHotkey = GlobalHotkey()
        self.toggleServiceHotkey.set_hotkey(["<super>", "<shift>"], "k")
        self.toggleServiceHotkey.enabled = True    
        
        app.init_global_hotkeys(self)        
        
        self.load_global_config()
                
        self.app.monitor.add_watch(CONFIG_DEFAULT_FOLDER)
        self.app.monitor.add_watch(common.CONFIG_DIR)
        
        if self.folders:
            return
    
        # --- Code below here only executed if no persisted config data provided
        
        _logger.info("No configuration found - creating new one")       
        
        myPhrases = model.Folder("My Phrases")
        myPhrases.set_hotkey(["<ctrl>"], "<f7>")
        myPhrases.set_modes([model.TriggerMode.HOTKEY])
        myPhrases.persist()

        f = model.Folder("Addresses")
        adr = model.Phrase("Home Address", "22 Avenue Street\nBrisbane\nQLD\n4000")
        adr.set_modes([model.TriggerMode.ABBREVIATION])
        adr.add_abbreviation("adr")
        f.add_item(adr)
        myPhrases.add_folder(f)        
        f.persist()
        adr.persist()

        p = model.Phrase("First phrase", "Test phrase number one!")
        p.set_modes([model.TriggerMode.PREDICTIVE])
        p.set_window_titles(".* - gedit")
        myPhrases.add_item(p)
        
        myPhrases.add_item(model.Phrase("Second phrase", "Test phrase number two!"))
        myPhrases.add_item(model.Phrase("Third phrase", "Test phrase number three!"))
        self.folders.append(myPhrases)
        [p.persist() for p in myPhrases.items]
        
        sampleScripts = model.Folder("Sample Scripts")
        sampleScripts.persist()
        dte = model.Script("Insert Date", "")
        dte.code = """output = system.exec_command("date")
keyboard.send_keys(output)"""
        sampleScripts.add_item(dte)
        
        lMenu = model.Script("List Menu", "")
        lMenu.code = """choices = ["something", "something else", "a third thing"]

retCode, choice = dialog.list_menu(choices)
if retCode == 0:
    keyboard.send_keys("You chose " + choice)"""
        sampleScripts.add_item(lMenu)
        
        sel = model.Script("Selection Test", "")
        sel.code = """text = clipboard.get_selection()
keyboard.send_key("<delete>")
keyboard.send_keys("The text %s was here previously" % text)"""
        sampleScripts.add_item(sel)
        
        abbrc = model.Script("Abbreviation from selection", "")
        abbrc.code = """import time
time.sleep(0.25)
contents = clipboard.get_selection()
retCode, abbr = dialog.input_dialog("New Abbreviation", "Choose an abbreviation for the new phrase")
if retCode == 0:
    if len(contents) > 20:
        title = contents[0:17] + "..."
    else:
        title = contents
    folder = engine.get_folder("My Phrases")
    engine.create_abbreviation(folder, title, abbr, contents)"""
        sampleScripts.add_item(abbrc)
        
        phrasec = model.Script("Phrase from selection", "")
        phrasec.code = """import time
time.sleep(0.25)
contents = clipboard.get_selection()
if len(contents) > 20:
    title = contents[0:17] + "..."
else:
    title = contents
folder = engine.get_folder("My Phrases")
engine.create_phrase(folder, title, contents)"""
        sampleScripts.add_item(phrasec)
        
        win = model.Script("Display window info", "")
        win.code = """# Displays the information of the next window to be left-clicked
import time
mouse.wait_for_click(1)
time.sleep(0.2)
winTitle = window.get_active_title()
winClass = window.get_active_class()
dialog.info_dialog("Window information", 
          "Active window information:\\nTitle: '%s'\\nClass: '%s'" % (winTitle, winClass))"""
        win.show_in_tray_menu = True
        sampleScripts.add_item(win)
        
        self.folders.append(sampleScripts)
        [s.persist() for s in sampleScripts.items]

        # TODO - future functionality
        self.recentEntries = []
        
        self.config_altered(True)