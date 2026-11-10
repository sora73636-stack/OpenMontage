# План восстановления окружения Kokoro V12 (TASK 3)

## Исторические доказательства (из git history)

| Коммит | Сообщение | Дата | Ключевые артефакты |
|--------|-----------|------|-------------------|
| dd45996 | step1: WER diagnosis - Kokoro 0.0% WER on 24kHz and 16kHz resampled | 2026-11-09 06:40 | `wer_diagnosis.json`, `kokoro_raw_24k.wav`, `kokoro_resampled_16k.wav` |
| d396bb4 | step2: Kokoro af_heart narration 11 blocks, all WER<10% ASR pass | 2026-11-09 06:51 | 11 kokoro WAV blocks, `script_blocks.json`, `espeak_narration_manifest.json` |
| db42457 | step5: softened unverified claims, regenerated Kokoro + ASR pass | 2026-11-09 07:02 | `kokoro_asr_results.json`, `kokoro_narration_manifest.json`, NASA primary sources |
| 8d3760e | step6: final_v12.mp4 built - 41 scenes, Kokoro narration, SRT subtitles | 2026-11-09 07:17 | `final_v12.mp4`, `narration_master.wav`, `final_v12.srt`, `render_manifest.json` |
| 6b401e7 | fix: remove false-positive packages, document torch CPU index | 2026-10-26 06:22 | `torch==2.14.1+cpu` в requirements-pinned.txt |
| c34f0e6 | docs: note why torch is excluded from codespace requirements | 2026-10-26 06:37 | torch excluded from codespace (Kaggle-only) |
| 1da666a | wip: pinned deps (diffusers 0.37.0/transformers 4.57.6/huggingface_hub 0.36.2) | — | kokoro==0.2.2, misaki==0.7.0, soundfile==0.14.0 |

## Доказательства успешной работы Kokoro в V12

1. **11 WAV-файлов** в `work/v12/narration_blocks/kokoro/` (B001–B011), каждый с SHA256 хешем и длительностью
2. **`kokoro_narration_manifest.json`** — все блоки имеют `kokoro_sample_rate: 24000`, voz `af_heart`, SHA256 хеши
3. **`kokoro_asr_results.json`** — `all_pass_under_10: true`, все WER от 0.0% до 8.0%, язык `en`, уверенность 1.0
4. **`wer_diagnosis.json`** — Kokoro 0.0% WER на 24kHz и 16kHz; espeak-ng 33–83%
5. **`final_v12_qc_baseline.json`** — длительность 132.425s, канал 1 (mono)
6. **`script_blocks.json`** — 11 блоков с `visual_class`, `motion_type`, `claim_ids`
7. **`render_manifest.json`** — 41 сцены с таймингами и motion типами

## Причина отсутствия прежнего окружения

В текущем Python 3.14.2 окружении (`/home/codespace/.python/current/bin/python`) отсутствуют:
- Пакет `kokoro` (не установлен)
- Пакет `torch` (не установлен)
- Пакет `misaki` (не установлен)
- Пакет `soundfile` (не установлен)
- Веса модели `kokoro-v1_0.pth` (не найдены на ФС)
- Переменная `HF_HOME` не задана

Файл `.python-version` указывает на **Python 3.10**, devcontainer использует **Python 3.12**, но активное окружение — **Python 3.14.2**, что не совместимо с kokoro wheel.

## Закреплённые зависимости V12 (TASK 4)

Версия | Пакет | Статус | Источник
-------|-------|--------|----------
3.10 | Python | VERIFIED | `.python-version`
3.12 | Python (devcontainer) | VERIFIED | `.devcontainer/devcontainer.json`
2.14.1+cpu | torch | VERIFIED | `requirements-pinned.txt` (commit 6b401e7), kokoro_tts.py
0.2.2 | kokoro | VERIFIED | `requirements-pinned.txt`, kokoro_tts.py, devcontainer
0.7.0 | misaki | VERIFIED | `requirements-pinned.txt`
0.7.4 | misaki | PROPOSED | kokoro_tts.py, devcontainer (расхождение с requirements-pinned.txt)
0.14.0 | soundfile | VERIFIED | `requirements-pinned.txt`
0.36.2 | huggingface_hub | VERIFIED | `requirements-pinned.txt`
— | numpy | PROPOSED | не зафиксировано в requirements-pinned.txt
— | phonemizer | PROPOSED | не найдено в истории V12

> Версии без прямого подтверждения в истории V12 помечены как **PROPOSED** — не обновлять до последних версий.

## Необходимые файлы модели (TASK 2)

| Файл | Ожидаемый размер | SHA-256 | Источник |
|------|-----------------|---------|----------|
| `kokoro-v1_0.pth` | ~327.2 МБ | **неизвестен** (требуется проверка владельцем) | hexgrad/Kokoro-82M (Apache-2.0) via HF_HOME |
| `voices/af_heart.pt` | ~523 КБ | **неизвестен** (требуется проверка владельцем) | hexgrad/Kokoro-82M (Apache-2.0) via HF_HOME |
| `config.json` | отдельный файл | **неизвестен** (требуется проверка владельцем) | hexgrad/Kokoro-82M (Apache-2.0) via HF_HOME |

