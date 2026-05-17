const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SESSION_DIR = path.join(ROOT, 'examples', 'runtime', 'student-sandbox-sessions');
const MAX_BODY_CHARS = 64000;
const MAX_TEXT_CHARS = 2000;
const MAX_TURNS = 24;
const MAX_SOURCE_CARDS = 4;

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

const SOURCE_CARD_LIMITS = {
  title: 240,
  url: 500,
  author: 240,
  date: 120,
  evidence: 700,
  uncertainty: 700,
  decision: 80,
};

const OBSERVER_LIMITS = {
  student_explained_question: 20,
  named_source_issue: 20,
  kept_human_responsibility: 20,
  used_ai_for_hints: 20,
  note: 1200,
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

function safeSourceCards(cards = []) {
  return cards.slice(0, MAX_SOURCE_CARDS).map((card, index) => ({
    id: safeText(card && card.id, 40) || `source-${index + 1}`,
    ...safeObject(card || {}, SOURCE_CARD_LIMITS),
  }));
}

function buildResearchSignals({ worksheet, reflection, sourceCards, chatTurns, observer }) {
  const acceptedSources = sourceCards.filter(card => card.decision === 'accepted').length;
  const sourceCardsComplete = sourceCards.filter(card =>
    card.title && card.author && card.date && card.evidence && card.uncertainty
  ).length;
  const reflectionFieldsComplete = [
    reflection.reflect_help,
    reflection.reflect_verify,
    reflection.reflect_responsibility,
    reflection.reflect_next,
  ].filter(Boolean).length;
  return {
    source_cards_total: sourceCards.length,
    source_cards_complete: sourceCardsComplete,
    accepted_sources: acceptedSources,
    reflection_fields_complete: reflectionFieldsComplete,
    chat_turns_total: chatTurns.length,
    has_human_boundary: Boolean(worksheet.boundary),
    has_revised_plan: Boolean(worksheet.revised_plan),
    observer_check_count: Object.entries(observer)
      .filter(([key, value]) => key !== 'note' && value === 'yes').length,
  };
}

function reviewReadiness(signals = {}) {
  const sourceCardsComplete = Number(signals.source_cards_complete || 0);
  const reflectionFieldsComplete = Number(signals.reflection_fields_complete || 0);
  const observerCheckCount = Number(signals.observer_check_count || 0);
  return {
    ready_for_first_pass: Boolean(signals.has_human_boundary),
    ready_for_second_pass: Boolean(signals.has_human_boundary && sourceCardsComplete >= 1),
    ready_for_review: Boolean(
      signals.has_human_boundary &&
      signals.has_revised_plan &&
      sourceCardsComplete >= 2 &&
      reflectionFieldsComplete >= 4
    ),
    source_cards_complete: sourceCardsComplete,
    reflection_fields_complete: reflectionFieldsComplete,
    observer_check_count: observerCheckCount,
  };
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
  const sourceCards = safeSourceCards(body.source_cards || []);
  const observer = safeObject(body.observer || {}, OBSERVER_LIMITS);
  const serialized = JSON.stringify({
    worksheet: body.worksheet || {},
    reflection: body.reflection || {},
    source_cards: body.source_cards || [],
    observer: body.observer || {},
    summary: body.summary || '',
    chat_turns: body.chat_turns || [],
  });
  const researchSignals = buildResearchSignals({ worksheet, reflection, sourceCards, chatTurns, observer });
  const readiness = reviewReadiness(researchSignals);

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
    source_cards: sourceCards,
    reflection,
    observer,
    research_signals: researchSignals,
    readiness,
    summary,
    chat_turns: chatTurns,
  };
}

function md(value, fallback = '[not filled]') {
  const text = String(value || '').trim();
  return text || fallback;
}

function yesNo(value) {
  return value ? 'yes' : 'no';
}

