import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get("file") as File | null;

    if (!file) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    const MAX_SIZE_MB = 10;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    if (file.size > MAX_SIZE_BYTES) {
      return NextResponse.json(
        { error: `File size exceeds ${MAX_SIZE_MB}MB limit.` }, 
        { status: 413 }
      );
    }

    const backendFormData = new FormData();
    backendFormData.append("file", file, file.name);

    backendFormData.forEach((value, key) => {
      console.log(`[FormData Debug] "${key}":`, value instanceof File ? value.name : value);
    });

    console.log(`[Proxy] Forwarding "${file.name}" to ${BACKEND_URL}/api/upload/`);

    const backendRes = await fetch(`${BACKEND_URL}/api/upload/`, {
      method: "POST",
      body: backendFormData,
      // @ts-expect-error FormData with file needs duplex option
      duplex: "half"
    });

    if (!backendRes.ok) {
      const text = await backendRes.text();
      console.error(`[Proxy Error] Backend responded with status ${backendRes.status}:`, text);
      return NextResponse.json(
        { error: `Backend Upload Failed: ${text}` },
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