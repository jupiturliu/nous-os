const http = require('http');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SITE_DIR = path.join(ROOT, '_site');
const PORT = Number(process.env.PORT || process.env.NOUS_BACKEND_PORT || 8787);
const HOST = process.env.HOST || process.env.NOUS_BACKEND_HOST || '127.0.0.1';

function loadLocalHermesEnv() {
  const hermesEnv = path.join(process.env.HOME || '', '.hermes', '.env');
  if (!fs.existsSync(hermesEnv)) return;
  const lines = fs.readFileSync(hermesEnv, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
    const index = trimmed.indexOf('=');
    const key = trimmed.slice(0, index).trim();
    let value = trimmed.slice(index + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    if (key && process.env[key] === undefined) {
      process.env[key] = value;
    }
  }
  if (!process.env.HERMES_API_SERVER_KEY && process.env.API_SERVER_KEY) {
    process.env.HERMES_API_SERVER_KEY = process.env.API_SERVER_KEY;
  }
}

loadLocalHermesEnv();

if (!process.env.HERMES_API_SERVER_URL) {
  const gatewayRoot = String(process.env.HERMES_GATEWAY_URL || 'http://127.0.0.1:8642').replace(/\/+$/, '');
  process.env.HERMES_API_SERVER_URL = `${gatewayRoot}/v1/chat/completions`;
}
if (!process.env.HERMES_ALLOWED_ORIGIN) {
  process.env.HERMES_ALLOWED_ORIGIN = process.env.NOUS_PUBLIC_ORIGIN || `http://${HOST}:${PORT}`;
}

const hermesHandler = require('../api/hermes-student-agent');
const studentSandboxSessionHandler = require('../api/student-sandbox-session');

function stageSite() {
  const result = spawnSync('bash', [path.join(ROOT, 'scripts', 'stage_static_site.sh')], {
    cwd: ROOT,
    stdio: 'inherit',
  });
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.md': 'text/markdown; charset=utf-8',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
  }[ext] || 'application/octet-stream';
}

function sendJson(response, status, payload) {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  });
  response.end(JSON.stringify(payload));
}

function sendStatic(request, response) {
  const url = new URL(request.url, `http://${request.headers.host || `${HOST}:${PORT}`}`);
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === '/') pathname = '/index.html';
  if (pathname.endsWith('/')) pathname += 'index.html';

  const candidate = path.normalize(path.join(SITE_DIR, pathname));
  if (!candidate.startsWith(SITE_DIR)) {
    response.writeHead(403);
    response.end('Forbidden');
    return;
  }

  fs.readFile(candidate, (error, data) => {
    if (error) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('Not found');
      return;
    }
    response.writeHead(200, {
      'Content-Type': contentType(candidate),
      'Cache-Control': 'no-store',
    });
    response.end(data);
  });
}

function createServer() {
  return http.createServer((request, response) => {
    const url = new URL(request.url, `http://${request.headers.host || `${HOST}:${PORT}`}`);
    if (url.pathname === '/api/health') {
      sendJson(response, 200, {
        status: 'ok',
        service: 'nous-os-web-backend',
        hermes_api_server_configured: Boolean(process.env.HERMES_API_SERVER_URL),
        hermes_api_server_key_source: process.env.HERMES_API_SERVER_KEY ? 'local-env' : 'none',
        route: 'web-backend-to-hermes-gateway',
      });
      return;
    }
    if (url.pathname === '/api/hermes-student-agent') {
      hermesHandler(request, response).catch(error => {
        sendJson(response, 500, { error: error.message || 'Hermes backend server failed.' });
      });
      return;
    }
    if (url.pathname === '/api/student-sandbox-session') {
      studentSandboxSessionHandler(request, response).catch(error => {
        sendJson(response, 500, { error: error.message || 'Student sandbox session save failed.' });
      });
      return;
    }
    sendStatic(request, response);
  });
}

function start() {
  stageSite();
  const server = createServer();
  server.listen(PORT, HOST, () => {
    console.log(`NOUS OS web backend: http://${HOST}:${PORT}`);
    console.log(`Hermes API server: ${process.env.HERMES_API_SERVER_URL}`);
  });
  return server;
}

if (require.main === module) {
  start();
}

module.exports = {
  createServer,
  start,
};
