import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

AGENT_TOKEN = os.environ.get("AGENT_TOKEN", "troque-este-token")
BACKUP_SOURCE = Path(os.environ.get("BACKUP_SOURCE", str(Path.home() / "Documents")))
BACKUP_DEST = Path(os.environ.get("BACKUP_DEST", str(Path.home() / "Desktop" / "backups_remotos")))
TEST_FOLDER = Path(os.environ.get("TEST_FOLDER", str(Path.home() / "Desktop" / "pasta_teste")))

HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Painel Remoto (Servidor + Agente)</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; max-width: 900px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
    button { width: 100%; padding: 12px; font-size: 14px; cursor: pointer; }
    .danger { background: #b00020; color: white; border: none; }
    .warn { background: #d47f00; color: white; border: none; }
    .ok { background: #006a4e; color: white; border: none; }
    .muted { color: #666; }
    pre { background: #f5f5f5; padding: 12px; overflow-x: auto; }
    input[type=text] { width: 100%; padding: 8px; margin: 6px 0 12px; }
  </style>
</head>
<body>
  <h1>Painel remoto</h1>
  <p class="muted">Fluxo: celular/painel → servidor → agente no PC.</p>

  <label>Mensagem de alerta no PC:</label>
  <input id="alertText" type="text" value="Atenção: ação remota solicitada." />

  <div class="grid">
    <button class="ok" onclick="sendAction('lock')">Bloquear sessão</button>
    <button class="warn" onclick="sendAction('alert')">Mostrar alerta</button>
    <button class="ok" onclick="sendAction('backup')">Fazer backup</button>
    <button class="warn" onclick="sendAction('clean_test')">Limpar pasta de teste</button>
    <button class="danger" onclick="sendAction('restart')">Reiniciar PC</button>
    <button class="danger" onclick="sendAction('shutdown')">Desligar PC</button>
  </div>

  <h3>Resposta</h3>
  <pre id="out">Aguardando ação...</pre>

  <script>
    async function sendAction(action) {
      const alert_text = document.getElementById('alertText').value;
      const res = await fetch('/api/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, alert_text })
      });
      const data = await res.json();
      document.getElementById('out').textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
"""


def _is_windows() -> bool:
    return os.name == "nt"


def _run_windows(cmd: list[str]) -> tuple[bool, str]:
    try:
        subprocess.run(cmd, check=True)
        return True, "OK"
    except subprocess.CalledProcessError as exc:
        return False, f"Falha (exit {exc.returncode})"


def action_lock() -> tuple[bool, str]:
    if not _is_windows():
        return False, "Bloqueio disponível apenas no Windows."
    return _run_windows(["rundll32.exe", "user32.dll,LockWorkStation"])


def action_alert(text: str) -> tuple[bool, str]:
    if not _is_windows():
        return False, "Alerta popup disponível apenas no Windows."
    safe = text.replace('"', "'")
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show(\"{safe}\",\"Alerta remoto\")"
    ]
    return _run_windows(cmd)


def action_backup() -> tuple[bool, str]:
    if not BACKUP_SOURCE.exists():
        return False, f"Origem de backup não existe: {BACKUP_SOURCE}"
    BACKUP_DEST.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DEST / f"backup_{stamp}"
    shutil.copytree(BACKUP_SOURCE, dest)
    return True, f"Backup criado em: {dest}"


def action_clean_test() -> tuple[bool, str]:
    if not TEST_FOLDER.exists():
        return True, f"Pasta de teste não existe: {TEST_FOLDER}"

    for item in TEST_FOLDER.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    return True, f"Pasta limpa: {TEST_FOLDER}"


def action_power(mode: str) -> tuple[bool, str]:
    if not _is_windows():
        return False, "Ação de energia disponível apenas no Windows."
    if mode == "shutdown":
        return _run_windows(["shutdown", "/s", "/t", "5"])
    if mode == "restart":
        return _run_windows(["shutdown", "/r", "/t", "5"])
    return False, "Modo de energia inválido."


@app.get("/")
def home():
    return render_template_string(HTML)


@app.post("/api/agent/action")
def agent_action():
    token = request.headers.get("X-Agent-Token", "")
    if token != AGENT_TOKEN:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    action = data.get("action")
    alert_text = data.get("alert_text", "Atenção: ação remota solicitada.")

    if action == "lock":
        ok, msg = action_lock()
    elif action == "alert":
        ok, msg = action_alert(alert_text)
    elif action == "backup":
        ok, msg = action_backup()
    elif action == "clean_test":
        ok, msg = action_clean_test()
    elif action in {"shutdown", "restart"}:
        ok, msg = action_power(action)
    else:
        return jsonify({"ok": False, "error": "ação inválida"}), 400

    return jsonify({"ok": ok, "message": msg, "action": action})


@app.post("/api/dispatch")
def dispatch():
    data = request.get_json(silent=True) or {}
    with app.test_request_context(
        "/api/agent/action",
        method="POST",
        json=data,
        headers={"X-Agent-Token": AGENT_TOKEN},
    ):
        return agent_action()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
