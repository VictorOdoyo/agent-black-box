from agent_black_box import AgentRecorder, TraceFileStore


def search_incidents():
    return {"matches": ["INC-421", "INC-422"]}


store = TraceFileStore("out/traces")

with AgentRecorder("example-triage-agent", metadata={"ticket": "INC-421"}) as recorder:
    recorder.observation("Webhook retries are failing", {"user_email": "operator@example.com"})
    recorder.decision("Investigate retry worker first", "The deploy only changed retry scheduling.")
    recorder.permission("search_incidents", True, "Read-only incident lookup")
    recorder.capture_tool(
        "search_incidents",
        {"query": "webhook retries", "authorization": "Bearer live-token"},
        search_incidents,
        requires_permission=True,
    )
    path = store.save(recorder.trace)
    print(path)
