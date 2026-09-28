import type { ErrorRequestHandler } from 'express';

export const errorHandler: ErrorRequestHandler = (error: unknown, _req, res, _next) => {
  console.error('Erro na API:', error);
  res.status(500).json({ error: 'Erro interno do servidor' });
};
