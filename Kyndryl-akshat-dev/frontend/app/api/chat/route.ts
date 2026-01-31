import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const backendRes = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: body.query,
        document_id: body.document_id,
      }),
    });

    const data = await backendRes.text();
    return new Response(data, { 
      status: backendRes.status,
      headers: { "Content-Type": "application/json" }
    });
  } catch {
    return new Response(JSON.stringify({ error: "Invalid Request" }), { status: 400 });
  }
}