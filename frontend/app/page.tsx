"use client";

import { useEffect, useMemo, useState } from "react";
import "./globals.css";

type PipelineResponse = {
  candidate_profile: any;
  interview_questions: Array<{
    question: string;
    why_ask: string;
    signal_to_look_for: string;
  }>;
  evaluation: any;
  final_report: string;
};

type RunItem = {
  id: number;
  status: "success" | "failed";
  error_message: string | null;
  created_at: string;
};

const API_BASE = "http://localhost:8000";

const UI_TEXT = {
  title: "Trợ lý Phỏng vấn AI",
  subtitle: "Hệ thống hỗ trợ sàng lọc ứng viên",
  cv: "Nội dung CV",
  jd: "Mô tả công việc (JD)",
  notes: "Ghi chú phỏng vấn",
  run: "Chạy phân tích",
  running: "Đang xử lý...",
  result: "Kết quả phân tích",
  history: "Lịch sử chạy gần đây",
  empty: "Chưa có dữ liệu.",
  errorGeneric: "Có lỗi xảy ra, vui lòng thử lại.",
  error422: "Vui lòng nhập đầy đủ nội dung (mỗi ô tối thiểu 20 ký tự).",
};

export default function Page() {
  const [cvText, setCvText] = useState("");
  const [jdText, setJdText] = useState("");
  const [interviewNotes, setInterviewNotes] = useState("");

  const [result, setResult] = useState<PipelineResponse | null>(null);
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [error, setError] = useState("");

  const canRun = useMemo(() => {
    return (
      cvText.trim().length >= 20 &&
      jdText.trim().length >= 20 &&
      interviewNotes.trim().length >= 20
    );
  }, [cvText, jdText, interviewNotes]);

  const fetchRuns = async () => {
    try {
      setLoadingRuns(true);
      const res = await fetch(`${API_BASE}/pipeline/runs`);
      if (!res.ok) throw new Error("Không tải được lịch sử chạy");
      const data = await res.json();
      setRuns(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingRuns(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleRun = async () => {
    setError("");
    setResult(null);

    if (!canRun) {
      setError(UI_TEXT.error422);
      return;
    }

    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/pipeline/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cv_text: cvText,
          jd_text: jdText,
          interview_notes: interviewNotes,
        }),
      });

      if (res.status === 422) {
        setError(UI_TEXT.error422);
        return;
      }

      if (!res.ok) {
        throw new Error(UI_TEXT.errorGeneric);
      }

      const data = await res.json();
      setResult(data);
      await fetchRuns();
      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    } catch (e) {
      console.error(e);
      setError(UI_TEXT.errorGeneric);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <h1 className="title">{UI_TEXT.title}</h1>
      <p className="subtitle">{UI_TEXT.subtitle}</p>

      <section className="card">
        <label className="label">{UI_TEXT.cv}</label>
        <textarea
          className="textarea"
          placeholder="Dán CV của ứng viên..."
          value={cvText}
          onChange={(e) => setCvText(e.target.value)}
        />

        <label className="label">{UI_TEXT.jd}</label>
        <textarea
          className="textarea"
          placeholder="Dán mô tả công việc (JD)..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />

        <label className="label">{UI_TEXT.notes}</label>
        <textarea
          className="textarea"
          placeholder="Nhập ghi chú sau buổi phỏng vấn..."
          value={interviewNotes}
          onChange={(e) => setInterviewNotes(e.target.value)}
        />

        <div className="row">
          <button className="btn btn-primary" onClick={handleRun} disabled={loading}>
            {loading ? UI_TEXT.running : UI_TEXT.run}
          </button>
        </div>

        {error && <p className="error">{error}</p>}
      </section>

      <section className="card">
        <h3>{UI_TEXT.history}</h3>
        {loadingRuns ? (
          <p>Đang tải...</p>
        ) : runs.length === 0 ? (
          <p>{UI_TEXT.empty}</p>
        ) : (
          <div className="pre">
            {runs.map((r) => (
              <div key={r.id} style={{ marginBottom: 10 }}>
                <b>#{r.id}</b> —{" "}
                <span className={`badge ${r.status === "success" ? "badge-success" : "badge-error"}`}>
                  {r.status}
                </span>{" "}
                — {new Date(r.created_at).toLocaleString("vi-VN")}
                {r.error_message ? <div>Lỗi: {r.error_message}</div> : null}
              </div>
            ))}
          </div>
        )}
      </section>

      {result && (
        <section className="card">
          <h3>{UI_TEXT.result}</h3>
          <div className="pre">{JSON.stringify(result, null, 2)}</div>
        </section>
      )}
    </main>
  );
}