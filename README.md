# Nexo Estudo

Aplicação web responsiva para organizar tarefas escolares, salvar rascunhos e preparar roteiros de revisão. Contas, tarefas e rascunhos são armazenados em SQLite no servidor; senhas recebem hash `scrypt`, e a sessão usa cookie `HttpOnly` (nenhuma credencial da Sala do Futuro é solicitada ou salva no navegador).

## Executar

Requer Python 3.10+ e não possui dependências externas.

```bash
python3 server.py
```

Abra `http://localhost:8000`. O banco será criado em `data/nexo.db`. Para mudar o caminho ou a porta:

```bash
NEXO_DB=/var/lib/nexo/nexo.db PORT=8080 python3 server.py
```

## Publicar

Execute o servidor atrás de um proxy HTTPS (Caddy, Nginx ou serviço equivalente), configure `NEXO_DB` para um volume persistente e limite acesso ao arquivo do banco. Para produção em múltiplas instâncias, troque o dicionário de sessões em memória por um armazenamento compartilhado e marque o cookie como `Secure` no proxy/aplicação.

## Sala do Futuro

Em 27/09/2026, foi procurada documentação pública nos canais oficiais da SEDUC-SP para um método autorizado que permita a um aplicativo de terceiro ler as tarefas do próprio aluno. Não foi possível confirmar uma API pública documentada. O ambiente de pesquisa também bloqueou o acesso automatizado aos portais oficiais (HTTP 403), portanto **a sincronização automática permanece indisponível** e isso é informado na interface.

Não foi inventado endpoint, não se pede RA/senha e nenhuma atividade é apresentada como real. `sync_provider.py` mantém somente o contrato isolado para uma integração futura, que deve ser implementada apenas após documentação e autorização oficiais. A importação manual por texto/TXT funciona hoje; imagens e PDFs entram no fluxo de conferência, mas OCR/leitura automática ainda não é realizado.

## Funções e limites

- Cadastro, login, logout e painel privado.
- Indicadores, busca, filtros, criação, conclusão e exclusão de tarefas.
- Página da tarefa, enunciado, roteiro local de revisão e rascunho com salvamento automático.
- Importação de texto/TXT com extração básica e confirmação explícita.
- Modo demonstração isolado, sempre marcado como exemplo.
- Nenhum envio é feito à Sala do Futuro. O assistente apenas propõe passos de estudo e toda mudança de status depende de clique explícito.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

O teste automatizado cobre proteção de rotas, cadastro, criação/listagem de tarefa, atualização de rascunho e conclusão.
