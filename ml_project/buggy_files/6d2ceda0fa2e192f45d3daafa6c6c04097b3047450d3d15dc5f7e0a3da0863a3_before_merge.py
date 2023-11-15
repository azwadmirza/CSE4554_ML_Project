def api_analysis(package, location):
    """API Analysis"""
    api_analysis_result = {}
    logger.info("Dynamic API Analysis")
    dat = ""
    api_base64 = []
    api_fileio = []
    api_reflect = []
    api_sysprop = []
    api_cntvl = []
    api_binder = []
    api_crypto = []
    api_acntmnger = []
    api_deviceinfo = []
    api_net = []
    api_dexloader = []
    api_cmd = []
    api_sms = []
    try:
        with open(location, "r", encoding="utf-8") as flip:
            dat = flip.readlines()
        res_id = "Droidmon-apimonitor-" + package + ":"
        for line in dat:
            if res_id in line:
                # print "LINE: " + line
                _, value = line.split(res_id, 1)
                # print "PARAM is :" + param
                # print "Value is :"+ value
                try:
                    apis = json.loads(value, strict=False)
                    ret = ''
                    args = ''
                    mtd = str(apis["method"])
                    clss = str(apis["class"])
                    # print "Called Class: " + CLS
                    # print "Called Method: " + MTD
                    if apis.get('return'):
                        ret = str(apis["return"])
                        # print "Return Data: " + RET
                    else:
                        # print "No Return Data"
                        ret = "No Return Data"
                    if apis.get('args'):
                        args = str(apis["args"])
                        # print "Passed Arguments" + ARGS
                    else:
                        # print "No Arguments Passed"
                        args = "No Arguments Passed"
                    # XSS Safe
                    call_data = "</br>METHOD: " + \
                        escape(mtd) + "</br>ARGUMENTS: " + escape(args) + \
                        "</br>RETURN DATA: " + escape(ret)

                    if re.findall("android.util.Base64", clss):
                        # Base64 Decode
                        if "decode" in mtd:
                            args_list = python_list(args)
                            if isBase64(args_list[0]):
                                call_data += '</br><span class="label label-info">' +\
                                    'Decoded String:</span> ' + \
                                    escape(base64.b64decode(args_list[0]))
                        api_base64.append(call_data)
                    if re.findall('libcore.io|android.app.SharedPreferencesImpl\$EditorImpl', clss):
                        api_fileio.append(call_data)
                    if re.findall('java.lang.reflect', clss):
                        api_reflect.append(call_data)
                    if re.findall('android.content.ContentResolver|android.location.Location|android.media.AudioRecord|android.media.MediaRecorder|android.os.SystemProperties', clss):
                        api_sysprop.append(call_data)
                    if re.findall('android.app.Activity|android.app.ContextImpl|android.app.ActivityThread', clss):
                        api_binder.append(call_data)
                    if re.findall('javax.crypto.spec.SecretKeySpec|javax.crypto.Cipher|javax.crypto.Mac', clss):
                        api_crypto.append(call_data)
                    if re.findall('android.accounts.AccountManager|android.app.ApplicationPackageManager|android.app.NotificationManager|android.net.ConnectivityManager|android.content.BroadcastReceiver', clss):
                        api_acntmnger.append(call_data)
                    if re.findall('android.telephony.TelephonyManager|android.net.wifi.WifiInfo|android.os.Debug', clss):
                        api_deviceinfo.append(call_data)
                    if re.findall('dalvik.system.BaseDexClassLoader|dalvik.system.DexFile|dalvik.system.DexClassLoader|dalvik.system.PathClassLoader', clss):
                        api_dexloader.append(call_data)
                    if re.findall('java.lang.Runtime|java.lang.ProcessBuilder|java.io.FileOutputStream|java.io.FileInputStream|android.os.Process', clss):
                        api_cmd.append(call_data)
                    if re.findall('android.content.ContentValues', clss):
                        api_cntvl.append(call_data)
                    if re.findall('android.telephony.SmsManager', clss):
                        api_sms.append(call_data)
                    if re.findall('java.net.URL|org.apache.http.impl.client.AbstractHttpClient', clss):
                        api_net.append(call_data)
                except:
                    PrintException("[ERROR] Parsing JSON Failed for: " + value)
    except:
        PrintException("[ERROR] Dynamic API Analysis")
    api_analysis_result["api_net"] = list(set(api_net))
    api_analysis_result["api_base64"] = list(set(api_base64))
    api_analysis_result["api_fileio"] = list(set(api_fileio))
    api_analysis_result["api_binder"] = list(set(api_binder))
    api_analysis_result["api_crypto"] = list(set(api_crypto))
    api_analysis_result["api_deviceinfo"] = list(set(api_deviceinfo))
    api_analysis_result["api_cntvl"] = list(set(api_cntvl))
    api_analysis_result["api_sms"] = list(set(api_sms))
    api_analysis_result["api_sysprop"] = list(set(api_sysprop))
    api_analysis_result["api_dexloader"] = list(set(api_dexloader))
    api_analysis_result["api_reflect"] = list(set(api_reflect))
    api_analysis_result["api_acntmnger"] = list(set(api_acntmnger))
    api_analysis_result["api_cmd"] = list(set(api_cmd))
    return api_analysis_result