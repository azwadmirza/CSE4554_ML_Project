def extract_facility_statistics(facility):

    dataset_id = facility.dataset_id

    settings = {name: getattr(facility.dataset, name) for name in facility_settings if hasattr(facility.dataset, name)}

    learners = FacilityUser.objects.filter(dataset_id=dataset_id).exclude(roles__kind__in=[role_kinds.ADMIN, role_kinds.COACH])
    coaches = FacilityUser.objects.filter(dataset_id=dataset_id, roles__kind__in=[role_kinds.ADMIN, role_kinds.COACH])

    usersessions = UserSessionLog.objects.filter(dataset_id=dataset_id)
    contsessions = ContentSessionLog.objects.filter(dataset_id=dataset_id, time_spent__lt=3600 * 2)

    # the aggregates below are used to calculate the first and most recent times this device was used
    usersess_agg = (usersessions
                    .filter(start_timestamp__gt=datetime.datetime(2016, 1, 1))
                    .aggregate(first=Min("start_timestamp"), last=Max("last_interaction_timestamp")))
    contsess_agg = (contsessions
                    .filter(start_timestamp__gt=datetime.datetime(2016, 1, 1))
                    .aggregate(first=Min("start_timestamp"), last=Max("end_timestamp")))

    # since newly provisioned devices won't have logs, we don't know whether we have an available datetime object
    first_interaction_timestamp = getattr(min(usersess_agg["first"], contsess_agg["first"]), 'strftime', None)
    last_interaction_timestamp = getattr(max(usersess_agg["last"], contsess_agg["last"]), 'strftime', None)

    sesslogs_by_kind = contsessions.order_by("kind").values("kind").annotate(count=Count("kind"))
    sesslogs_by_kind = {log["kind"]: log["count"] for log in sesslogs_by_kind}

    summarylogs = ContentSummaryLog.objects.filter(dataset_id=dataset_id)

    contsessions_user = contsessions.exclude(user=None)
    contsessions_anon = contsessions.filter(user=None)

    return {
        # facility_id
        "fi": base64.encodestring(hashlib.md5(facility.id.encode()).digest())[:10].decode(),
        # settings
        "s": settings,
        # learners_count
        "lc": learners.count(),
        # learner_login_count
        "llc": usersessions.exclude(user__roles__kind__in=[role_kinds.ADMIN, role_kinds.COACH]).distinct().count(),
        # coaches_count
        "cc": coaches.count(),
        # coach_login_count
        "clc": usersessions.filter(user__roles__kind__in=[role_kinds.ADMIN, role_kinds.COACH]).distinct().count(),
        # first
        "f" : first_interaction_timestamp("%Y-%m-%d") if first_interaction_timestamp else None,
        # last
        "l": last_interaction_timestamp("%Y-%m-%d") if last_interaction_timestamp else None,
        # summ_started
        "ss": summarylogs.count(),
        # summ_complete
        "sc": summarylogs.exclude(completion_timestamp=None).count(),
        # sess_kinds
        "sk": sesslogs_by_kind,
        # lesson_count
        "lec": Lesson.objects.filter(dataset_id=dataset_id).count(),
        # exam_count
        "ec": Exam.objects.filter(dataset_id=dataset_id).count(),
        # exam_log_count
        "elc": ExamLog.objects.filter(dataset_id=dataset_id).count(),
        # att_log_count
        "alc": AttemptLog.objects.filter(dataset_id=dataset_id).count(),
        # exam_att_log_count
        "ealc": ExamAttemptLog.objects.filter(dataset_id=dataset_id).count(),
        # sess_user_count
        "suc": contsessions_user.count(),
        # sess_anon_count
        "sac": contsessions_anon.count(),
        # sess_user_time
        "sut": int((contsessions_user.aggregate(total_time=Sum("time_spent"))["total_time"] or 0) / 60),
        # sess_anon_time
        "sat": int((contsessions_anon.aggregate(total_time=Sum("time_spent"))["total_time"] or 0) / 60),
    }