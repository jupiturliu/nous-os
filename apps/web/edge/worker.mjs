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

function normalizeOrigin(value) {
  return String(value || '').trim().replace(/\/+$/, '');
}

async function proxyApiToBackend(request, env) {
  const backendOrigin = normalizeOrigin(env.NOUS_BACKEND_ORIGIN_URL || env.NOUS_WEB_BACKEND_URL);
  if (!backendOrigin) {
    return json(503, {
      error: 'NOUS backend server is not configured. Set NOUS_BACKEND_ORIGIN_URL on the Cloudflare Worker.',
    });
  }
  const incoming = new URL(request.url);
  const upstreamUrl = `${backendOrigin}${incoming.pathname}${incoming.search}`;
  const headers = new Headers(request.headers);
  headers.set('X-Nous-Edge', 'cloudflare-worker');
  headers.set('X-Forwarded-Host', incoming.host);
  headers.set('X-Forwarded-Proto', incoming.protocol.replace(':', ''));

  return fetch(new Request(upstreamUrl, {
    method: request.method,
    headers,
    body: request.body,
    redirect: 'manual',
  }));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/api/')) {
      return proxyApiToBackend(request, env);
    }
    return env.ASSETS.fetch(request);
  },
};

export const _private = {
  normalizeOrigin,
  proxyApiToBackend,
};
