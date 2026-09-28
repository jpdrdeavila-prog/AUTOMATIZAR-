import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import { apiRouter } from './routes/index.js';
import { errorHandler } from './middleware/error-handler.js';

export const app = express();
const allowedOrigin = process.env.FRONTEND_ORIGIN ?? 'http://localhost:5173';
app.disable('x-powered-by');
app.use(helmet());
app.use(cors({ origin: allowedOrigin }));
app.use(express.json({ limit: '1mb' }));
app.use('/api', apiRouter);
app.use((_req, res) => { res.status(404).json({ error: 'Rota não encontrada' }); });
app.use(errorHandler);
