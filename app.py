from cryptography.fernet import Fernet, InvalidToken
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

KV = """
<RootWidget>:
    orientation: "vertical"
    padding: "16dp"
    spacing: "10dp"

    Label:
        text: "Criptografar e Descriptografar Mensagens"
        size_hint_y: None
        height: "40dp"

    TextInput:
        id: key_input
        hint_text: "Chave (deixe vazio para gerar automaticamente)"
        multiline: False

    TextInput:
        id: message_input
        hint_text: "Digite a mensagem"

    BoxLayout:
        size_hint_y: None
        height: "48dp"
        spacing: "8dp"

        Button:
            text: "Criptografar"
            on_release: root.encrypt_message()

        Button:
            text: "Descriptografar"
            on_release: root.decrypt_message()

    Label:
        text: "Resultado"
        size_hint_y: None
        height: "28dp"

    TextInput:
        id: result_output
        readonly: True
"""


class RootWidget(BoxLayout):
    def _get_or_generate_key(self):
        key_text = self.ids.key_input.text.strip()
        if key_text:
            return key_text.encode("utf-8")

        generated = Fernet.generate_key()
        self.ids.key_input.text = generated.decode("utf-8")
        return generated

    def encrypt_message(self):
        try:
            key = self._get_or_generate_key()
            message = self.ids.message_input.text.encode("utf-8")
            encrypted = Fernet(key).encrypt(message)
            self.ids.result_output.text = encrypted.decode("utf-8")
        except Exception as exc:
            self.ids.result_output.text = f"Erro ao criptografar: {exc}"

    def decrypt_message(self):
        try:
            key = self._get_or_generate_key()
            encrypted_message = self.ids.message_input.text.encode("utf-8")
            decrypted = Fernet(key).decrypt(encrypted_message)
            self.ids.result_output.text = decrypted.decode("utf-8")
        except InvalidToken:
            self.ids.result_output.text = "Erro: chave inválida ou mensagem corrompida."
        except Exception as exc:
            self.ids.result_output.text = f"Erro ao descriptografar: {exc}"


class CryptoMobileApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootWidget()


if __name__ == "__main__":
    CryptoMobileApp().run()
