import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.API_BASE ?? "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const upstream = await fetch(`${API_BASE}/api/plan-b`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  } catch (err) {
    console.error("plan-b proxy error:", err);
    return NextResponse.json(
      { fallback: true, error: "Upstream unavailable" },
      { status: 502 }
    );
  }
}

