# AUTOMATIZAR-

Base do monorepo: React/Vite/Tailwind 4, Express, worker Node e tipos compartilhados.

## Requisitos
Node.js 20.19+ e npm 10+.

## Desenvolvimento
```bash
cp .env.example .env
npm install
npm run dev
```
Acesse http://localhost:5173. API: http://localhost:3001/api/health e /api/test.

## Verificação e build
```bash
npm run build
npm run lint
npm run format:check
```
Para executar a compilação: `npm run start -w backend` e `npm run start -w worker` em terminais separados. O frontend estático fica em `frontend/dist`; sirva em hospedagem estática com `/api` redirecionado ao backend, ou configure a origem da API antes de publicar.

## Deploy
Backend: Node 20.19+, comando de build `npm install && npm run build`, start `npm run start -w backend`, variável `PORT` e `FRONTEND_ORIGIN` com a origem exata do frontend. Worker: mesmo build, start `npm run start -w worker`, variável `INTERNAL_API_URL` apontando ao backend. Frontend: build `npm install && npm run build`, diretório `frontend/dist`; configure proxy `/api` para o backend na hospedagem. Ainda não há fila, banco, autenticação ou integração externa. Os cartões refletem esse estado, e o worker apenas verifica a saúde da API. Não exponha endpoints futuros de execução antes de implementar autenticação e controle de acesso.
