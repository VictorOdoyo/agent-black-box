from agent_black_box import ReplaySession, TraceFileStore


trace = TraceFileStore("fixtures/traces").load("incident_triage.json")
replay = ReplaySession(trace)
search_incidents = replay.mock("search_incidents")

print(search_incidents({"query": "ignored during replay"}))
