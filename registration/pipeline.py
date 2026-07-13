import sys
from . import config
from .auth       import get_token
from .doctors    import find_provider
from .inbox      import get_unmatched_referrals, get_admin_doc_detail
from .ocr        import ocr_referral_pages
from .extractor  import extract_structured_data
from .patient    import find_existing_patient, register_patient
from .insurance  import post_insurance
from .referral   import attach_referral_to_patient, close_inbox_document
from .logger     import setup_logger, log_referral_result


def run():
    # ── 1. Setup ──────────────────────────────────────────────
    logger = setup_logger()
    logger.info("Pipeline started")

    token   = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    logger.info("AthenaHealth token obtained")

    provider = find_provider(
        headers,
        name=config.TARGET_DOCTOR_NAME,
        provider_id=config.TARGET_PROVIDER_ID,
    )
    if not provider:
        logger.error(f"Doctor not found: name='{config.TARGET_DOCTOR_NAME}' id={config.TARGET_PROVIDER_ID}")
        sys.exit(1)

    full_name       = f"Dr. {provider.get('firstname', '')} {provider.get('lastname', '')}".strip()
    scheduling_name = provider.get("schedulingname", "")

    logger.info(f"Target doctor: {full_name} | schedulingname={scheduling_name} | providerid={provider['providerid']}")
    print(f"\n  Doctor : {full_name}")
    print(f"  ID     : {provider['providerid']}")
    print(f"  Queue  : {scheduling_name}\n")

    # ── 2. Inbox ──────────────────────────────────────────────
    unmatched = get_unmatched_referrals(headers, scheduling_name)
    total     = len(unmatched)

    logger.info(f"Unmatched referrals found: {total}")
    print(f"  Unmatched referrals in inbox: {total}")

    if total == 0:
        print("  Nothing to process. Exiting.\n")
        logger.info("Pipeline finished — no referrals to process")
        return

    print(f"  Processing {total} referral(s)...\n")
    print("=" * 65)

    # ── 3. Process each referral ──────────────────────────────
    registered = 0
    skipped    = 0
    failed     = 0

    for doc in unmatched:
        admin_id = doc["adminid"]
        print(f"\n  [adminid={admin_id}]")

        try:
            # 3a — Get full doc detail (includes pages array)
            detail = get_admin_doc_detail(headers, admin_id)
            pages  = detail.get("pages", [])
            print(f"    Pages found : {len(pages)}")

            if not pages:
                raise Exception("No pages found on this document — cannot OCR")

            # 3b — OCR all pages
            print(f"    OCR         : running...")
            ocr_text = ocr_referral_pages(headers, pages)
            if not ocr_text.strip():
                raise Exception("OCR returned empty text")
            print(f"    OCR         : {len(ocr_text)} chars extracted")

            # 3c — Extract structured data
            print(f"    Extracting  : patient / insurance / provider fields...")
            extraction = extract_structured_data(ocr_text)
            p = extraction.patient
            print(f"    Patient     : {p.firstname} {p.lastname} | DOB: {p.dob} | Sex: {p.sex}")

            # 3d — Check for existing patient
            patient_id = find_existing_patient(headers, p.firstname, p.lastname, p.dob)

            if patient_id:
                # 3e — Already registered — skip registration, still close inbox doc
                print(f"    Patient     : already exists (patientid={patient_id}) — skipping registration")
                close_inbox_document(headers, admin_id)
                log_referral_result(logger, admin_id, "SKIPPED_EXISTING", patient_id)
                skipped += 1
                continue

            # 3f — Register new patient
            print(f"    Registering : new patient...")
            patient_id = register_patient(headers, extraction)
            print(f"    Registered  : patientid={patient_id}")

            # 3g — Post insurance (best-effort)
            print(f"    Insurance   : {extraction.insurance.payer or 'not found'}")
            post_insurance(headers, patient_id, extraction.insurance)

            # 3h — Attach referral pages to patient chart
            print(f"    Attaching   : referral to patient chart...")
            new_admin_id = attach_referral_to_patient(headers, patient_id, pages)
            print(f"    Attached    : new adminid={new_admin_id}")

            # 3i — Close the original unmatched inbox document
            closed = close_inbox_document(headers, admin_id)
            print(f"    Inbox doc   : {'closed' if closed else 'close FAILED'}")

            # 3j — Log success
            log_referral_result(
                logger, admin_id, "REGISTERED", patient_id,
                f"insurance={extraction.insurance.payer or 'N/A'} | new_adminid={new_admin_id}"
            )
            registered += 1

        except Exception as e:
            print(f"    FAILED      : {e}")
            log_referral_result(logger, admin_id, "FAILED", detail=str(e))
            failed += 1
            continue

    # ── 4. Summary ────────────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"  Pipeline complete for {full_name}")
    print(f"  Total     : {total}")
    print(f"  Registered: {registered}")
    print(f"  Skipped   : {skipped}  (patient already existed)")
    print(f"  Failed    : {failed}")
    print("=" * 65 + "\n")

    logger.info(
        f"Pipeline complete | total={total} registered={registered} "
        f"skipped={skipped} failed={failed}"
    )


if __name__ == "__main__":
    run()
