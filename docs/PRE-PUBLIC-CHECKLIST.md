# Pre-Public Checklist — PETER PAN

Gate for making this repository public. **Public push stays blocked until every item in
§4 is checked.** This file consolidates three separate work threads so nothing slips
before release.

Status legend: `[ ]` open · `[x]` done · `[~]` in progress

---

## 1. Skills / tooling cleanup (tooling-only, no product code)

- [ ] Consolidate to single canonical root `.claude/skills/` (8 skills).
- [ ] Move `ec2-deploy` and `peter-evaluation` out of `.cursor/skills/`.
- [ ] Rename each entrypoint to per-folder `skills/<name>/SKILL.md` (verify 8 distinct folders, not colliding files).
- [ ] Delete `.cursor/skills/`, remaining generic skills, and the `.agents\skills` backslash folder.
- [ ] Do NOT restore `hw07-open-webui` or `local-models` (course residue).
- [ ] `docs/AGENT-TOOLING.md`: record the 8-skill inventory + canonical-root policy.
- [ ] **Verify (don't assume)** whether Cursor actually discovers `.claude/skills/`; document accurately, not as unconfirmed "official compatibility".
- [ ] Show contents of `docs/AGENT_TOOLING_v2.md` before deleting; confirm only the EC2 row was worth keeping.

Final skill set (exactly 8): `ec2-deploy`, `frontend-design`, `guardrails-testing`,
`incident-triage`, `mcp-integration`, `peter-evaluation`, `prompt-engineering-log`, `rag-evaluation`.

---

## 2. Security / residue pass (surgical remediation — accepted)

- [ ] Add `.claude/settings.local.json` to `.gitignore` (contains live EC2 IP + SSH/deploy commands).
- [ ] In `settings.local.json`: move `provision_ec2.sh`, `deploy_ec2.sh`, and SSH-to-EC2 from `allow` → `ask`; remove broad `Read(.../.ssh/**)` grant.
- [ ] Delete stale `.env.production` (PITER-era, contains a populated Flask secret + Bedrock IDs).
- [ ] Strip only `PITER_*` assignments from `.env`; preserve all `PETER_*` / `N8N_*` / `AWS_*`; never print values. (Collapse duplicate `AWS_REGION` only if identical.)
- [ ] Verify diff shows ONLY `PITER_*` lines removed — nothing else touched.
- [ ] Do NOT commit, push, deploy, rotate, or rewrite history in this pass.

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

- [ ] `git log --all --oneline -- "**/kaggle.json" "kaggle.json"` → expect empty.
- [ ] `git log --all -p -S "<real_token_fragment>" --oneline` → expect empty.
- [ ] Add `kaggle.json` and `**/.kaggle/` to `.gitignore` (prevent future commits).
- [ ] If BOTH checks are empty → Kaggle thread CLEARED, no revoke/purge needed.
- [ ] If EITHER returns a commit → real exposure: revoke the Kaggle token (kaggle.com → Settings → API → Expire Token) and run the history purge below for that literal.

---

## 4. Public-release gate — ALL must be checked before `--public`

- [ ] §1 skills cleanup complete and verified.
- [ ] §2 security pass complete; diff clean; `settings.local.json` ignored + untracked.
- [ ] §3 both `git log` checks returned empty (or the real-exposure path was fully remediated).
- [ ] Confirm ignored + **untracked** (not merely ignored): `.env`, `.env.production` (deleted), `.cursor/mcp.json`, `.claude/settings.local.json`.
- [ ] No tracked `PITER_*` references anywhere in source.
- [ ] README / CLAUDE / AGENTS canonical doc links all resolve (no dead links).
- [ ] Final `git log --all` sweep shows no secrets in history.

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
