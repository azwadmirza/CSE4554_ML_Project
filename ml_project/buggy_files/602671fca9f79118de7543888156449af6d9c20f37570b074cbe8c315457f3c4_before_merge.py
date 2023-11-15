def keyboard_detect():
    global internalid, usbid, chromeswap, system_type
    internal_kbname = ""
    usb_kbname = ""
    print()
    print("Looking for keyboards...")
    print()
    result = subprocess.check_output('xinput list | grep -iv "Virtual\|USB" | grep -i "keyboard.*keyboard" | grep -o -P "(?<=↳).*(?=id\=)";exit 0', shell=True).decode('utf-8')
    if result != "":
        internal_kbname = result.strip()
    internalid = subprocess.check_output('xinput list | grep -iv "Virtual\|USB" | grep -i "keyboard.*keyboard" | cut -d "=" -f 2- | awk \'{print $1}\' | tail -1;exit 0', shell=True).decode('utf-8')
    print("Internal Keyboard\nName: " + internal_kbname + "\nID: " + internalid)

    result = subprocess.check_output('udevadm info -e | grep -o -P "(?<=by-id/usb-).*(?=-event-kbd)" | head -1;exit 0', shell=True).decode('utf-8')
    if result != "":
        usb_kbname = result.strip()

    # Loop the following to ensure the id is picked up after 5-10 tries
    usbid = ""
    usbcount=0
    while usbid == "":
        usbid = subprocess.check_output('udevadm info -e | stdbuf -oL grep -o -P "(?<=event-kbd /dev/input/by-path/pci-0000:00:).*(?=.0-usb)";exit 0', shell=True).decode('utf-8')
        if usbid == "":
            usbcount += 1
            # print('usbid not found '+ str(usbcount))
            if usbcount == 5:
                usbid = "0"
        time.sleep(1)
    print("\nUSB Keyboard\n" + "Name: " + usb_kbname + "\nID: " + usbid)

    if system_type == "1":
        system_type = "windows"
    elif system_type == "2":
        system_type = "chromebook"
    elif system_type == "3":
        system_type = "mac"

    if system_type == "windows" or system_type == "mac":
        subprocess.check_output('/bin/bash -c ./mac_wordwise.sh', shell=True).decode('utf-8')
        cmdgui = '"/usr/bin/setxkbmap -option;xkbcomp -w0 -I$HOME/.xkb ~/.xkb/keymap/kbd.mac.onelvl $DISPLAY"'
        # subprocess.check_output('echo "1" > /sys/module/hid_apple/parameters/swap_opt_cmd', shell=True).decode('utf-8')
    elif system_type == "chromebook":
        subprocess.check_output('/bin/bash -c ./chromebook.sh', shell=True).decode('utf-8')
        cmdgui = '"setxkbmap -option;xkbcomp -w0 -I$HOME/.xkb ~/.xkb/keymap/kbd.chromebook.gui $DISPLAY"'

    # password = getpass("Please enter your password to complete the keyswap: ")
    # proc = Popen("echo '1' | sudo tee -a /sys/module/hid_apple/parameters/swap_opt_cmd".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # proc.communicate(password.encode())

    if swap_behavior == 1:
        print("Setting up " + system_type + " keyswap as a service.")
        print("You can disable and remove the service by using the following commands.")
        print("systemctl --user stop keyswap")
        print("systemctl --user disable keyswap")
        print("rm -rf ~/.config/autostart/keyswap.sh")
        print("rm -rf ~/.config/xactive.sh")
        keyswapcmd = '/bin/bash -c "./keyswap_service.sh 1 0 ' + system_type + ' ' + str(internalid).strip() + ' ' + str(usbid).strip() + ' ' + str(chromeswap) + '"'
        print(keyswapcmd)
        subprocess.check_output(keyswapcmd, shell=True).decode('utf-8')
    else:
        print("Setting up " + system_type + " keyswap inside your profiles ~/.Xsession file.")
        print("You can modify or remove the file if you want you want to remove the modification.")
        keyswapcmd = '/bin/bash -c "./keyswap_service.sh 0 ' + cmdgui + '"'
        subprocess.check_output(keyswapcmd, shell=True).decode('utf-8')

    print("Please run this command in the terminal if you are using a Windows or Macbook.")
    print("Your keymapping will not work right on Apple keyboards without it.")
    print("echo '1' | sudo tee -a /sys/module/hid_apple/parameters/swap_opt_cmd")