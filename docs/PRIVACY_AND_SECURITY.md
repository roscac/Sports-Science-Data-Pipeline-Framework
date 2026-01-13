# Privacy and Security Model

This project is designed to demonstrate **real-world athlete data governance**.

## Core principles
1. Raw data never leaves the local machine
2. Identity keys never enter version control
3. ML models never access athlete names
4. Re-identification is deliberate and auditable

## Local-only directories
These folders are blocked from Git and exports:
- `data/raw/`
- `data/identity_key/`
- `data/upload/`
- `logs/`

## Export behavior
Exported projects replicate structure but exclude all sensitive contents. The GUI exposes Export Project in Advanced Mode.

## Public demo context
This repository contains **no real athlete data** and is safe for public viewing.

## Deterministic pseudonyms (HMAC)
- Athlete identifiers are converted to stable pseudonyms using an HMAC key stored in `data/identity_key/hmac_key.txt`
- The lookup key in `data/identity_key/identity_key.csv` maps `anon_id` back to source identifiers when needed
- The HMAC key and identity key never go to Git, and should stay local-only

## Key rotation (optional)
- Create a new HMAC key by deleting `data/identity_key/hmac_key.txt`
- Re-run anonymization to generate new pseudonyms and a new identity key
- Keep old keys if you need to reconcile historical exports
