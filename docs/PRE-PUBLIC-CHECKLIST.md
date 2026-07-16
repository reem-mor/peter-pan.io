# Pre-Public Checklist — PETER PAN

Gate for making this repository public. **Public push stays blocked until every item in
§4 is checked.** This file consolidates three separate work threads so nothing slips
before release.

Status legend: `[ ]` open · `[x]` done · `[~]` in progress

---

## 1. Skills / tooling cleanup (tooling-only, no product code)

- [x] Consolidate to single canonical root `.claude/skills/` (9 skills incl. `graphify`).
- [x] Domain guidance from former `.cursor/skills/` migrated into matching `.claude` skills
  (or into `docs/AGENT-TOOLING.md` for FastAPI / caveman ladder).
- [x] Each skill is `skills/<name>/SKILL.md` under `.claude/skills/`.
- [x] Delete `.cursor/skills/` (no mirror trees).
- [x] Do NOT restore `hw07-open-webui` or `local-models` (course residue).
- [x] `docs/AGENT-TOOLING.md`: inventory + canonical-root policy (no `.cursor/skills/` mirrors).
- [x] Cursor discovery: third-party skills compatibility documented in AGENT-TOOLING
  (enable **Include third-party Plugins, Skills, and other configs**).
- [x] `docs/AGENT_TOOLING_v2.md` already absent (nothing to delete).

Canonical skill set (9): `ec2-deploy`, `frontend-design`, `graphify`, `guardrails-testing`,
`incident-triage`, `mcp-integration`, `peter-evaluation`, `prompt-engineering-log`,
`rag-evaluation`.

---

## 2. Security / residue pass (surgical remediation — accepted)

- [x] Add `.claude/settings.local.json` to `.gitignore` (already present).
- [x] In `settings.local.json`: `provision_ec2.sh` / `deploy_ec2.sh` / SSH in `ask`;
  deny `Read(**/.ssh/**)` and `Read(**/*.pem)`; remove live EC2 IPs from allow/ask.
- [x] Delete stale `.env.production` — already absent.
- [x] Strip only `PITER_*` assignments from `.env` — none present (0 lines removed).
- [x] Verify: no `PITER_*` values printed; local `.env` not staged.
- [x] Do NOT commit, push, deploy, rotate, or rewrite history in this pass.

Deferred (Path-to-Production, NOT blocking public): EC2 loopback/port hardening in
`docker-compose.ec2.yml`; `N8N_BLOCK_ENV_ACCESS_IN_NODE` → `true` for the demo profile.

---

## 3. Kaggle finding — reclassified as FALSE POSITIVE

Commit `94193cb` `.cursor/mcp.json` was flagged as containing a "literal Kaggle
Authorization credential." **It does not.** The value is an env-var placeholder:
`"Authorization": "Bearer ${env:KAGGLE_API_TOKEN}"` — a reference, not a secret. No
literal token is stored in that commit.

Consequence: the history-purge of `94193cb` and the credential rotation tied to
`mcp.json` are **NOT required** — unless the checks below find a real literal token
committed elsewhere.

- [x] `git log --all --oneline -- "**/kaggle.json" "kaggle.json"` → empty.
- [x] No literal Kaggle token file in tree; `-S KAGGLE_API_TOKEN` hits are placeholder
  references only (FALSE POSITIVE path — cleared).
- [x] `kaggle.json` and `**/.kaggle/` already in `.gitignore`.
- [x] Kaggle thread CLEARED — no revoke/purge needed.

---

## 4. Public-release gate — ALL must be checked before `--public`

- [x] §1 skills cleanup complete and verified.
- [x] §2 security pass complete; `settings.local.json` ignored + untracked.
- [x] §3 Kaggle checks cleared (placeholder-only).
- [x] Confirm ignored + **untracked** (not merely ignored): `.env`, `.env.production` (absent), `.cursor/mcp.json`, `.claude/settings.local.json`.
- [x] No tracked `PITER_*` assignments in source (checklist mentions only).
- [x] README / CLAUDE / AGENTS canonical doc links all resolve (SPEC-CROSSWALK → PETER-PAN-SPEC-CROSSWALK; skill paths updated).
- [ ] Final `git log --all` sweep shows no secrets in history (operator gate before `--public`).

Only when every box in §4 is checked is the repository clean to publish.

---

## Appendix — history purge (ONLY if §3 finds a real literal token)

Not needed for the placeholder. Kept here so the procedure is on record if a genuine
literal is ever found. Run on a backup; requires a force-push (blocked by the deny-floor
by default — done consciously here).

```powershell
cd ..; git clone c:\dev\peter-pan.io peter-pan-backup   # back up first
cd c:\dev\peter-pan.io
pip install git-filter-repo
git filter-repo --path <file-with-secret> --invert-paths --force
# or redact a literal string:
#   echo "OLD_TOKEN==>REDACTED" > replacements.txt
#   git filter-repo --replace-text replacements.txt --force ; del replacements.txt
git remote add origin https://github.com/reem-mor/peter-pan.io.git
git push origin --force --all ; git push origin --force --tags
git log --all -S "<token_fragment>" --oneline   # expect empty
```
Revoke-before-purge: expire the credential first, so any cached copy is already dead.
