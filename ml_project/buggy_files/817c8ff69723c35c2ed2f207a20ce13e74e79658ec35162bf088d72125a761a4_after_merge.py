def get_image_vulnerabilities(user_id, image_id, force_refresh=False, vendor_only=True):
    """
    Return the vulnerability listing for the specified image and load from catalog if not found and specifically asked
    to do so.


    Example json output:
    {
       "multi" : {
          "url_column_index" : 7,
          "result" : {
             "rows" : [],
             "rowcount" : 0,
             "colcount" : 8,
             "header" : [
                "CVE_ID",
                "Severity",
                "*Total_Affected",
                "Vulnerable_Package",
                "Fix_Available",
                "Fix_Images",
                "Rebuild_Images",
                "URL"
             ]
          },
          "querycommand" : "/usr/lib/python2.7/site-packages/anchore/anchore-modules/multi-queries/cve-scan.py /ebs_data/anchore/querytmp/queryimages.7026386 /ebs_data/anchore/data /ebs_data/anchore/querytmp/query.59057288 all",
          "queryparams" : "all",
          "warns" : [
             "0005b136f0fb (prom/prometheus:master) cannot perform CVE scan: no CVE data is currently available for the detected base distro type (busybox:unknown_version,busybox:v1.26.2)"
          ]
       }
    }

    :param user_id: user id of image to evaluate
    :param image_id: image id to evaluate
    :param force_refresh: if true, flush and recompute vulnerabilities rather than returning current values
    :param vendor_only: if true, filter out the vulnerabilities that vendors will explicitly not address
    :return:
    """

    # Has image?
    db = get_session()
    try:
        img = db.query(Image).get((image_id, user_id))
        vulns = []
        if not img:
            abort(404)
        else:
            if force_refresh:
                log.info('Forcing refresh of vulnerabiltiies for {}/{}'.format(user_id, image_id))
                try:
                    vulns = rescan_image(img, db_session=db)
                    db.commit()
                except Exception as e:
                    log.exception('Error refreshing cve matches for image {}/{}'.format(user_id, image_id))
                    db.rollback()
                    return make_response_error('Error refreshing vulnerability listing for image.', in_httpcode=500)

                db = get_session()
                db.refresh(img)
            
            vulns = img.vulnerabilities()

        # Has vulnerabilities?
        warns = []
        if not vulns:
            vulns = []
            ns = DistroNamespace.for_obj(img)
            if not have_vulnerabilities_for(ns):
                warns = ['No vulnerability data available for image distro: {}'.format(ns.namespace_name)]


        rows = []
        for vuln in vulns:
            # Skip the vulnerability if the vendor_only flag is set to True and the issue won't be addressed by the vendor
            if vendor_only and vuln.fix_has_no_advisory():
                continue

            cves = ''
            if vuln.vulnerability.additional_metadata:
                cves = ' '.join(vuln.vulnerability.additional_metadata.get('cves', []))

            rows.append([
                vuln.vulnerability_id,
                vuln.vulnerability.severity,
                1,
                vuln.pkg_name + '-' + vuln.package.fullversion,
                str(vuln.fixed_in()),
                vuln.pkg_image_id,
                'None', # Always empty this for now
                vuln.vulnerability.link,
                vuln.pkg_type,
                'vulnerabilities',
                vuln.vulnerability.namespace_name,
                vuln.pkg_name,
                vuln.package.fullversion,
                cves,
                ]
            )

        vuln_listing = {
            'multi': {
                'url_column_index': 7,
                'result': {
                    'header': TABLE_STYLE_HEADER_LIST,
                    'rowcount': len(rows),
                    'colcount': len(TABLE_STYLE_HEADER_LIST),
                    'rows': rows
                },
                'warns': warns
            }
        }

        cpe_vuln_listing = []
        try:
            all_cpe_matches = img.cpe_vulnerabilities()
            if not all_cpe_matches:
                all_cpe_matches = []

            cpe_hashes = {}
            for image_cpe, vulnerability_cpe in all_cpe_matches:
                cpe_vuln_el = {
                    'vulnerability_id': vulnerability_cpe.vulnerability_id,
                    'severity': vulnerability_cpe.severity,
                    'link': vulnerability_cpe.link,
                    'pkg_type': image_cpe.pkg_type,
                    'pkg_path': image_cpe.pkg_path,
                    'name': image_cpe.name,
                    'version': image_cpe.version,
                    'cpe': image_cpe.get_cpestring(),
                    'feed_name': vulnerability_cpe.feed_name,
                    'feed_namespace': vulnerability_cpe.namespace_name,
                }
                cpe_hash = hashlib.sha256(utils.ensure_bytes(json.dumps(cpe_vuln_el))).hexdigest()
                if not cpe_hashes.get(cpe_hash, False):
                    cpe_vuln_listing.append(cpe_vuln_el)
                    cpe_hashes[cpe_hash] = True
        except Exception as err:
            log.warn("could not fetch CPE matches - exception: " + str(err))

        report = LegacyVulnerabilityReport.from_dict(vuln_listing)
        resp = ImageVulnerabilityListing(user_id=user_id, image_id=image_id, legacy_report=report, cpe_report=cpe_vuln_listing)

        return resp.to_dict()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        log.exception('Error checking image {}, {} for vulnerabiltiies. Rolling back'.format(user_id, image_id))
        db.rollback()
        abort(500)
    finally:
        db.close()