import { Router } from 'express';
import type { ApiStatus, TestResponse } from '@automatizar/shared';

export const apiRouter = Router();
apiRouter.get('/health', (_req, res) => {
  const result: ApiStatus = { status: 'ok', service: 'backend', timestamp: new Date().toISOString() };
  res.json(result);
});
apiRouter.get('/test', (_req, res) => {
  const result: TestResponse = { message: 'API funcionando', timestamp: new Date().toISOString() };
  res.json(result);
});
