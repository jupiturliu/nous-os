const http = require('http');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SITE_DIR = path.join(ROOT, '_site');
const PORT = Number(process.env.PORT || process.env.NOUS_BACKEND_PORT || 8787);
const HOST = process.env.HOST || process.env.NOUS_BACKEND_HOST || '127.0.0.1';

if (!process.env.HERMES_GATEWAY_URL) {
  process.env.HERMES_GATEWAY_URL = 'http://127.0.0.1:8642';
}
if (!process.env.HERMES_ALLOWED_ORIGIN) {
  process.env.HERMES_ALLOWED_ORIGIN = process.env.NOUS_PUBLIC_ORIGIN || `http://${HOST}:${PORT}`;
}

const hermesHandler = require('../api/hermes-student-agent');

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
        hermes_gateway_configured: Boolean(process.env.HERMES_GATEWAY_URL),
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
    sendStatic(request, response);
  });
}

function start() {
  stageSite();
  const server = createServer();
  server.listen(PORT, HOST, () => {
    console.log(`NOUS OS web backend: http://${HOST}:${PORT}`);
    console.log(`Hermes Gateway: ${process.env.HERMES_GATEWAY_URL}`);
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