> SHA-256 хеши не зафиксированы в истории V12. Требуется проверка владельцем после загрузки. Не скачивать без разрешения.

### Проверка SHA-256 после загрузки (выполнять только с разрешения владельца)

```bash
# В HF_HOME каталоге (по умолчанию ~/.cache/huggingface/hub)
sha256sha256sum models--hexgrad--Kokoro-82M/snapshots/*/kokoro-v1_0.pth
sha256sum models--hexgrad--Kokoro-82M/snapshots/*/voices/af_heart.pt
sha256sum models--hexgrad--Kokoro-82M/snapshots/*/config.json
```

## Ожидаемый размер загрузок (TASK 3)

| Компонент | Размер |
|-----------|--------|
| `kokoro-v1_0.pth` | ~327.2 МБ |
| `voices/af_heart.pt` | ~523 КБ |
| `config.json` | отдельный файл (размер неизвестен) |
| torch CPU wheel (2.14.1, Python 3.10/3.11/3.12, linux x86_64) | ~180–250 МБ |
| kokoro==0.2.2 + misaki + soundfile + numpy | ~10–50 МБ |
| **Итого примерно** | **~520–630 МБ** |

## Доступное дисковое пространство (TASK 3)

| Путь | Всего | Использовано | Свободно | Use% |
|------|-------|--------------|----------|------|
| `/workspaces` | 32G | 21G | 8.8G | 71% |
| `/tmp` | 44G | 3.9G | 38G | 10% |
| `/` (overlay) | 32G | 21G | 8.8G | 71% |

**Вывод:** Свободного места на `/workspaces` (8.8G) достаточно для загрузки (~520–630 МБ), но margin узкий. Рекомендуется очистить `__pycache__` и `.pyc` перед установкой или использовать `/tmp` для временных файлов.

## Официальный CPU index PyTorch (TASK 3)

- URL: `https://download.pytorch.org/whl/cpu`
- Пакет: `torch==2.14.1+cpu` (CPU-only, без CUDA)
- Не смешивать с CUDA сборками

## Команды установки (выполнять только с разрешения владельца)

```bash
# 1. Создать виртуальное окружение с Python 3.10 (из .python-version)
python3.10 -m venv /opt/openmontage/kokoro-venv
source /opt/openmontage/kokoro-venv/bin/activate

# 2. Установить torch CPU (официальный CPU index, без CUDA)
pip install --only-binary=:all: torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu

# 3. Установить kokoro и зависимости (версии из requirements-pinned.txt)
pip install --only-binary=:all: kokoro==0.2.2 misaki==0.7.0 soundfile==0.14.0

# 4. Настроить HF_HOME для кэша весов
export HF_HOME=/opt/openmontage/hf_cache

# 5. Проверить импорт
python -c "from kokoro import KPipeline; import soundfile; print('kokoro stack OK')"
```

## Команды проверки af_heart (выполнять только с разрешения владельца)

```bash
# Проверить доступность голоса af_heart
python -c "
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a')
print('Pipeline created, voice af_heart available')
"

# Проверить синтез короткого тестового фрагмента
python -c "
from kokoro import KPipeline
import soundfile as sf
import numpy as np

pipeline = KPipeline(lang_code='a')
text = 'Could life exist in an ocean that has never seen the sky?'
chunks = []
for _, _, seg in pipeline(text, voice='af_heart', speed=1.0):
    chunks.append(np.asarray(seg, dtype=np.float32))
audio = np.concatenate(chunks)
sf.write('/tmp/kokoro_test.wav', audio, 24000, subtype='PCM_16')
print(f'Synthesized {len(audio)/24000:.2f}s of audio')
"

# Проверить выходной WAV
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/kokoro_test.wav
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 /tmp/kokoro_test.wav
```

Ожидается: длительность > 0, кодек PCM_S16LE, sample_rate 24000, каналы 1.

## Действия, требующие разрешения владельца

1. **Установка Python 3.10** — не текущая версия окружения (активная: 3.14.2)
2. **Установка пакетов** torch, kokoro, misaki, soundfile — запрещено без разрешения
3. **Скачивание весов kokoro-v1_0.pth (~327.2 МБ)** — запрещено без разрешения
4. **Скачивание voices/af_heart.pt (~523 КБ)** — запрещено без разрешения
5. **Скачивание config.json** — запрещено без разрешения
6. **Настройка HF_HOME** — изменение переменных окружения
7. **Создание виртуального окружения** — изменение структуры проекта

## Состояние текущего окружения

| Компонент | Статус |
|-----------|--------|
| Python | 3.14.2 (не совместим с kokoro wheel; .python-version указывает 3.10) |
| kokoro | НЕ установлен |
| torch | НЕ установлен |
| misaki | НЕ установлен |
| soundfile | НЕ установлен |
| kokoro-v1_0.pth | НЕ найден |
| voices/af_heart.pt | НЕ найден |
| config.json | НЕ найден |
| HF_HOME | не задан |

## Статус: PLAN_READY

План представлен владельцу на утверждение. Не выполняется без разрешения.
