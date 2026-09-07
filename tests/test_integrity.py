from agent_black_box import AgentRecorder, chain_hash, trace_manifest, verify_event_fingerprints, verify_manifest


def test_manifest_verifies_clean_trace():
    with AgentRecorder("demo") as recorder:
        recorder.observation("input")
    manifest = trace_manifest(recorder.trace)
    assert chain_hash(recorder.trace) == manifest["chain_hash"]
    assert verify_manifest(recorder.trace, manifest) == []


def test_fingerprint_mismatch_is_reported():
    with AgentRecorder("demo") as recorder:
        event = recorder.observation("input")
    event.summary = "tampered"
    findings = verify_event_fingerprints(recorder.trace)
    assert findings[0].code == "fingerprint_mismatch"
