
import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

import theme
from database import conectar


def mostrar_auditoria(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    # Criar tabela adicional sem apagar dados existentes.
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria_estoque (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto_id INT NOT NULL,
                tipo VARCHAR(30) NOT NULL,
                quantidade INT NOT NULL,
                saldo_anterior INT NOT NULL,
                saldo_posterior INT NOT NULL,
                motivo VARCHAR(255) NOT NULL,
                usuario VARCHAR(100) DEFAULT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_auditoria_produto (produto_id)
            )
        """)
        conexao.commit()

    except Exception as erro:
        messagebox.showerror(
            "Erro",
            f"Não foi possível preparar a auditoria:\n{erro}"
        )
        return

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()

    # CABEÇALHO
    ctk.CTkLabel(
        app.conteudo,
        text="Auditoria e controle de perdas",
        font=("Segoe UI", 27, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=30, pady=(25, 5))

    ctk.CTkLabel(
        app.conteudo,
        text="Registre divergências, perdas e ajustes de inventário.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", padx=30, pady=(0, 20))

    # FORMULÁRIO
    formulario = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=14
    )
    formulario.pack(fill="x", padx=30, pady=(0, 18))

    ctk.CTkLabel(
        formulario,
        text="Registrar ajuste",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=18, pady=(16, 10))

    campo_produto = ctk.CTkEntry(
        formulario,
        placeholder_text="ID do produto",
        height=38
    )
    campo_produto.pack(fill="x", padx=18, pady=5)

    campo_tipo = ctk.CTkOptionMenu(
        formulario,
        values=["PERDA", "SOBRA", "AJUSTE"],
        height=38
    )
    campo_tipo.pack(fill="x", padx=18, pady=5)

    campo_quantidade = ctk.CTkEntry(
        formulario,
        placeholder_text="Quantidade (número inteiro positivo)",
        height=38
    )
    campo_quantidade.pack(fill="x", padx=18, pady=5)

    campo_motivo = ctk.CTkEntry(
        formulario,
        placeholder_text="Motivo obrigatório (ex.: produto danificado)",
        height=38
    )
    campo_motivo.pack(fill="x", padx=18, pady=5)

    ctk.CTkLabel(
        formulario,
        text=(
            "PERDA reduz o estoque; SOBRA aumenta o estoque; "
            "AJUSTE define uma nova quantidade total."
        ),
        text_color=theme.SECUNDARIO,
        font=("Segoe UI", 11),
        wraplength=850
    ).pack(anchor="w", padx=18, pady=(8, 12))

    # HISTÓRICO
    painel = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=14
    )
    painel.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    ctk.CTkLabel(
        painel,
        text="Histórico de auditoria",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=18, pady=(15, 8))

    historico = ctk.CTkScrollableFrame(
        painel,
        fg_color="transparent"
    )
    historico.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def carregar_historico():
        for widget in historico.winfo_children():
            widget.destroy()

        conexao_local = None
        cursor_local = None

        try:
            conexao_local = conectar()
            cursor_local = conexao_local.cursor()

            cursor_local.execute("""
                SELECT
                    a.id,
                    a.produto_id,
                    p.nome,
                    a.tipo,
                    a.quantidade,
                    a.saldo_anterior,
                    a.saldo_posterior,
                    a.motivo,
                    a.criado_em
                FROM auditoria_estoque a
                LEFT JOIN produtos p ON p.id = a.produto_id
                ORDER BY a.id DESC
                LIMIT 200
            """)

            registros = cursor_local.fetchall()

            if not registros:
                ctk.CTkLabel(
                    historico,
                    text="Nenhum ajuste registrado ainda.",
                    text_color=theme.SECUNDARIO
                ).pack(pady=20)
                return

            for registro in registros:
                (
                    identificador,
                    produto_id,
                    nome,
                    tipo,
                    quantidade,
                    anterior,
                    posterior,
                    motivo,
                    criado_em
                ) = registro

                linha = ctk.CTkFrame(
                    historico,
                    fg_color=theme.SIDEBAR,
                    corner_radius=8
                )
                linha.pack(fill="x", pady=4)

                ctk.CTkLabel(
                    linha,
                    text=f"#{identificador}  |  {nome or 'Produto removido'}",
                    font=("Segoe UI", 12, "bold"),
                    text_color=theme.TEXTO
                ).pack(anchor="w", padx=12, pady=(9, 2))

                ctk.CTkLabel(
                    linha,
                    text=(
                        f"{tipo} • Quantidade: {quantidade} • "
                        f"Saldo: {anterior} → {posterior}"
                    ),
                    font=("Segoe UI", 11),
                    text_color=theme.AMARELO
                ).pack(anchor="w", padx=12, pady=2)

                ctk.CTkLabel(
                    linha,
                    text=f"Motivo: {motivo} • Data: {criado_em}",
                    font=("Segoe UI", 10),
                    text_color=theme.SECUNDARIO,
                    wraplength=850,
                    justify="left"
                ).pack(anchor="w", padx=12, pady=(2, 9))

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar o histórico:\n{erro}"
            )

        finally:
            if cursor_local:
                cursor_local.close()
            if conexao_local and conexao_local.is_connected():
                conexao_local.close()

    def registrar_ajuste():
        conexao_local = None
        cursor_local = None

        try:
            produto_id = int(campo_produto.get().strip())
            quantidade = int(campo_quantidade.get().strip())
            tipo = campo_tipo.get()
            motivo = campo_motivo.get().strip()

            if produto_id <= 0 or quantidade <= 0:
                messagebox.showwarning(
                    "Dados inválidos",
                    "Informe um ID e uma quantidade maiores que zero."
                )
                return

            if not motivo:
                messagebox.showwarning(
                    "Motivo obrigatório",
                    "Informe o motivo do ajuste."
                )
                return

            conexao_local = conectar()
            conexao_local.start_transaction()
            cursor_local = conexao_local.cursor()

            cursor_local.execute("""
                SELECT quantidade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
            """, (produto_id,))

            produto = cursor_local.fetchone()

            if not produto:
                conexao_local.rollback()
                messagebox.showerror(
                    "Produto não encontrado",
                    "Confira o ID informado."
                )
                return

            anterior = int(produto[0])

            if tipo == "PERDA":
                if quantidade > anterior:
                    conexao_local.rollback()
                    messagebox.showwarning(
                        "Estoque insuficiente",
                        "A perda não pode ser maior que o estoque atual."
                    )
                    return
                posterior = anterior - quantidade

            elif tipo == "SOBRA":
                posterior = anterior + quantidade

            else:
                posterior = quantidade

            cursor.execute("""
                UPDATE produtos
                SET quantidade = %s
                WHERE id = %s
            """, (posterior, produto_id))

            cursor.execute("""
                INSERT INTO auditoria_estoque (
                    produto_id, tipo, quantidade,
                    saldo_anterior, saldo_posterior, motivo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                produto_id,
                tipo,
                quantidade,
                anterior,
                posterior,
                motivo
            ))

            conexao_local.commit()

            messagebox.showinfo(
                "Auditoria registrada",
                f"Estoque atualizado: {anterior} → {posterior}."
            )

            campo_produto.delete(0, "end")
            campo_quantidade.delete(0, "end")
            campo_motivo.delete(0, "end")

            carregar_historico()

        except ValueError:
            if conexao_local and conexao_local.is_connected():
                conexao_local.rollback()
            messagebox.showwarning(
                "Dados inválidos",
                "ID e quantidade precisam ser números inteiros."
            )

        except Exception as erro:
            if conexao_local and conexao_local.is_connected():
                conexao_local.rollback()
            messagebox.showerror(
                "Erro",
                f"Não foi possível registrar o ajuste:\n{erro}"
            )

        finally:
            if cursor_local:
                cursor_local.close()
            if conexao_local and conexao_local.is_connected():
                conexao_local.close()

    botoes = ctk.CTkFrame(
        formulario,
        fg_color="transparent"
    )
    botoes.pack(fill="x", padx=18, pady=(0, 16))

    ctk.CTkButton(
        botoes,
        text="Registrar ajuste",
        height=40,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        command=registrar_ajuste
    ).pack(side="left")

    ctk.CTkButton(
        botoes,
        text="Atualizar histórico",
        height=40,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        command=carregar_historico
    ).pack(side="left", padx=10)

    carregar_historico()
 