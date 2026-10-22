import customtkinter as ctk
import hashlib
import hmac
import os
import re
import mysql.connector

from tkinter import messagebox
from database import conectar
import theme


# =========================================================
# ESTOQUE INTELIGENTE ULTIMATE — OBSIDIAN LOGIN
# =========================================================

PRETO = "#050505"
PAINEL = "#0A0A0C"
PAINEL_INTERNO = "#0E0F12"
CAMPO = "#090A0C"
BORDA_LOGIN = "#202126"
BORDA_FOCO = "#3B82F6"
AZUL_LOGIN = "#3B82F6"
AZUL_HOVER_LOGIN = "#2563EB"
BRANCO = "#F5F5F7"
CINZA = "#92929B"
CINZA_FRACO = "#65656F"


class TelaLogin(ctk.CTk):

    ITERACOES = 200_000

    def __init__(self, ao_entrar=None):
        super().__init__()

        self.ao_entrar = ao_entrar
        self.usuario_atual = None
        self.usuario_id = None
        self.papel_atual = "usuario"
        self.modo_cadastro = False

        self.title("Estoque Inteligente Ultimate | Acesso")
        self.geometry("940x600")
        self.minsize(800, 540)
        self.configure(fg_color=PRETO)

        self.criar_interface()

    # =====================================================
    # SEGURANCA DAS SENHAS
    # =====================================================

    @classmethod
    def gerar_hash(cls, senha, salt=None):
        if salt is None:
            salt = os.urandom(16)

        resultado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            cls.ITERACOES
        )

        return resultado.hex(), salt.hex()

    @classmethod
    def verificar_senha(cls, senha, salt_armazenado, hash_armazenado):
        try:
            salt = bytes.fromhex(salt_armazenado)

            resultado = hashlib.pbkdf2_hmac(
                "sha256",
                senha.encode("utf-8"),
                salt,
                cls.ITERACOES
            )

            return hmac.compare_digest(
                resultado.hex(),
                hash_armazenado
            )

        except (ValueError, TypeError, AttributeError):
            return False

    # =====================================================
    # VALIDACAO DO BANCO
    # =====================================================

    def verificar_banco(self):
        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute("SHOW COLUMNS FROM usuarios_app")

            colunas = {
                linha[0]
                for linha in cursor.fetchall()
            }

            necessarias = {
                "id",
                "usuario",
                "senha_hash",
                "salt",
                "criado_em"
            }

            faltantes = necessarias - colunas

            if faltantes:
                messagebox.showerror(
                    "Estrutura inesperada",
                    "A tabela usuarios_app nao possui todas as "
                    "colunas esperadas:\n"
                    + ", ".join(sorted(faltantes))
                    + "\n\nNenhuma alteracao foi feita no banco."
                )
                return False

            return True

        except mysql.connector.Error as erro:
            messagebox.showerror(
                "Erro de conexao",
                f"Nao foi possivel verificar o banco:\n{erro}"
            )
            return False

        finally:
            if cursor:
                cursor.close()

            if conexao and conexao.is_connected():
                conexao.close()

    # =====================================================
    # COMPONENTES VISUAIS
    # =====================================================

    def criar_interface(self):
        principal = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        principal.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=25
        )

        # Painel esquerdo: identidade visual
        self.painel_esquerdo = ctk.CTkFrame(
            principal,
            fg_color=PAINEL,
            corner_radius=18,
            border_width=1,
            border_color="#17181C",
            width=360
        )
        self.painel_esquerdo.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 14)
        )
        self.painel_esquerdo.pack_propagate(False)

        # Detalhe azul superior
        faixa = ctk.CTkFrame(
            self.painel_esquerdo,
            fg_color=AZUL_LOGIN,
            height=3,
            corner_radius=0
        )
        faixa.pack(fill="x")
        faixa.pack_propagate(False)

        marca = ctk.CTkFrame(
            self.painel_esquerdo,
            fg_color="#111722",
            corner_radius=18,
            border_width=1,
            border_color="#25334A",
            width=82,
            height=82
        )
        marca.pack(pady=(72, 22))
        marca.pack_propagate(False)

        ctk.CTkLabel(
            marca,
            text="EI",
            text_color="#79ADFF",
            font=("Segoe UI", 31, "bold")
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.painel_esquerdo,
            text="Estoque Inteligente",
            font=("Segoe UI", 24, "bold"),
            text_color=BRANCO
        ).pack(pady=(0, 7))

        ctk.CTkLabel(
            self.painel_esquerdo,
            text="ULTIMATE EDITION",
            font=("Segoe UI", 10, "bold"),
            text_color=AZUL_LOGIN
        ).pack(pady=(0, 20))

        separador = ctk.CTkFrame(
            self.painel_esquerdo,
            fg_color=BORDA_LOGIN,
            height=1,
            width=210
        )
        separador.pack(pady=(0, 20))

        ctk.CTkLabel(
            self.painel_esquerdo,
            text="Controle seu estoque.\nSimplifique sua gestao.",
            font=("Segoe UI", 13),
            text_color=CINZA,
            justify="center",
            wraplength=290
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            self.painel_esquerdo,
            text="SEGURO  /  ORGANIZADO  /  INTELIGENTE",
            font=("Segoe UI", 8, "bold"),
            text_color=CINZA_FRACO
        ).pack(side="bottom", pady=23)

        # Painel direito: formulário
        painel_direito = ctk.CTkFrame(
            principal,
            fg_color="transparent"
        )
        painel_direito.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(24, 14)
        )

        ctk.CTkLabel(
            painel_direito,
            text="ACESSO AO SISTEMA",
            font=("Segoe UI", 9, "bold"),
            text_color=CINZA_FRACO
        ).pack(
            anchor="w",
            pady=(47, 10)
        )

        self.titulo = ctk.CTkLabel(
            painel_direito,
            text="Bem-vindo de volta",
            font=("Segoe UI", 26, "bold"),
            text_color=BRANCO
        )
        self.titulo.pack(
            anchor="w",
            pady=(0, 7)
        )

        self.subtitulo = ctk.CTkLabel(
            painel_direito,
            text="Entre com suas credenciais para continuar.",
            font=("Segoe UI", 11),
            text_color=CINZA
        )
        self.subtitulo.pack(
            anchor="w",
            pady=(0, 27)
        )

        # Usuario
        ctk.CTkLabel(
            painel_direito,
            text="USUARIO",
            font=("Segoe UI", 10, "bold"),
            text_color="#C8CAD2"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.campo_usuario = ctk.CTkEntry(
            painel_direito,
            height=46,
            placeholder_text="Digite seu usuario",
            placeholder_text_color="#5F626C",
            border_color=BORDA_LOGIN,
            border_width=1,
            fg_color=CAMPO,
            text_color=BRANCO,
            corner_radius=9,
            font=("Segoe UI", 12)
        )
        self.campo_usuario.pack(
            fill="x",
            pady=(0, 19)
        )

        # Senha
        ctk.CTkLabel(
            painel_direito,
            text="SENHA",
            font=("Segoe UI", 10, "bold"),
            text_color="#C8CAD2"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.campo_senha = ctk.CTkEntry(
            painel_direito,
            height=46,
            placeholder_text="Digite sua senha",
            placeholder_text_color="#5F626C",
            show="*",
            border_color=BORDA_LOGIN,
            border_width=1,
            fg_color=CAMPO,
            text_color=BRANCO,
            corner_radius=9,
            font=("Segoe UI", 12)
        )
        self.campo_senha.pack(
            fill="x",
            pady=(0, 23)
        )

        # Botao principal
        self.botao_entrar = ctk.CTkButton(
            painel_direito,
            text="Entrar na plataforma",
            height=46,
            corner_radius=9,
            fg_color=AZUL_LOGIN,
            hover_color=AZUL_HOVER_LOGIN,
            text_color="#FFFFFF",
            font=("Segoe UI", 12, "bold"),
            command=self.entrar
        )
        self.botao_entrar.pack(
            fill="x",
            pady=(0, 13)
        )

        # Botao secundario
        self.botao_cadastro = ctk.CTkButton(
            painel_direito,
            text="Nao tem cadastro? Criar conta",
            height=40,
            corner_radius=9,
            fg_color="transparent",
            hover_color="#15161B",
            border_width=1,
            border_color=BORDA_LOGIN,
            text_color="#B7BBC6",
            font=("Segoe UI", 11),
            command=self.mostrar_cadastro
        )
        self.botao_cadastro.pack(fill="x")

        self.rodape = ctk.CTkLabel(
            painel_direito,
            text="Acesso protegido ao seu sistema de estoque",
            font=("Segoe UI", 9),
            text_color=CINZA_FRACO
        )
        self.rodape.pack(
            anchor="w",
            pady=(24, 0)
        )

        # Realce sutil ao focar nos campos
        self.campo_usuario.bind(
            "<FocusIn>",
            lambda evento: self.campo_usuario.configure(
                border_color=BORDA_FOCO
            )
        )
        self.campo_usuario.bind(
            "<FocusOut>",
            lambda evento: self.campo_usuario.configure(
                border_color=BORDA_LOGIN
            )
        )
        self.campo_senha.bind(
            "<FocusIn>",
            lambda evento: self.campo_senha.configure(
                border_color=BORDA_FOCO
            )
        )
        self.campo_senha.bind(
            "<FocusOut>",
            lambda evento: self.campo_senha.configure(
                border_color=BORDA_LOGIN
            )
        )

        self.bind("<Return>", lambda evento: self.acao_principal())

    # =====================================================
    # LOGIN / CADASTRO
    # =====================================================

    def acao_principal(self):
        if self.modo_cadastro:
            self.cadastrar()
        else:
            self.entrar()

    def mostrar_cadastro(self):
        self.modo_cadastro = True

        self.titulo.configure(text="Criar sua conta")
        self.subtitulo.configure(
            text="Preencha os dados para criar seu acesso."
        )

        self.botao_entrar.configure(
            text="Criar conta",
            command=self.cadastrar
        )

        self.botao_cadastro.configure(
            text="Ja tem cadastro? Voltar ao login",
            command=self.mostrar_login
        )

        self.campo_usuario.focus()

    def mostrar_login(self):
        self.modo_cadastro = False

        self.titulo.configure(text="Bem-vindo de volta")
        self.subtitulo.configure(
            text="Entre com suas credenciais para continuar."
        )

        self.botao_entrar.configure(
            text="Entrar na plataforma",
            command=self.entrar
        )

        self.botao_cadastro.configure(
            text="Nao tem cadastro? Criar conta",
            command=self.mostrar_cadastro
        )

        self.campo_senha.delete(0, "end")
        self.campo_usuario.focus()

    # =====================================================
    # CADASTRO
    # =====================================================

    def cadastrar(self):
        usuario = self.campo_usuario.get().strip()
        senha = self.campo_senha.get()

        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,100}", usuario):
            messagebox.showwarning(
                "Usuario invalido",
                "Use de 3 a 100 caracteres: letras sem acento, "
                "numeros, ponto, hifen ou sublinhado."
            )
            return

        if len(senha) < 8:
            messagebox.showwarning(
                "Senha fraca",
                "A senha precisa ter pelo menos 8 caracteres."
            )
            return

        if not self.verificar_banco():
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT id FROM usuarios_app WHERE usuario = %s",
                (usuario,)
            )

            if cursor.fetchone():
                messagebox.showwarning(
                    "Usuario existente",
                    "Esse nome de usuario ja esta cadastrado."
                )
                return

            senha_hash, salt = self.gerar_hash(senha)

            cursor.execute("""
                INSERT INTO usuarios_app
                    (usuario, senha_hash, salt)
                VALUES (%s, %s, %s)
            """, (usuario, senha_hash, salt))

            conexao.commit()

            messagebox.showinfo(
                "Cadastro concluido",
                "Conta criada com sucesso!\n\n"
                "Agora entre com seu usuario e senha."
            )

            self.mostrar_login()
            self.campo_usuario.delete(0, "end")
            self.campo_usuario.insert(0, usuario)
            self.campo_senha.delete(0, "end")

        except mysql.connector.IntegrityError:
            if conexao:
                conexao.rollback()

            messagebox.showwarning(
                "Usuario existente",
                "Esse usuario ja existe. Escolha outro nome."
            )

        except mysql.connector.Error as erro:
            if conexao:
                conexao.rollback()

            messagebox.showerror(
                "Erro no cadastro",
                f"Nao foi possivel criar a conta:\n{erro}"
            )

        finally:
            if cursor:
                cursor.close()

            if conexao and conexao.is_connected():
                conexao.close()

    # =====================================================
    # LOGIN
    # =====================================================

    def entrar(self):
        usuario = self.campo_usuario.get().strip()
        senha = self.campo_senha.get()

        if not usuario or not senha:
            messagebox.showwarning(
                "Campos obrigatorios",
                "Informe seu usuario e sua senha."
            )
            return

        if not self.verificar_banco():
            return

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, usuario, senha_hash, salt
                FROM usuarios_app
                WHERE usuario = %s
                LIMIT 1
            """, (usuario,))

            registro = cursor.fetchone()

            if not registro or not self.verificar_senha(
                senha,
                registro["salt"],
                registro["senha_hash"]
            ):
                messagebox.showerror(
                    "Acesso negado",
                    "Usuario ou senha incorretos."
                )
                return

            self.usuario_id = registro["id"]
            self.usuario_atual = registro["usuario"]
            self.papel_atual = "usuario"

            callback = self.ao_entrar

            if callback is None:
                messagebox.showinfo(
                    "Login realizado",
                    f"Bem-vindo, {self.usuario_atual}!"
                )
                return

            self.withdraw()

            try:
                callback(self.usuario_atual, self.papel_atual)
            except Exception as erro:
                self.deiconify()
                messagebox.showerror(
                    "Erro ao abrir o sistema",
                    "O login foi validado, mas o sistema principal "
                    f"nao abriu.\n\nDetalhes: {erro}"
                )
                return

            self.destroy()

        except mysql.connector.Error as erro:
            messagebox.showerror(
                "Erro de conexao",
                f"Nao foi possivel realizar o login:\n{erro}"
            )

        finally:
            if cursor:
                cursor.close()

            if conexao and conexao.is_connected():
                conexao.close()


if __name__ == "__main__":
    app = TelaLogin()

    if app.verificar_banco():
        app.mainloop()
    else:
        app.destroy()
