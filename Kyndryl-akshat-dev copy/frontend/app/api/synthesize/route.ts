import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

/**
 * Synthesize text to speech
 * Proxies request to backend /api/speech/synthesize endpoint
 */
export async function POST(req: NextRequest) {
  try {
    const { text, language } = await req.json();

    if (!text) {
      return NextResponse.json(
        { error: "Text is required" },
        { status: 400 }
      );
    }

    // Create FormData for backend
    const formData = new FormData();
    formData.append("text", text);
    if (language) {
      formData.append("language", language);
    }

    console.log("[TTS DEBUG] Synthesizing text:", {
      text_length: text.length,
      language: language || "en"
    });

    const res = await fetch(`${BACKEND_URL}/api/speech/synthesize`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("[TTS DEBUG] Backend synthesis failed:", errorText);
      return NextResponse.json(
        { error: errorText || "TTS synthesis failed" },
        { status: res.status }
      );
    }

    const data = await res.json();
    console.log("[TTS DEBUG] Synthesis successful:", {
      audio_url: data.audio_url,
      has_audio: !!data.audio_url
    });

    return NextResponse.json(data);
  } catch (error) {
    console.error("[TTS DEBUG] Synthesis error:", error);
    return NextResponse.json(
      { error: "Internal server error during synthesis" },
      { status: 500 }
    );
  }
}
