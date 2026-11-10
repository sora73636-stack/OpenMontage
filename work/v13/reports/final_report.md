# Отчёт запуска V13 (Appendix A2 формат)

RUN_ID: v13-maintenance
REPO_ROOT: /workspaces/OpenMontage
BRANCH_BEFORE: kilo/mega-100
BRANCH_AFTER: kilo/mega-100 (ветка не переключалась, nuevos веток не создавалось)
HEAD_BEFORE: 1717fc20c0f27c9eedfe30ac9503108f60523e41
HEAD_AFTER: 1717fc20c0f27c9eedfe30ac9503108f60523e41 (до коммита 지원ки)
WORKTREE_BEFORE: грязный (см. work/v13/logs/s0/git_status.txt, untracked.txt, modified_sha256.txt)
SAFETY_TAG: pre-v13-maintenance-20261110-114934 (аннотирован, на HEAD 1717fc20, до первых изменений)
CLEANUP_SUMMARY: 11 документов заархивированы через git mv в archive/ (+ archive/README.md); очищены regenerable кеши (37 __pycache__ dirs, 517 .pyc, 1 .pytest_cache); 15 кандидатов оставлены (KEEP) с доказательством ссылок; ничего защищённого не удалено
CLEANUP_MANIFEST: work/v13/reports/cleanup_manifest.json (26 кандидатов, 3-way reference evidence: grep path+basename + Python AST imports + test/CI/Makefile/config refs)
DELETION_MANIFEST: не создано (ничего не удалено физически; только git mv в archive и очистка неотслеживаемых кешей)
CODE_FIXES:
  - lib/budget_guard.py: estimated_usd default = None; None (неизвестная стоимость) => blocked/fallback, никогда не free; только явный 0.0 разрешен. Вызывающий lib/scene_router.py передает 0.0 явно — не сломан.
  - lib/image_generation_engine.py: execute_approved() теперь передает реальный user_approved вместо hardcoded True.
  - lib/release_gate.py: реестр REQUIRED vs SOFT (REQUIRED_CHECK_IDS / declare_required); REQUIRED check absent/NOT_RUN/BLOCKED/FAIL/unknown => can_publish=False; SOFT NOT_RUN => WARNING, видно в summary; убран default PASS при неполном покрытии.
  - config/qc_thresholds.json + lib/final_qc.py DEFAULT_THRESHOLDS: lufs_target -14→-16.0, lufs_tolerance 2.0→1.5 (устранен drift vs требования задачи −16 LUFS ±1.5); единый канонический источник порогов.
