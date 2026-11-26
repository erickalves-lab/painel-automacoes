# Painel das automações

Página única que mostra, num relance, as automações agendadas do Erick: quantas estão ativas, quais rodaram hoje, quais falharam e o que ainda roda hoje.

- `index.html`: o painel. Lê o `data.json` e se atualiza sozinho a cada 5 minutos.
- `data.json`: a foto atual das automações (nome, horário, status, motivo de falha, duração). Não contém resultados, e-mails, vagas nem leads.
- `scripts/build_data.py`: transforma a lista de tarefas agendadas no `data.json`.
- `scripts/descricoes.json`: a linha "o que ela faz" de cada automação.
- `docs/ATUALIZAR.md`: o passo a passo que a tarefa de atualização segue.

A página é pública. Por isso nada de conteúdo das tarefas entra aqui.
