# Painel remoto + servidor + agente (Python/Flask) + Android APK

Fluxo: **celular/painel → servidor → agente no PC**.

## Servidor Python (PC)

Ações suportadas:
- Bloquear sessão do Windows
- Mostrar alerta na tela
- Fazer backup de pasta configurada
- Limpar apenas pasta de teste configurada
- Desligar ou reiniciar

### 1) Instalação
```bash
pip install -r requirements.txt
```

### 2) Configuração
- `AGENT_TOKEN` (obrigatório em produção)
- `BACKUP_SOURCE` (origem do backup; padrão: `~/Documents`)
- `BACKUP_DEST` (destino; padrão: `~/Desktop/backups_remotos`)
- `TEST_FOLDER` (pasta segura para limpeza; padrão: `~/Desktop/pasta_teste`)

Exemplo (PowerShell):
```powershell
$env:AGENT_TOKEN="seu-token-forte"
$env:BACKUP_SOURCE="C:\Users\SeuUsuario\Documents"
$env:BACKUP_DEST="C:\Users\SeuUsuario\Desktop\backups_remotos"
$env:TEST_FOLDER="C:\Users\SeuUsuario\Desktop\pasta_teste"
python app.py
```

## App Android

Projeto Android nativo em `android-app/` com botões para enviar ações ao endpoint `POST /api/agent/action`.

### 1) Abrir no Android Studio
- Abra a pasta `android-app` no Android Studio (Giraffe ou superior).
- Aguarde o sync do Gradle.

### 2) Gerar APK debug
No terminal, dentro de `android-app`:
```bash
./gradlew assembleDebug
```

APK gerado em:
```text
android-app/app/build/outputs/apk/debug/app-debug.apk
```

### 3) Configurar no app
No celular, informe:
- URL do servidor (ex: `http://192.168.0.10:5000`)
- `AGENT_TOKEN`
- Mensagem de alerta (opcional)

### 4) Instalar APK no Android
```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

> O celular e o PC precisam estar na mesma rede (ou com roteamento/VPN entre eles).


## APK pronto (GitHub Actions)

Se você quer o APK sem depender deste ambiente, use o workflow:

1. Vá em **Actions** no GitHub.
2. Rode **Build Android APK** (manual) ou faça push em `android-app/**`.
3. Baixe o artefato **app-debug-apk** ao final da execução.

Arquivo gerado: `app/build/outputs/apk/debug/app-debug.apk`.