function buildReviewPacket(record) {
  const worksheet = record.worksheet || {};
  const reflection = record.reflection || {};
  const observer = record.observer || {};
  const signals = record.research_signals || {};
  const readiness = record.readiness || reviewReadiness(signals);
  const sources = Array.isArray(record.source_cards) ? record.source_cards : [];
  const turns = Array.isArray(record.chat_turns) ? record.chat_turns : [];
  const lines = [
    '# Student Sandbox v1 Trial Review',
    '',
    `- Session id: ${md(record.session_id)}`,
    `- Saved at: ${md(record.saved_at)}`,
    '- Observer role: parent / teacher / researcher / self-review',
    '- Trial type: real / student-adjacent / dry-run',
    '- Privacy: de-identified; no student name, school, email, phone, address, or raw private prompt',
    '',
    '## Session Summary',
    '',
    `- Research question: ${md(worksheet.question)}`,
    `- Prior belief: ${md(worksheet.prior_belief)}`,
    `- Human boundary: ${md(worksheet.boundary)}`,
    `- Revised plan: ${md(worksheet.revised_plan)}`,
    '',
    '## Readiness Snapshot',
    '',
    `- Ready for first pass: ${yesNo(readiness.ready_for_first_pass)}`,
    `- Ready for second pass: ${yesNo(readiness.ready_for_second_pass)}`,
    `- Ready for review: ${yesNo(readiness.ready_for_review)}`,
    `- Complete source cards: ${md(readiness.source_cards_complete, '0')}`,
    `- Complete reflection fields: ${md(readiness.reflection_fields_complete, '0')}`,
    `- Observer checks: ${md(readiness.observer_check_count, '0')}`,
    '',
    '## Source Cards',
    '',
  ];
  if (sources.length === 0) {
    lines.push('- No structured source cards saved.');
  } else {
    sources.forEach(source => {
      lines.push(`### ${md(source.id, 'source')}: ${md(source.title)}`);
      lines.push('');
      lines.push(`- Author / institution: ${md(source.author)}`);
      lines.push(`- Date: ${md(source.date)}`);
      lines.push(`- Decision: ${md(source.decision, 'pending')}`);
      lines.push(`- Evidence: ${md(source.evidence)}`);
      lines.push(`- Uncertainty: ${md(source.uncertainty)}`);
      lines.push('');
    });
  }
  lines.push(
    '## Reflection',
    '',
    `- What did AI help with? ${md(reflection.reflect_help)}`,
    `- What did the student verify? ${md(reflection.reflect_verify)}`,
    `- What remains human responsibility? ${md(reflection.reflect_responsibility)}`,
    `- What would change next time? ${md(reflection.reflect_next)}`,
    '',
    '## Observer Notes',
    '',
    `- Student explained the question: ${md(observer.student_explained_question, 'no')}`,
    `- Student named one source issue: ${md(observer.named_source_issue, 'no')}`,
    `- Student kept human responsibility: ${md(observer.kept_human_responsibility, 'no')}`,
    `- AI was used for hints, not final-answer writing: ${md(observer.used_ai_for_hints, 'no')}`,
    `- Note: ${md(observer.note)}`,
    '',
    '## NOUS Guide Evidence',
    '',
    `- Saved chat turns: ${turns.length}`,
    '- Review note: inspect whether NOUS Guide gave hints, source-check questions, and boundary support rather than final-answer text.',
    '',
    '## Next-run Change',
    '',
    '- Single focused improvement to make before the next session:',
    '',
    '## Research Interpretation',
    '',
    '- Human capability delta:',
    '- Trust calibration:',
    '- Boundary integrity:',
    '- Memory / protocol update:',
    ''
  );
  return lines.join('\n');
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

function listRecords(limit = 20) {
  if (!fs.existsSync(SESSION_DIR)) return [];
  return fs.readdirSync(SESSION_DIR)
    .filter(name => name.endsWith('.json') && name !== 'latest.json')
    .map(name => path.join(SESSION_DIR, name))
    .map(filePath => {
      try {
        const record = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        return {
          session_id: record.session_id,
          saved_at: record.saved_at,
          question: record.worksheet && record.worksheet.question,
          private_pattern_detected: Boolean(record.privacy && record.privacy.private_pattern_detected),
          research_signals: record.research_signals || {},
          readiness: record.readiness || reviewReadiness(record.research_signals || {}),
        };
      } catch (error) {
        return null;
      }
    })
    .filter(Boolean)
    .sort((a, b) => String(b.saved_at || '').localeCompare(String(a.saved_at || '')))
    .slice(0, limit);
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
    if (url.searchParams.get('list') === '1') {
      const limit = Math.max(1, Math.min(50, Number(url.searchParams.get('limit') || 20)));
      json(response, 200, { sessions: listRecords(limit) });
      return;
    }
    const sessionId = safeSessionId(url.searchParams.get('session_id'));
    const record = readRecord(sessionId);
    if (!record) {
      json(response, 404, { error: 'Student sandbox session not found.' });
      return;
    }
    if (url.searchParams.get('format') === 'markdown') {
      response.statusCode = 200;
      response.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      response.setHeader('Cache-Control', 'no-store');
      response.end(buildReviewPacket(record));
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
  buildReviewPacket,
  buildResearchSignals,
  containsPrivatePattern,
  listRecords,
  redactPrivateText,
  reviewReadiness,
  safeSessionId,
  safeSourceCards,
  safeText,
  safeTurns,
  sessionPath,
};
