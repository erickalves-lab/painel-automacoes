# Como atualizar o data.json

Quem roda isto é uma tarefa agendada do Claude, de hora em hora. Passo a passo:

1. Chame `list_triggers` com `limit` 100 e pagine até acabar.
2. Salve em `triggers_raw.json` (fora do repositório, em /tmp) uma lista só com estes campos de cada tarefa: `id`, `name`, `cron_expression`, `run_once_at`, `enabled`, `ended_reason`, `next_run_at` e `last_run` (`status`, `fired_at`, `finished_at`, `failure_reason`). Não copie `derived_state`, `prompt` nem `mcp_connections`.
3. Rode `pip install croniter --break-system-packages` (se faltar) e depois `python3 scripts/build_data.py /tmp/triggers_raw.json > data.json`.
4. Se aparecer tarefa nova que não está em `scripts/descricoes.json`, acrescente uma linha curta de "o que ela faz", escrita em português e **sem nomes de pessoas, empresas, e-mails ou números de leads**.
5. Só faça commit se o `data.json` mudou além do campo `posicao`. Mensagem: `dados: atualização automática`. Envie para `main`.

Regra fixa: nada do conteúdo das tarefas (prompt, resultado, e-mail, vaga, lead) pode ir para este repositório. É público.