CANONICAL_ENTRYPOINT: scripts/run_factory.py (13-этапный fail-closed orchestrator, zero_cost_gate + checkpoint). scripts/assemble_pilot_final.py — внутренний FFmpeg-хелпер рендера. scripts/run_episode.py — поддерживаемая альтернатива (тесты есть, реальныйツールчейн требует отсутствующий /tmp/kilo/z1_venv). Никакой второй рендер-фреймворк не создан; Remotion/HyperFrames не используются.
TESTS_BASELINE: 2803 collected, 3 collection errors (пред-existing: soundfile×2, test_08_end_to_end checkpoint). Зафиксировано в work/v13/logs/s0/pytest_collect_baseline.txt.
TESTS_AFTER: 2823 collected, 3 collection errors (те же 3 пред-existing, НОВЫХ ошибок нет). Добавлено 20 регрессионных теста: tests/lib/test_budget_guard.py (8), tests/lib/test_v13_release_gate.py (10, каждый утверждает can_publish), tests/factory/test_zero_cost_flow_cdp.py (2: Flow/CDP заблокирован без вызова провайдера и сети; ретрай не дублирует job).
RAW_COMMAND_LOGS: work/v13/logs/s0..s5 (stdout/stderr/exit code/UTC/cwd/команда/версии инструментов на каждый этап)
V13_MASTER_PATH: work/v13/render/v13_preview.mp4 (ПРЕВЬЮ, не финальный мастер)
V13_SHA256: 991223b683234b7a38ee8309e4323d7a259a1e339d0c7b226f92d02bdac2c192
FFPROBE: 1 video + 1 audio stream; 1920x1080@30fps; sar=1:1 dar=16:9; H.264/AAC 48kHz; 178.733s; 24.48 MB
AUDIO_QC: WARNING (music-only превью; повествование BLOCKED, цель −16 LUFS не применима; I=-70 LUFS из-за тихой музыки)
VIDEO_QC: PASS (ffprobe, full_decode, black_frames, silence, frozen_segments, frame_count 5362=5362, A/V delta 0.003s <=0.10s, SHA256 + aHash, EDL=render=storyboard=12 сцен). scene_cuts и subtitles = NOT_RUN (неприменимо к превью).
EDL_SCENES / RENDER_SCENES / TIMELINE_SPANS: 12 / 12 / 12
RUBRIC_SCORE: не вычислен (голос BLOCKED, невозможна объектная оценка критериев 6/7/8); см. work/v13/review_package/rubric.csv (все критерии в статусе REVIEW/BLOCKED/NOT_RUN/PASS только по техническому QC)
FLOW_IMAGES_USED: 0
VEO_USED: 0
KILO_REQUESTS: 0
CODESPACES_ACTIVE_MINUTES: не отсчитывался сегментно (старые этапы ≤15 мин, один ожидание ≤90 с)
DISK_BEFORE_AFTER: 9.1G -> 9.0G свободно из 32G (исключительно очистка кешей; медиа/веса/ассеты не трогались)
BLOCKERS:
  1. Kokoro `af_heart` пакет и веса НЕ установлены -> голосовой этап S4.3 BLOCKED, placeholder WAV не создан, финальныйvoices-мастер невозможен.
  2. faster_whisper НЕ установлен -> ASR/WERゲт BLOCKED, WER=0 не подделан.
  3. soundfile НЕ установлен -> lib/audio_engine.py и tools/audio/kokoro_tts.py не собираются (пред-existing, не вызвано этой работой).
  4. Visual budget не соблюдается в превью: 100% существующих AI-реконструкций (S1.2 лимит AI 0-15%). Требуются архив/оригинальные диаграммы владельца.
  5. Сценарий/раскадровка — черновик, требует утверждения владельцем перед финальным рендером (S4.1).
OWNER_ACTION_REQUIRED:
  - Установить Kokoro `af_heart` (пакет + веса) и верифицировать.
  - Утвердить сюжетное оформление (script_v13.md) и раскадровку (storyboard_v13.json / edit_decisions_v13.json).
  - Поставить compliant визуальный микс (~40-50% архив NASA/JPL/ESA, ~30-40% оригинальные PIL-диаграммы, 0-15% существующие AI).
  - Подтвердить музыку (ardune_red_moon.mp3 public domain) или предоставить лицензированный трек.
  - Только после этого: финальный рендер V13, полный QC, читательская приемка, статус READY_FOR_OWNER_REVIEW -> OWNER_APPROVED (только владелец).
FINAL_STATUS: PARTIAL
  Кодовые исправления (zero-cost, approval, release-gate) + регрессионные тесты — ГОТОВЫ.
  Очистка ветки + манифест + architecture_before_after/entrypoints — ГОТОВЫ.
  V13 превью (FFmpeg/PIL) + полный QC JSON/MD + контактный лист + review-пакет — СОБРАНЫ.
  Финальный voices-мастер V13 НЕ собран (блокер: Kokoro + утверждение владельца + визуальный микс). READY_FOR_OWNER_REVIEW не 달성лен (нет rubric≥6.5 / science≥8 без финального мастера, не все REQUIRED gates пройдены).
  OWNER_APPROVED не выставлен (только владелец может).
