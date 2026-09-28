import 'dotenv/config';
import { ApiClient } from './api-client.js';
import type { ApiStatus } from '@automatizar/shared';

const api = new ApiClient(process.env.INTERNAL_API_URL ?? 'http://localhost:3001');
const intervalMs = 30_000;
let busy = false;
async function checkApi(): Promise<void> {
  if (busy) return;
  busy = true;
  try {
    const health = await api.get<ApiStatus>('/api/health');
    console.log(`Worker pronto; API: ${health.status}`);
  } catch (error) {
    console.error('API indisponível:', error);
  } finally { busy = false; }
}
void checkApi();
const timer = setInterval(() => void checkApi(), intervalMs);
function shutdown(): void { clearInterval(timer); process.exit(0); }
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
