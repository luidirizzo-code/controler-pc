# App mobile em Python para criptografar e descriptografar mensagens

Este projeto cria um aplicativo de celular usando **Kivy** com um sistema de:
- **Criptografar** mensagens
- **Descriptografar** mensagens

A criptografia usa **Fernet** (biblioteca `cryptography`), que fornece criptografia simétrica com autenticação.

## Como executar localmente

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Rode o aplicativo:
   ```bash
   python app.py
   ```

## Como usar

1. No campo **Chave**, você pode:
   - Colar uma chave Fernet existente, ou
   - Deixar vazio para gerar automaticamente.
2. Digite o texto no campo **Digite a mensagem**.
3. Clique em:
   - **Criptografar** para gerar o texto criptografado.
   - **Descriptografar** para recuperar o texto original.
4. O resultado aparece no campo **Resultado**.

## Gerar APK (Android)

Para transformar em APK, use o **Buildozer** em ambiente Linux. Fluxo básico:

```bash
pip install buildozer
buildozer init
# ajuste buildozer.spec (nome, pacote, permissões e requirements)
buildozer -v android debug
```

> Observação: compilar APK exige SDK/NDK e dependências específicas do Android.
