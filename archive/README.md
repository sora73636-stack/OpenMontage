# OpenMontage Archive — historical documents moved from active tree

Moved here by `git mv` during V13 maintenance (branch `kilo/mega-100`, HEAD
`1717fc20c0f27c9eedfe30ac9503108f60523e41`, safety tag
`pre-v13-maintenance-20261110-114934`), per `VIDEO_BUILD_TASK_V13.md` S2.1 §4.

These are historical versioned plans/reports. They remain in Git (full history
preserved) but are removed from the active documentation root so they are not
mistaken for current decisions.

Restore command (from repo root):
    git restore --source=pre-v13-maintenance-20261110-114934 -- <original-path>
    # then re-stage if you want them back in the active tree.

| Archived from | Moved to | Reason |
|---------------|----------|--------|
| FACTORY_MASTER_BUILD_V7.md | archive/root_docs/ | Superseded V7 factory plan |
| FACTORY_RESEARCH_AND_ARCHITECTURE_AUDIT_V8.md | archive/root_docs/ | Superseded V8 audit |
| V9_QUALITY_EXPERIMENTS.md | archive/root_docs/ | Superseded V9 experiments |
| docs/END_OF_DAY_SUMMARY_V7.md | archive/docs/ | Historical end-of-day summary |
| docs/END_OF_DAY_SUMMARY_V8.md | archive/docs/ | Historical end-of-day summary |
| docs/BUILD_LOG_V7.md | archive/docs/ | Historical build log |
| docs/BUILD_LOG_V8.md | archive/docs/ | Historical build log |
| docs/OPENMONTAGE_PLAN_V3_2.md | archive/docs/ | Superseded plan |
| docs/ARCHITECTURE_PIVOT_V5.md | archive/docs/ | Superseded architecture pivot |
| docs/P4_TEST_REPORT.md | archive/docs/ | Historical test report |
| docs/P5_TEST_REPORT.md | archive/docs/ | Historical test report |

No source code, media, weights, `.git/`, `.gflow/`, `assets/music/`, user
changes, or protected paths were removed or modified by this archiving.
