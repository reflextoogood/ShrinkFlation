# ShrinkFlation

Exposes shrinkflation — companies reducing product quantity while keeping prices the same.

## Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

API runs on http://localhost:8000  
Frontend runs on http://localhost:5173
