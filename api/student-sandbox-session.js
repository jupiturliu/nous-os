const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SESSION_DIR = path.join(ROOT, 'examples', 'runtime', 'student-sandbox-sessions');
const MAX_BODY_CHARS = 64000;
const MAX_TEXT_CHARS = 2000;
const MAX_TURNS = 24;

const FIELD_LIMITS = {
  question: 500,
  prior_belief: 800,
  boundary: 400,
  ai_plan_notes: 1400,
  source_notes: 1400,
  revised_plan: 1400,
  reflect_help: 900,
  reflect_verify: 900,
  reflect_responsibility: 900,
  reflect_next: 900,
  summary: 2000,
};

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
      if (body.length > MAX_BODY_CHARS) {
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

function redactPrivateText(value) {
  return String(value || '')
    .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '[redacted-email]')
    .replace(/\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b/g, '[redacted-phone]')
    .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[redacted-ssn]')
    .replace(/\b\d{9}\b/g, '[redacted-id]');
}

function containsPrivatePattern(value) {
  const text = String(value || '');
  return (
    /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(text) ||
    /\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b/.test(text) ||
    /\b\d{3}-\d{2}-\d{4}\b/.test(text) ||
    /\b\d{9}\b/.test(text)
  );
}

function safeText(value, limit = MAX_TEXT_CHARS) {
  return redactPrivateText(value).trim().slice(0, limit);
}

function safeSessionId(value) {
  const id = String(value || '').trim();
  if (!/^[a-zA-Z0-9_-]{8,80}$/.test(id)) {
    return `session-${Date.now()}`;
  }
  return id;
}

function safeObject(input = {}, limits = FIELD_LIMITS) {
  const output = {};
  for (const [key, limit] of Object.entries(limits)) {
    output[key] = safeText(input[key], limit);
  }
  return output;
}

function safeTurns(turns = []) {
  return turns.slice(-MAX_TURNS).map(turn => ({
    role: turn && turn.role === 'agent' ? 'agent' : 'student',
    text: safeText(turn && turn.text, 1600),
    created_at: safeText(turn && turn.created_at, 80),
  }));
}

function buildRecord(body) {
  const worksheet = safeObject(body.worksheet || {});
  const reflection = safeObject(body.reflection || {}, {
    reflect_help: FIELD_LIMITS.reflect_help,
    reflect_verify: FIELD_LIMITS.reflect_verify,
    reflect_responsibility: FIELD_LIMITS.reflect_responsibility,
    reflect_next: FIELD_LIMITS.reflect_next,
  });
  const summary = safeText(body.summary, FIELD_LIMITS.summary);
  const chatTurns = safeTurns(body.chat_turns || []);
  const serialized = JSON.stringify({
    worksheet: body.worksheet || {},
    reflection: body.reflection || {},
    summary: body.summary || '',
    chat_turns: body.chat_turns || [],
  });

  return {
    version: 'student_sandbox_session_v1',
    session_id: safeSessionId(body.session_id),
    saved_at: new Date().toISOString(),
    storage: {
      backend: 'local-filesystem',
      path_hint: 'examples/runtime/student-sandbox-sessions',
      browser_storage: false,
      local_only: true,
    },
    privacy: {
      contains_private_student_data: false,
      private_pattern_detected: containsPrivatePattern(serialized),
      redaction: 'email_phone_ssn_and_numeric_id_patterns',
      reminder: 'Do not enter full names, school names, teacher names, addresses, or family details.',
    },
    worksheet,
    reflection,
    summary,
    chat_turns: chatTurns,
  };
}

function sessionPath(sessionId) {
  return path.join(SESSION_DIR, `${safeSessionId(sessionId)}.json`);
}

function writeRecord(record) {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
  const data = JSON.stringify(record, null, 2);
  fs.writeFileSync(sessionPath(record.session_id), data);
  fs.writeFileSync(path.join(SESSION_DIR, 'latest.json'), data);
}

function readRecord(sessionId) {
  const filePath = sessionPath(sessionId);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

module.exports = async function handler(request, response) {
  response.setHeader('Access-Control-Allow-Origin', process.env.HERMES_ALLOWED_ORIGIN || 'https://nousos.ai');
  response.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  response.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (request.method === 'OPTIONS') {
    response.statusCode = 204;
    response.end();
    return;
  }

  if (request.method === 'GET') {
    const url = new URL(request.url, 'http://127.0.0.1');
    const sessionId = safeSessionId(url.searchParams.get('session_id'));
    const record = readRecord(sessionId);
    if (!record) {
      json(response, 404, { error: 'Student sandbox session not found.' });
      return;
    }
    json(response, 200, record);
    return;
  }

  if (request.method !== 'POST') {
    json(response, 405, { error: 'Use GET or POST for student sandbox sessions.' });
    return;
  }

  let body;
  try {
    body = await parseBody(request);
  } catch (error) {
    json(response, 400, { error: error.message });
    return;
  }

  const record = buildRecord(body);
  writeRecord(record);
  json(response, 200, {
    status: 'saved',
    session_id: record.session_id,
    saved_at: record.saved_at,
    private_pattern_detected: record.privacy.private_pattern_detected,
    storage: record.storage,
  });
};

module.exports._private = {
  buildRecord,
  containsPrivatePattern,
  redactPrivateText,
  safeSessionId,
  safeText,
  safeTurns,
  sessionPath,
};
