export class ApiClient {
  constructor(
    private readonly baseUrl: string,
    private readonly token?: string,
  ) {
    if (!baseUrl.startsWith('https://') && !baseUrl.startsWith('http://localhost:')) {
      throw new Error('API_BASE_URL deve usar HTTPS (localhost é permitido em desenvolvimento)');
    }
  }

  async get<T>(path: string): Promise<T> {
    const response = await fetch(new URL(path.replace(/^\//, ''), `${this.baseUrl.replace(/\/$/, '')}/`), {
      headers: this.token ? { Authorization: `Bearer ${this.token}` } : {},
      signal: AbortSignal.timeout(10_000),
    });
    if (!response.ok) throw new Error(`Falha na API: HTTP ${response.status}`);
    return (await response.json()) as T;
  }
}
