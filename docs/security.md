# Security Model

Agent Black Box is designed for local, inspectable traces. It does not require a cloud account or live service.

Security boundaries:

- Redaction happens before payloads are appended
- The CLI works on local files
- Demo fixtures do not contain real credentials
- Policy checks flag unredacted tokens
- Replay returns captured responses rather than invoking live tools
