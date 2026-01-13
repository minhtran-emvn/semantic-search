# SemanticSearch

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
