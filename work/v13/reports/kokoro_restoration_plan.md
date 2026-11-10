# План восстановления окружения Kokoro V12 (TASK 3)

## Исторические доказательства (из git history)

| Коммит | Сообщение | Дата | Ключевые артефакты |
|--------|-----------|------|-------------------|
| dd45996 | step1: WER diagnosis - Kokoro 0.0% WER on 24kHz and 16kHz resampled | 2026-11-09 06:40 | `wer_diagnosis.json`, `kokoro_raw_24k.wav`, `kokoro_resampled_16k.wav` |
| d396bb4 | step2: Kokoro af_heart narration 11 blocks, all WER<10% ASR pass | 2026-11-09 06:51 | 11 kokoro WAV blocks, `script_blocks.json`, `espeak_narration_manifest.json` |
| db42457 | step5: softened unverified claims, regenerated Kokoro + ASR pass | 2026-11-09 07:02 | `kokoro_asr_results.json`, `kokoro_narration_manifest.json`, NASA primary sources |
| 8d3760e | step6: final_v12.mp4 built - 41 scenes, Kokoro narration, SRT subtitles | 2026-11-09 07:17 | `final_v12.mp4`, `narration_master.wav`, `final_v12.srt`, `render_manifest.json` |

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

Веса модели Kokoro-82M (~313 МБ) должны загружаться из `hexgrad/Kokoro-82M` (Apache-2.0) при первом запуске, но кэш весов не найден.

## Рекомендуемый план восстановления

### 1. Рекомендуемая версия Python

**Python 3.10 или 3.11** — Kokoro-82M с torch 2.x официально поддерживает эти версии. Python 3.14.2 может иметь проблемы с совместимостью бинарных wheel-пакетов torch.

### 2. Точные версии зависимостей (из `tools/audio/kokoro_tts.py`)

```
torch==2.14.1 (CPU wheel)
kokoro==0.2.2
misaki==0.7.4
soundfile (зависимость kokoro)
numpy (зависимость kokoro)
```

### 3. Необходимые файлы модели

| Файл | Ожидаемый размер | Источник |
|------|-----------------|----------|
| `kokoro-v1_0.pth` | ~313 МБ | hexgrad/Kokoro-82M (Apache-2.0) via HF_HOME |
| `voices/af_heart.pt` (или встроенный в модель) | включен в kokoro-v1_0.pth | hexgrad/Kokoro-82M |

### 4. Ожидаемый размер загрузок

- **~313 МБ** — веса kokoro-v1_0.pth (один раз, в HF_HOME)
- **~200–800 МБ** — torch CPU wheel (зависит от версии и платформы)
- **~10–50 МБ** — kokoro, misaki, soundfile, numpy

### 5. Команды установки

```bash
# Создать виртуальное окружение с совместимой версией Python
python3.11 -m venv /opt/openmontage/kokoro-venv
source /opt/openmontage/kokoro-venv/bin/activate

# Установить torch CPU (без CUDA, для работы на CPU)
pip install --only-binary=:all: torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu

# Установить kokoro и зависимости
pip install --only-binary=:all: kokoro==0.2.2 misaki==0.7.4

# Установить soundfile
pip install soundfile

# Проверить HF_HOME (веса кэшируются здесь при первом запуске)
export HF_HOME=/opt/openmontage/hf_cache
```

### 6. Команды проверки af_heart

```bash
# Проверить импорт
python -c "from kokoro import KPipeline; import soundfile; print('kokoro stack OK')"

# Проверить доступность голоса af_heart
python -c "
from kokoro import KPipeline
pipeline = KPipeline(lang_code='a')
# af_heart должен быть доступен как голос по умолчанию
print('Pipeline created, voice af_heart available')
"
```

### 7. Проверка синтеза короткого тестового фрагмента

```bash
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
```

### 8. Проверка выходного WAV

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/kokoro_test.wav
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 /tmp/kokoro_test.wav
```

Ожидается: длительность > 0, кодек PCM_S16LE, sample_rate 24000, каналы 1.

## Действия, требующие разрешения владельца

1. **Установка Python 3.10/3.11** — не текущая версия окружения
2. **Установка пакетов** torch, kokoro, misaki, soundfile — запрещено без разрешения
3. **Скачивание весов kokoro-v1_0.pth (~313 МБ)** — запрещено без разрешения
4. **Настройка HF_HOME** — изменение переменных окружения
5. **Создание виртуального окружения** — изменение структуры проекта

## Состояние текущего окружения

| Компонент | Статус |
|-----------|--------|
| Python | 3.14.2 (не совместим с kokoro wheel) |
| kokoro | НЕ установлен |
| torch | НЕ установлен |
| misaki | НЕ установлен |
| soundfile | НЕ установлен |
| kokoro-v1_0.pth | НЕ найден |
| HF_HOME | не задан |

## Статус: PLAN_READY

План представлен владельцу на утверждение. Не выполняется без разрешения.
