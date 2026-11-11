# Source File Discovery — 2026-11-11 (updated after full-branch search)

## Result

| File | Status | Location |
|---|---|---|
| `OpenMontage_10of10_Four_Factories_OpenCode_Agent_Task_2026-11-11.md` | **FOUND** | `origin/main` @ `2f8f1915` (root of repo) |
| `OpenMontage_4_Factories_Deep_Research_2026-11-11.md` | **NOT FOUND** in any reachable ref | — |

### 10of10 — exact evidence

- **Path:** `OpenMontage_10of10_Four_Factories_OpenCode_Agent_Task_2026-11-11.md`
- **Branch:** `origin/main` (repo `sora73636-stack/OpenMontage`)
- **Commit:** `2f8f1915cc3db296bba081955ae5ba0cf4375af9` — `Add files via upload`, 2026-11-11 19:40:50 +0500
- **Blob SHA:** `84aaf47136d34aa3a6ca3bb1e90f6b07af58eed8`
- **File SHA-256:** `8d8fe0f074784fe8d1e18f862804a96d684bfee5c60659031e88575fa27fafd2`
- **Size:** 80,376 bytes / 1,044 lines
- **Commit also added:** `CHATGPT_KAGGLE_QUALITY_BRIEF.md` (not requested)
- **Read:** full document read; local analysis copy at `work/master-run/source/10of10.md`.

**Why the first pass missed it:** the local `origin/main` ref was stale. `git fetch
origin '+refs/heads/*:refs/remotes/origin/*'` updated it to `2f8f1915`, after which
`git ls-tree -r --name-only origin/main` and the GitHub tree API both returned the file.

### 4_Factories — search evidence

Searched, with no match:

1. All local/remote heads, tags, stash, dangling objects, reflog, worktrees.
2. **726 refs** after fetching every upstream head and every `refs/pull/*/head` and
   `refs/pull/*/merge` (blob:none fetch).
3. `git log --all --diff-filter=A --name-only` and `git rev-list --all --objects`.
4. Per-ref `git ls-tree -r` for every head/PR/merge ref.
5. GitHub code search (`gh search code`), commit search, Actions artifacts, releases,
   gists, wiki (`OpenMontage.wiki.git` does not exist).
6. 100 forks of `OpenMontageInc/OpenMontage` sampled via the default-branch tree
   (repository has 10,657 forks; a full 10k-fork scan is not feasible here).

The 10of10 document itself says the 4_Factories matrix is optional:

> `OpenMontage_4_Factories_Deep_Research_2026-11-11.md` — previous research matrix
> (`if available in the project; otherwise use the model/checkpoint lists embedded above`).

The embedded model/checkpoint lists in the 10of10 file were used as the fallback.

## Integrity

No source file was modified, deleted, renamed, or rewritten. No branch switch, no
`reset`, `clean`, `rebase`, `force-push`, or `stash` operation was performed. The 10of10
file remains in `origin/main` at commit `2f8f1915`; only a read-only copy was placed in
`work/master-run/source/10of10.md`.

## What this changes for the run

The 10of10 document is now the authoritative task. It requires:

- `COMPETITOR_VIDEO_AUDIT.csv` (done; 20 rows, 5 biology/evolution).
- Official YouTube baseline separated from house targets (done; `YOUTUBE_QUALITY_STANDARD.md`).
- `configs/model_matrix.yaml` and `configs/quality_gates.yaml` (done).
- `benchmark_result.json` per run (done for the local TTS benchmark).
- `FINAL_HANDOFF.md` (pending).
- Manim test, I2V/T2V tests, ACE-Step/SFX tests, human watch-through (not done; blockers documented).