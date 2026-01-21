# SemanticSearch

## Multilingual Search

Prompt Search accepts natural language queries and translates Vietnamese to English before embedding generation. If translation is unavailable, the system falls back to the original text with a warning so searches still complete.

## Content Type Detection

Searches automatically detect whether a query is for songs or sound effects. The UI displays a "Searching: Songs/SFX" chip that users can toggle to override detection for the current session.

## Example Prompts

The search page shows four categorized prompt examples (Mood/Emotion, Genre/Style, Use-Case, Sound Effects). Clicking an example runs the search immediately. Prompts are stored in `backend/config/example_prompts.json` for easy localization.

## Configuration

Prompt Search configuration uses environment variables:
- `TRANSLATION_SERVICE_PROVIDER` (google | googletrans | deepl)
- `TRANSLATION_API_KEY` (optional, depending on provider)
- `TRANSLATION_API_URL` (optional override, useful for self-hosted services)
- `MUSIC_CHECKPOINT_PATH` (default: `music_audioset_epoch_15_esc_90.14.pt`)

## Generating Music Embeddings

Use the embeddings script with the music checkpoint and content type:

```
python -m scripts.generate_embeddings \
  --audio-dir data/audio \
  --content-type song \
  --checkpoint music_audioset_epoch_15_esc_90.14.pt
```

By default, output is stored under `data/embeddings/song/` unless `--output-dir` is provided.

## Similarity Score Badges

Result cards display similarity scores with match tiers:
- 90-100%: Excellent Match (green)
- 75-89%: Good Match (blue)
- 60-74%: Fair Match (yellow)
- Below 60%: Low Match (gray)

## Development

#### Backend (terminal 1):

```
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# Generate embeddings once (after you add audio files)
# When add audio:
python -m scripts.generate_embeddings --audio-dir data/audio --output-dir data/embeddings --device cpu

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Troubleshooting (macOS)

If `python -m scripts.generate_embeddings ... --device cpu` crashes with `EXC_BAD_ACCESS` in `libomp`/`libtorch`, limit CPU thread usage before running:

```
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

python -m scripts.generate_embeddings --audio-dir data/audio --output-dir data/embeddings --device cpu
```

#### Frontend (terminal 2):

```
cd frontend
# echo 'VITE_API_BASE_URL=http://localhost:8000' > .env.local
npm run dev
```
