# Tasks: OpenMontage V13 — cleanup, core fixes, V13 pilot (branch kilo/mega-100)
## РЕЗУЛЬТАТ: PARTIAL (коммит 7706b2a на ветке kilo/mega-100, не main, не новая ветка)

## Phase 0 — [x] ДОНЕ: идентификация, тег, базовые тесты
## Phase 1 — [x] ДОНЕ: уборка (11 doc в archive/, кеши очищены, cleanup_manifest.json, 0 новых collection error)
## Phase 2 — [x] ДОНЕ: P0 исправления + 20 регрессионных теста (budget_guard, image_generation_engine approval, release_gate fail-closed, Flow/CDP сухое тестирование)
## Phase 3 — [~] ДОНЕ частично: entrypoints.json + architecture_before_after.md; QC пороги приведены к −16 LUFS ±1.5; ничего мертвого не удалено (stickman/hyperframes имеют ссылки -> KEEP)
## Phase 4 — [~] ДОНЕ частично: storyboard/EDL/manifest/права/сценарий-черновик (work/v13/); ГОЛОС BLOCKED (Kokoro отсутствует, placeholder WAV не создан)
## Phase 5 — [x] ДОНЕ: превью v13_preview.mp4 (1920x1080@30, 178.7s), v13_qc.json/md (все blocking PASS), контактный лист + review-пакет (rubric.csv, watch_notes.md, owner_review_template.json, rights_ledger)
## Phase 6 — [x] ДОНЕ: final_report.md (формат Appendix A2)

## ФИНАЛЬНЫЙ СТАТУС: PARTIAL
- Готово: кодовые исправления + тесты, очистка ветки, манифесты, архитектурные отчёты, превью + полный QC + контактный лист + review-пакет.
- НЕ готово (блокеры, владелец): финальный voices-мастер V13 — Kokoro `af_heart` не установлен (голос BLOCKED), сценарий не утверждён владельцем, визуальный микс не соблюдает лимит AI 0-15% (требуются архив/оригинальные диаграммы).
- READY_FOR_OWNER_REVIEW не 달성лен (нет финального мастера, не все REQUIRED gates пройдены, нет rubric≥6.5/science≥8).
- OWNER_APPROVED не выставлен — только владелец может.
