#!/usr/bin/env python3
"""Gera data.json a partir da saída bruta de list_triggers.

Uso: python3 scripts/build_data.py triggers_raw.json > data.json

triggers_raw.json é uma lista com, para cada tarefa agendada:
  id, name, cron_expression, run_once_at, enabled, ended_reason, next_run_at,
  last_run: {status, fired_at, finished_at, failure_reason}   (last_run pode faltar)

Só saem para o site: nome, horário, status, motivo de falha e duração.
Nada do conteúdo das tarefas (prompts, resultados, e-mails, leads) entra no data.json.
"""
import sys, json, datetime as dt, re, os
from zoneinfo import ZoneInfo
try:
    from croniter import croniter
except ImportError:
    sys.exit("Falta o croniter: pip install croniter --break-system-packages")

SP = ZoneInfo("America/Sao_Paulo")
UTC = dt.timezone.utc
HERE = os.path.dirname(os.path.abspath(__file__))
DESC = json.load(open(os.path.join(HERE, "descricoes.json"), encoding="utf-8"))
DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"]

def parse(ts):
    if not ts: return None
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(UTC)

def iso(d):
    return d.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if d else ""

def split_cron(expr):
    tz = UTC
    m = re.match(r"CRON_TZ=(\S+)\s+(.*)", expr or "")
    if m:
        tz = ZoneInfo(m.group(1)); expr = m.group(2)
    return tz, (expr or "").strip()

def fires(expr, start, end):
    tz, e = split_cron(expr)
    if not e: return []
    it = croniter(e, start.astimezone(tz))
    out = []
    for _ in range(400):
        n = it.get_next(dt.datetime)
        if n.astimezone(UTC) >= end: break
        out.append(n.astimezone(UTC))
    return out

def quando_auto(t):
    if t.get("run_once_at"):
        d = parse(t["run_once_at"]).astimezone(SP)
        return f"uma vez, {d:%d/%m} às {d.hour}h{d.minute:02d}"
    now = dt.datetime.now(UTC)
    fs = [f.astimezone(SP) for f in fires(t.get("cron_expression", ""), now, now + dt.timedelta(days=14))]
    if not fs: return ""
    horas = sorted({f"{f.hour}h" + (f"{f.minute:02d}" if f.minute >= 20 else "") for f in fs})
    dias = sorted({(f.weekday() + 1) % 7 for f in fs})
    if len(dias) == 7: d = "todo dia"
    elif dias == [1, 2, 3, 4, 5]: d = "seg a sex"
    else:
        nomes = [DIAS[i] for i in dias]
        d = nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]
    return d + ", " + " e ".join(horas)

def main(path):
    raw = json.load(open(path, encoding="utf-8"))
    now = dt.datetime.now(UTC)
    fim_hoje = (now.astimezone(SP).replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=1)).astimezone(UTC)
    out = []
    for t in raw:
        i = t["id"]; ds = DESC.get(i, {})
        enabled = bool(t.get("enabled"))
        once = bool(t.get("run_once_at"))
        lr = t.get("last_run") or {}
        fired, fin = parse(lr.get("fired_at")), parse(lr.get("finished_at"))
        st = {"SUCCEEDED": "ok", "FAILED": "falhou"}.get(lr.get("status", ""), "")
        nxt = parse(t.get("next_run_at")) if enabled else None
        if enabled and not once:
            slots = fires(t.get("cron_expression", ""), now, fim_hoje)
            if nxt:  # o disparo real tem um pequeno atraso: usa o horário informado
                slots = [nxt if abs((s - nxt).total_seconds()) <= 1200 else s for s in slots]
        elif enabled and once and nxt and nxt < fim_hoje:
            slots = [nxt]
        else:
            slots = []
        fora = ""
        if not enabled:
            fora = ds.get("fora") or ("Disparo único já executado" if once and fired else "Desativada")
        out.append({
            "id": i,
            "nome": t.get("name", ""),
            "quando": ds.get("quando") or quando_auto(t),
            "ativa": enabled,
            "estado": "fora" if not enabled else ("unica" if once else "ativa"),
            "fora": fora,
            "proxima": iso(nxt),
            "slots_hoje": ",".join(iso(s) for s in slots),
            "ultima": iso(fired),
            "status": st,
            "motivo": lr.get("failure_reason", "") if st == "falhou" else "",
            "duracao": int((fin - fired).total_seconds()) if fired and fin else 0,
            "posicao": iso(now),
            "funcao": ds.get("funcao", ""),
        })
    out.sort(key=lambda r: (not r["ativa"], r["proxima"] or "9"))
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1])
