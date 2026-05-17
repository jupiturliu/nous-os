const http = require('http');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SITE_DIR = path.join(ROOT, '_site');
const PORT = Number(process.env.PORT || 8787);
const HOST = process.env.HOST || '127.0.0.1';

if (!process.env.HERMES_GATEWAY_URL) {
  process.env.HERMES_GATEWAY_URL = 'http://127.0.0.1:8642';
}
if (!process.env.HERMES_ALLOWED_ORIGIN) {
  process.env.HERMES_ALLOWED_ORIGIN = `http://${HOST}:${PORT}`;
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

stageSite();

const server = http.createServer((request, response) => {
  const url = new URL(request.url, `http://${request.headers.host || `${HOST}:${PORT}`}`);
  if (url.pathname === '/api/hermes-student-agent') {
    hermesHandler(request, response).catch(error => {
      response.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
      response.end(JSON.stringify({ error: error.message || 'Hermes local server failed.' }));
    });
    return;
  }
  sendStatic(request, response);
});

server.listen(PORT, HOST, () => {
  console.log(`NOUS OS local site: http://${HOST}:${PORT}`);
  console.log(`Hermes Gateway: ${process.env.HERMES_GATEWAY_URL}`);
});
