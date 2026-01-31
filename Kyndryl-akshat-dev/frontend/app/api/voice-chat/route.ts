import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "No audio file provided" }, { status: 400 });
    }

    const backendFormData = new FormData();
    backendFormData.append("file", file, "voice_message.webm"); 

    console.log(`[Proxy] Forwarding audio to ${BACKEND_URL}/api/speech/voice-chat`);

    const backendRes = await fetch(`${BACKEND_URL}/api/speech/voice-chat`, {
      method: "POST",
      body: backendFormData,
      // @ts-expect-error FormData with file needs duplex option
      duplex: "half"
    });

    if (!backendRes.ok) {
      const text = await backendRes.text();
      console.error(`[Proxy Error] Speech API status ${backendRes.status}:`, text);
      return NextResponse.json(
        { error: `Backend Speech Failed: ${text}` },
        { status: backendRes.status }
      );
    }

    const json = await backendRes.json();
    return NextResponse.json(json);
  } catch (error) {
    console.error("[Proxy] Internal Error:", error);
    return NextResponse.json({ error: "Server Error" }, { status: 500 });
  }
}