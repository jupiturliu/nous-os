const MAX_MESSAGE_CHARS = 1200;
const DEFAULT_GATEWAY_MODEL = 'hermes-agent';

function json(status, payload, headers = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'no-store',
      ...headers,
    },
  });
}

function corsHeaders(env) {
  return {
    'Access-Control-Allow-Origin': env.HERMES_ALLOWED_ORIGIN || 'https://nousos.ai',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function compactWorksheet(worksheet = {}) {
  return {
    question: String(worksheet.question || '').slice(0, 500),
    prior_belief: String(worksheet.prior_belief || '').slice(0, 500),
    boundary: String(worksheet.boundary || '').slice(0, 300),
    ai_plan_notes: String(worksheet.ai_plan_notes || '').slice(0, 700),
    source_notes: String(worksheet.source_notes || '').slice(0, 700),
    revised_plan: String(worksheet.revised_plan || '').slice(0, 700),
  };
}

function normalizeGatewayUrl(value) {
  return String(value || '').trim().replace(/\/+$/, '');
}

function hermesSystemPrompt() {
  return [
    'You are Hermes, the NOUS OS Student Sandbox learning agent.',
    'You run behind Hermes Gateway. Preserve the gateway as the model/tool/provider boundary.',
    'Audience: a high-school student, sometimes with a parent or teacher nearby.',
    'Purpose: help the student think better with AI while preserving human agency.',
    'Privacy policy: do_not_request_or_store_private_student_data.',
    '',
    'Hard rules:',
    '- Do not write the final answer, essay, thesis paragraph, or finished homework.',
    '- Give hints, subquestions, source-check steps, boundary suggestions, and reflection prompts.',
    '- Keep the student responsible for goals, values, verification, final claim, and final wording.',
    '- Do not ask for private student data, full names, school names, teacher names, emails, phone numbers, addresses, or account details.',
    '- If the student includes private details, tell them to remove or generalize those details before continuing.',
    '- Use concise language suitable for a student and parent.',
    '',
    'Response shape:',
    '1. Briefly acknowledge the question.',
    '2. Give 2-4 useful hints or subquestions.',
    '3. Name one boundary to keep.',
    '4. Name one source check or verification move.',
    '5. End with one concrete next action in the worksheet.',
  ].join('\n');
}

function buildGatewayMessages(message, body) {
  return [
    { role: 'system', content: hermesSystemPrompt() },
    {
      role: 'user',
      content: JSON.stringify({
        student_message: message,
        worksheet: compactWorksheet(body.worksheet),
        sandbox_policy: body.policy || {},
      }),
    },
  ];
}

function extractGatewayReply(payload) {
  const choice = payload.choices && payload.choices[0];
  const content = choice && choice.message && choice.message.content;
  if (typeof content === 'string' && content.trim()) return content.trim();
  if (Array.isArray(content)) {
    return content
      .map(part => part && (part.text || part.content || ''))
      .filter(Boolean)
      .join('\n')
      .trim();
  }
  return '';
}

async function handleHermesStudentAgent(request, env) {
  const cors = corsHeaders(env);
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: cors });
  }
  if (request.method !== 'POST') {
    return json(405, { error: 'Use POST for Hermes student agent requests.' }, cors);
  }

  const gatewayUrl = normalizeGatewayUrl(env.HERMES_GATEWAY_URL);
  if (!gatewayUrl) {
    return json(503, { error: 'Hermes Gateway is not configured. Set HERMES_GATEWAY_URL on the Worker.' }, cors);
  }

  let body;
  try {
    body = await request.json();
  } catch (error) {
    return json(400, { error: 'Invalid JSON request body.' }, cors);
  }

  const message = String(body.message || '').trim().slice(0, MAX_MESSAGE_CHARS);
  if (!message) {
    return json(400, { error: 'Missing student message.' }, cors);
  }

  const headers = {
    'Content-Type': 'application/json',
    'X-Hermes-Session-Key': 'nous-os-student-sandbox-v1',
  };
  if (env.HERMES_GATEWAY_API_KEY) {
    headers.Authorization = `Bearer ${env.HERMES_GATEWAY_API_KEY}`;
  }

  const upstream = await fetch(`${gatewayUrl}/v1/chat/completions`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: env.HERMES_GATEWAY_MODEL || DEFAULT_GATEWAY_MODEL,
      messages: buildGatewayMessages(message, body),
      temperature: 0.3,
      max_tokens: 500,
      stream: false,
    }),
  });

  const payload = await upstream.json().catch(() => ({}));
  if (!upstream.ok) {
    return json(upstream.status, {
      error: payload.error?.message || 'Hermes Gateway request failed.',
    }, cors);
  }

  return json(200, {
    reply: extractGatewayReply(payload) || 'Hermes Gateway returned an empty reply. Try again with a shorter question.',
    model: env.HERMES_GATEWAY_MODEL || DEFAULT_GATEWAY_MODEL,
    agent: 'hermes-student-agent',
    route: 'cloudflare-worker-to-hermes-gateway',
  }, cors);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/hermes-student-agent') {
      return handleHermesStudentAgent(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};

export const _private = {
  buildGatewayMessages,
  compactWorksheet,
  extractGatewayReply,
  hermesSystemPrompt,
  normalizeGatewayUrl,
};
