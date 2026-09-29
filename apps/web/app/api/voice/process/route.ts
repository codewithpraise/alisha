import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const pyRes = await fetch('http://127.0.0.1:8000/api/voice/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!pyRes.ok) {
      const errText = await pyRes.text();
      return NextResponse.json({ error: `Backend returned ${pyRes.status}: ${errText}` }, { status: pyRes.status });
    }

    const data = await pyRes.json();
    return NextResponse.json(data);
  } catch (err: any) {
    console.error('[API Proxy Voice Process Error]:', err);
    return NextResponse.json({ error: err.message || 'Failed to proxy voice process to backend' }, { status: 500 });
  }
}
