# Teamworks Ingestion (Demonstration)

This project includes a **stubbed Teamworks ingestion flow** for demonstration purposes.

## Current behavior
- Uploads run in dry-run mode by default
- No real endpoints or credentials are included
- GUI Advanced Mode can optionally auto-delete ML outputs after re-identify

## Where to extend
Implement final ingestion logic in:
```text
scripts/helpers/teamworks_api.py
```

When adapting for real environments:
- Confirm authentication method
- Confirm required schema
- Add retry and error handling

## Important
This repository does not perform live uploads.
