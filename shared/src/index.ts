export interface ApiStatus {
  status: 'ok';
  service: 'backend';
  timestamp: string;
}

export interface TestResponse {
  message: string;
  timestamp: string;
}

export interface AutomationTask {
  id: string;
  type: string;
  payload: Record<string, unknown>;
  createdAt: string;
}
