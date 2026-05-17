const MAX_MESSAGE_CHARS = 1200;
const DEFAULT_GATEWAY_MODEL = 'hermes-agent';

function json(response, status, payload) {
  response.statusCode = status;
  response.setHeader('Content-Type', 'application/json; charset=utf-8');
  response.setHeader('Cache-Control', 'no-store');
  response.end(JSON.stringify(payload));
}

function parseBody(request) {
  return new Promise((resolve, reject) => {
    let body = '';
    request.on('data', chunk => {
      body += chunk;
      if (body.length > 16000) {
        reject(new Error('Request body too large.'));
        request.destroy();
      }
    });
    request.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(new Error('Invalid JSON request body.'));
      }
    });
    request.on('error', reject);
  });
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

module.exports = async function handler(request, response) {
  response.setHeader('Access-Control-Allow-Origin', process.env.HERMES_ALLOWED_ORIGIN || 'https://nousos.ai');
  response.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  response.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (request.method === 'OPTIONS') {
    response.statusCode = 204;
    response.end();
    return;
  }

  if (request.method !== 'POST') {
    json(response, 405, { error: 'Use POST for Hermes student agent requests.' });
    return;
  }

  const gatewayUrl = normalizeGatewayUrl(process.env.HERMES_GATEWAY_URL);
  if (!gatewayUrl) {
    json(response, 503, { error: 'Hermes Gateway is not configured. Set HERMES_GATEWAY_URL on the server.' });
    return;
  }

  let body;
  try {
    body = await parseBody(request);
  } catch (error) {
    json(response, 400, { error: error.message });
    return;
  }

  const message = String(body.message || '').trim().slice(0, MAX_MESSAGE_CHARS);
  if (!message) {
    json(response, 400, { error: 'Missing student message.' });
    return;
  }

  const model = process.env.HERMES_GATEWAY_MODEL || DEFAULT_GATEWAY_MODEL;
  const headers = {
    'Content-Type': 'application/json',
    'X-Hermes-Session-Key': 'nous-os-student-sandbox-v1',
  };
  if (process.env.HERMES_GATEWAY_API_KEY) {
    headers.Authorization = `Bearer ${process.env.HERMES_GATEWAY_API_KEY}`;
  }

  const upstream = await fetch(`${gatewayUrl}/v1/chat/completions`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model,
      messages: buildGatewayMessages(message, body),
      temperature: 0.3,
      max_tokens: 500,
      stream: false,
    }),
  });

  const payload = await upstream.json().catch(() => ({}));
  if (!upstream.ok) {
    json(response, upstream.status, {
      error: payload.error?.message || 'Hermes Gateway request failed.',
    });
    return;
  }

  json(response, 200, {
    reply: extractGatewayReply(payload) || 'Hermes Gateway returned an empty reply. Try again with a shorter question.',
    model,
    agent: 'hermes-student-agent',
    route: 'hermes-gateway',
  });
};

module.exports._private = {
  buildGatewayMessages,
  compactWorksheet,
  extractGatewayReply,
  hermesSystemPrompt,
  normalizeGatewayUrl,
};
