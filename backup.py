
import customtkinter as ctk
import mysql.connector
import subprocess
import shutil
import os
from datetime import datetime
from tkinter import filedialog, messagebox

import theme
from database import DB_CONFIG


def mostrar_backup(app):
    """
    Tela de backup do banco de dados.
    Usa mysqldump quando disponível no computador.
    """

    for widget in app.conteudo.winfo_children():
        widget.destroy()

    principal = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    principal.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=25
    )

    ctk.CTkLabel(
        principal,
        text="Backup e segurança",
        font=("Segoe UI", 27, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        principal,
        text="Crie cópias de segurança do banco de dados.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(5, 22))

    card = ctk.CTkFrame(
        principal,
        fg_color=theme.CARD,
        corner_radius=14,
        border_width=1,
        border_color=theme.BORDA
    )
    card.pack(fill="x", pady=(0, 18))

    ctk.CTkLabel(
        card,
        text="Cópia de segurança do MySQL",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=20, pady=(20, 8))

    ctk.CTkLabel(
        card,
        text=(
            "O backup será salvo em um arquivo SQL contendo "
            "a estrutura e os dados das tabelas."
        ),
        font=("Segoe UI", 12),
        text_color=theme.SECUNDARIO,
        wraplength=650,
        justify="left"
    ).pack(anchor="w", padx=20, pady=(0, 20))

    status = ctk.CTkLabel(
        principal,
        text="Pronto para criar um backup.",
        font=("Segoe UI", 12),
        text_color=theme.SECUNDARIO
    )
    status.pack(anchor="w", pady=10)

    def localizar_mysqldump():
        """
        Procura mysqldump no PATH e em diretórios comuns.
        """

        encontrado = shutil.which("mysqldump")

        if encontrado:
            return encontrado

        caminhos = [
            r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
            r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe",
            r"C:\xampp\mysql\bin\mysqldump.exe",
            r"C:\wamp64\bin\mysql\mysql8.0.31\bin\mysqldump.exe",
        ]

        for caminho in caminhos:
            if os.path.isfile(caminho):
                return caminho

        return None

    def criar_backup():
        destino = filedialog.asksaveasfilename(
            parent=app,
            title="Salvar backup do banco",
            defaultextension=".sql",
            initialfile=(
                "backup_estoque_inteligente_"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".sql"
            ),
            filetypes=[
                ("Arquivo SQL", "*.sql"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not destino:
            return

        mysqldump = localizar_mysqldump()

        if not mysqldump:
            messagebox.showerror(
                "MySQL não encontrado",
                "Não encontrei o programa mysqldump.\n\n"
                "Instale ou localize as ferramentas do MySQL "
                "e tente novamente."
            )
            return

        status.configure(
            text="Criando backup... aguarde.",
            text_color=theme.AZUL
        )
        app.update_idletasks()

        comando = [
            mysqldump,
            "--host=" + str(DB_CONFIG["host"]),
            "--port=" + str(DB_CONFIG["port"]),
            "--user=" + str(DB_CONFIG["user"]),
            "--default-character-set=utf8mb4",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--databases",
            str(DB_CONFIG["database"]),
        ]

        # Não coloca a senha na linha de comando.
        # Se o banco usar senha, o utilitário poderá solicitá-la.
        if DB_CONFIG.get("password"):
            comando.append("--password=" + DB_CONFIG["password"])

        try:
            with open(destino, "wb") as arquivo:
                resultado = subprocess.run(
                    comando,
                    stdout=arquivo,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    check=False
                )

            if resultado.returncode != 0:
                try:
                    os.remove(destino)
                except OSError:
                    pass

                erro = resultado.stderr.decode(
                    "utf-8",
                    errors="replace"
                )

                status.configure(
                    text="Falha ao criar o backup.",
                    text_color=theme.VERMELHO
                )

                messagebox.showerror(
                    "Erro no backup",
                    "O MySQL não conseguiu gerar o backup:\n\n"
                    + erro[:1800]
                )
                return

            tamanho = os.path.getsize(destino)

            if tamanho == 0:
                os.remove(destino)
                raise RuntimeError(
                    "O arquivo de backup ficou vazio."
                )

            status.configure(
                text="Backup criado com sucesso!",
                text_color=theme.VERDE
            )

            messagebox.showinfo(
                "Backup concluído",
                f"Arquivo salvo em:\n{destino}\n\n"
                f"Tamanho: {tamanho / 1024:.1f} KB"
            )

        except (OSError, subprocess.TimeoutExpired, RuntimeError) as erro:
            status.configure(
                text="Não foi possível concluir o backup.",
                text_color=theme.VERMELHO
            )

            messagebox.showerror(
                "Erro",
                f"Não foi possível criar o backup:\n{erro}"
            )

    ctk.CTkButton(
        card,
        text="Criar backup agora",
        height=44,
        corner_radius=10,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        font=("Segoe UI", 13, "bold"),
        command=criar_backup
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 20)
    )

    ctk.CTkLabel(
        principal,
        text=(
            "Importante: guarde os backups em um local seguro. "
            "Ainda não há agendamento automático configurado."
        ),
        font=("Segoe UI", 11),
        text_color=theme.SECUNDARIO,
        wraplength=700,
        justify="left"
    ).pack(anchor="w", pady=10)
