import type { AutomationTask } from '@automatizar/shared';

export interface TaskQueue {
  enqueue(task: AutomationTask): Promise<void>;
  consume(handler: (task: AutomationTask) => Promise<void>): Promise<void>;
  close(): Promise<void>;
}

// Contrato para um adaptador persistente (Redis/BullMQ) na próxima fase.
// Sem adaptador, o worker não aceita nem descarta tarefas silenciosamente.
export class QueueNotConfigured implements TaskQueue {
  async enqueue(_task: AutomationTask): Promise<void> { throw new Error('Fila não configurada'); }
  async consume(_handler: (task: AutomationTask) => Promise<void>): Promise<void> { throw new Error('Fila não configurada'); }
  async close(): Promise<void> { /* nenhum recurso aberto */ }
}
