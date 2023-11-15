def manual_download_subtitle(path, language, hi, subtitle, provider, providers_auth, sceneName, media_type):
    if hi == "True":
        hi = True
    else:
        hi = False
    subtitle = pickle.loads(codecs.decode(subtitle.encode(), "base64"))
    if media_type == 'series':
        type_of_score = 360
    elif media_type == 'movie':
        type_of_score = 120
    use_scenename = get_general_settings()[9]
    use_postprocessing = get_general_settings()[10]
    postprocessing_cmd = get_general_settings()[11]

    if language == 'pb':
        language = alpha3_from_alpha2(language)
        lang_obj = Language('por', 'BR')
    else:
        language = alpha3_from_alpha2(language)
        lang_obj = Language(language)

    try:
        if sceneName is None or use_scenename is False:
            used_sceneName = False
            video = scan_video(path)
        else:
            used_sceneName = True
            video = Video.fromname(sceneName)
    except Exception as e:
        logging.exception('Error trying to extract information from this filename: ' + path)
        return None
    else:
        try:
            best_subtitle = subtitle
            download_subtitles([best_subtitle], providers=provider, provider_configs=providers_auth)
        except Exception as e:
            logging.exception('Error downloading subtitles for ' + path)
            return None
        else:
            single = get_general_settings()[7]
            try:
                score = round(float(compute_score(best_subtitle, video, hearing_impaired=hi)) / type_of_score * 100, 2)
                if used_sceneName == True:
                    video = scan_video(path)
                if single is True:
                    result = save_subtitles(video, [best_subtitle], single=True, encoding='utf-8')
                else:
                    result = save_subtitles(video, [best_subtitle], encoding='utf-8')
            except Exception as e:
                logging.exception('Error saving subtitles file to disk.')
                return None
            else:
                downloaded_provider = str(result[0]).strip('<>').split(' ')[0][:-8]
                downloaded_language = language_from_alpha3(language)
                downloaded_language_code2 = alpha2_from_alpha3(language)
                downloaded_language_code3 = language
                downloaded_path = get_subtitle_path(path, language=lang_obj)
                message = downloaded_language + " subtitles downloaded from " + downloaded_provider + " with a score of " + unicode(score) + "% using manual search."

                if use_postprocessing is True:
                    command = pp_replace(postprocessing_cmd, path, downloaded_path, downloaded_language, downloaded_language_code2, downloaded_language_code3)
                    try:
                        if os.name == 'nt':
                            codepage = subprocess.Popen("chcp", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            # wait for the process to terminate
                            out_codepage, err_codepage = codepage.communicate()
                            encoding = out_codepage.split(':')[-1].strip()

                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        # wait for the process to terminate
                        out, err = process.communicate()

                        if os.name == 'nt':
                            out = out.decode(encoding)

                    except:
                        if out == "":
                            logging.error('Post-processing result for file ' + path + ' : Nothing returned from command execution')
                        else:
                            logging.error('Post-processing result for file ' + path + ' : ' + out)
                    else:
                        if out == "":
                            logging.info('Post-processing result for file ' + path + ' : Nothing returned from command execution')
                        else:
                            logging.info('Post-processing result for file ' + path + ' : ' + out)

                return message