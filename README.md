# Interview Copilot (FastAPI + Next.js)

Hệ thống hỗ trợ sàng lọc ứng viên bằng AI: phân tích CV/JD/ghi chú phỏng vấn, đề xuất câu hỏi follow-up, chấm điểm và tạo báo cáo tổng hợp.

## Tính năng chính

- Chạy pipeline AI qua API `POST /pipeline/run`
- Nhập:
  - CV text
  - JD text
  - Interview notes
- Trả về:
  - `candidate_profile`
  - `interview_questions`
  - `evaluation`
  - `final_report`
- Lưu lịch sử chạy vào DB (`pipeline_runs`)
- Xem lịch sử qua API `GET /pipeline/runs`
- UI tiếng Việt (Next.js) để nhập liệu và xem kết quả

## Kiến trúc

- **Frontend**: Next.js (`src/app/page.tsx`)
- **Backend**: FastAPI
- **Database**: PostgreSQL (hoặc SQLite fallback)
- **LLM Layer**:
  - Gọi OpenAI API khi có quota
  - Có fallback mock khi gặp lỗi quota/key để tránh app bị crash

Luồng xử lý:

1. User nhập dữ liệu từ UI
2. Frontend gọi `POST /pipeline/run`
3. Backend orchestrator gọi các agent:
   - ingestion agent
   - question agent
   - evaluation agent
   - report agent
4. Trả kết quả JSON cho frontend
5. Lưu lịch sử chạy vào bảng `pipeline_runs`

## Cấu trúc thư mục 

```bash
backend/
  app/
    api/
    agents/
    core/
    db/
    models/
    orchestrator/
frontend/
  src/app/
    page.tsx
    globals.css
```

## Cài đặt & chạy local

## 1) Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

Tạo file `.env` từ `.env.example` rồi điền giá trị thật.

Chạy server:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Backend docs:
- http://localhost:8000/docs

## 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Mở:
- http://localhost:3000

## API chính

### `POST /pipeline/run`
Chạy pipeline phân tích ứng viên.

Ví dụ payload:

```json
{
  "cv_text": "Backend Engineer with 3 years ...",
  "jd_text": "Hiring Backend Engineer ...",
  "interview_notes": "Candidate communicated clearly ..."
}
```

### `GET /pipeline/runs`
Lấy lịch sử chạy gần đây.

## Biến môi trường

Xem file `.env.example`.


