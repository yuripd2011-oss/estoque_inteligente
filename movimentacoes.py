
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

import theme
import database


def mostrar_movimentacoes(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    produtos_disponiveis = {}

    # ==============================================
    # CABEÇALHO
    # ==============================================

    ctk.CTkLabel(
        app.conteudo,
        text="Entradas e saídas",
        font=("Segoe UI", 30, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        app.conteudo,
        text="Registre movimentações e acompanhe o histórico do estoque.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(4, 20))

    # ==============================================
    # FORMULÁRIO
    # ==============================================

    formulario = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=14
    )
    formulario.pack(fill="x", pady=(0, 18))

    ctk.CTkLabel(
        formulario,
        text="Nova movimentação",
        font=("Segoe UI", 18, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=18, pady=(16, 12))

    campos = ctk.CTkFrame(formulario, fg_color="transparent")
    campos.pack(fill="x", padx=12)

    for coluna in range(2):
        campos.grid_columnconfigure(coluna, weight=1, uniform="campos")

    ctk.CTkLabel(
        campos,
        text="Produto",
        text_color=theme.SECUNDARIO
    ).grid(row=0, column=0, sticky="w", padx=6, pady=(0, 5))

    seletor_produto = ctk.CTkComboBox(
        campos,
        values=["Carregando produtos..."],
        height=40,
        state="readonly",
        fg_color=theme.FUNDO,
        border_color=theme.BORDA,
        button_color=theme.AZUL,
        text_color=theme.TEXTO
    )
    seletor_produto.grid(
        row=1, column=0, sticky="ew", padx=6, pady=(0, 14)
    )

    ctk.CTkLabel(
        campos,
        text="Tipo de movimentação",
        text_color=theme.SECUNDARIO
    ).grid(row=0, column=1, sticky="w", padx=6, pady=(0, 5))

    seletor_tipo = ctk.CTkSegmentedButton(
        campos,
        values=["ENTRADA", "SAIDA"],
        selected_color=theme.AZUL,
        selected_hover_color=theme.AZUL_HOVER,
        unselected_color=theme.SIDEBAR,
        text_color=theme.TEXTO,
        height=40
    )
    seletor_tipo.grid(
        row=1, column=1, sticky="ew", padx=6, pady=(0, 14)
    )
    seletor_tipo.set("ENTRADA")

    ctk.CTkLabel(
        campos,
        text="Quantidade",
        text_color=theme.SECUNDARIO
    ).grid(row=2, column=0, sticky="w", padx=6, pady=(0, 5))

    campo_quantidade = ctk.CTkEntry(
        campos,
        placeholder_text="Informe uma quantidade inteira",
        height=40,
        fg_color=theme.FUNDO,
        border_color=theme.BORDA,
        text_color=theme.TEXTO
    )
    campo_quantidade.grid(
        row=3, column=0, sticky="ew", padx=6, pady=(0, 14)
    )

    ctk.CTkLabel(
        campos,
        text="Observação",
        text_color=theme.SECUNDARIO
    ).grid(row=2, column=1, sticky="w", padx=6, pady=(0, 5))

    campo_observacao = ctk.CTkEntry(
        campos,
        placeholder_text="Ex.: compra, venda, avaria...",
        height=40,
        fg_color=theme.FUNDO,
        border_color=theme.BORDA,
        text_color=theme.TEXTO
    )
    campo_observacao.grid(
        row=3, column=1, sticky="ew", padx=6, pady=(0, 14)
    )

    # ==============================================
    # HISTÓRICO
    # ==============================================

    painel_historico = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=14
    )
    painel_historico.pack(fill="both", expand=True)

    topo_historico = ctk.CTkFrame(
        painel_historico,
        fg_color="transparent"
    )
    topo_historico.pack(fill="x", padx=16, pady=14)

    ctk.CTkLabel(
        topo_historico,
        text="Histórico recente",
        font=("Segoe UI", 18, "bold"),
        text_color=theme.TEXTO
    ).pack(side="left")

    # ==============================================
    # ATUALIZAR LISTA DE PRODUTOS
    # ==============================================

    def carregar_produtos():
        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT id, nome, quantidade
                FROM produtos
                ORDER BY nome
            """)

            produtos = cursor.fetchall()
            produtos_disponiveis.clear()

            opcoes = []

            for produto_id, nome, quantidade in produtos:
                texto = f"#{produto_id} - {nome} | estoque: {quantidade}"
                produtos_disponiveis[texto] = produto_id
                opcoes.append(texto)

            seletor_produto.configure(
                values=opcoes if opcoes else ["Nenhum produto cadastrado"]
            )

            if opcoes:
                seletor_produto.set(opcoes[0])
            else:
                seletor_produto.set("Nenhum produto cadastrado")

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os produtos.\n\n{erro}"
            )
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    # ==============================================
    # REGISTRAR MOVIMENTAÇÃO
    # ==============================================

    def registrar_movimentacao():
        produto_id = produtos_disponiveis.get(seletor_produto.get())

        if produto_id is None:
            messagebox.showwarning(
                "Atenção",
                "Cadastre ou selecione um produto primeiro."
            )
            return

        try:
            quantidade = int(campo_quantidade.get().strip())
            if quantidade <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Quantidade inválida",
                "Informe uma quantidade inteira maior que zero."
            )
            campo_quantidade.focus()
            return

        tipo = seletor_tipo.get()

        if tipo not in ("ENTRADA", "SAIDA"):
            messagebox.showwarning(
                "Tipo inválido",
                "Selecione ENTRADA ou SAIDA."
            )
            return

        observacao = campo_observacao.get().strip()

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            conexao.start_transaction()
            cursor = conexao.cursor()

            # Bloqueia a linha durante a operação para reduzir
            # o risco de duas movimentações alterarem o mesmo saldo.
            cursor.execute(
                """
                SELECT quantidade
                FROM produtos
                WHERE id = %s
                FOR UPDATE
                """,
                (produto_id,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError("O produto selecionado não existe mais.")

            saldo_anterior = int(resultado[0])

            if tipo == "ENTRADA":
                saldo_posterior = saldo_anterior + quantidade
            else:
                if quantidade > saldo_anterior:
                    raise ValueError(
                        f"Estoque insuficiente!\n\n"
                        f"Disponível: {saldo_anterior} unidade(s).\n"
                        f"Solicitado: {quantidade} unidade(s)."
                    )

                saldo_posterior = saldo_anterior - quantidade

            cursor.execute(
                """
                UPDATE produtos
                SET quantidade = %s
                WHERE id = %s
                """,
                (saldo_posterior, produto_id)
            )

            cursor.execute(
                """
                INSERT INTO movimentacoes
                (
                    produto_id,
                    tipo,
                    quantidade,
                    saldo_anterior,
                    saldo_posterior,
                    observacao,
                    criado_em
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    produto_id,
                    tipo,
                    quantidade,
                    saldo_anterior,
                    saldo_posterior,
                    observacao,
                    datetime.now()
                )
            )

            conexao.commit()

            campo_quantidade.delete(0, "end")
            campo_observacao.delete(0, "end")

            carregar_produtos()
            carregar_historico()

            messagebox.showinfo(
                "Movimentação registrada",
                f"Tipo: {tipo}\n"
                f"Quantidade: {quantidade}\n"
                f"Saldo anterior: {saldo_anterior}\n"
                f"Saldo atual: {saldo_posterior}"
            )

        except Exception as erro:
            if conexao:
                conexao.rollback()

            messagebox.showerror(
                "Não foi possível registrar",
                str(erro)
            )

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    botao_registrar = ctk.CTkButton(
        formulario,
        text="Registrar movimentação",
        height=42,
        corner_radius=10,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        font=("Segoe UI", 13, "bold"),
        command=registrar_movimentacao
    )
    botao_registrar.pack(anchor="w", padx=18, pady=(0, 17))

    # ==============================================
    # EXIBIR HISTÓRICO
    # ==============================================

    lista_historico = ctk.CTkScrollableFrame(
        painel_historico,
        fg_color="transparent",
        corner_radius=0
    )
    lista_historico.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def carregar_historico():
        for widget in lista_historico.winfo_children():
            widget.destroy()

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    m.id,
                    p.nome,
                    m.tipo,
                    m.quantidade,
                    m.saldo_anterior,
                    m.saldo_posterior,
                    m.observacao,
                    m.criado_em
                FROM movimentacoes m
                INNER JOIN produtos p ON p.id = m.produto_id
                ORDER BY m.id DESC
                LIMIT 100
            """)

            movimentos = cursor.fetchall()

            if not movimentos:
                ctk.CTkLabel(
                    lista_historico,
                    text="Nenhuma movimentação registrada ainda.",
                    text_color=theme.SECUNDARIO
                ).pack(pady=22)
                return

            for mov in movimentos:
                (
                    mov_id, nome, tipo, qtd,
                    anterior, posterior, observacao, data
                ) = mov

                entrada = tipo == "ENTRADA"
                cor = theme.VERDE if entrada else theme.VERMELHO
                sinal = "+" if entrada else "-"

                linha = ctk.CTkFrame(
                    lista_historico,
                    fg_color=theme.CARD_HOVER,
                    corner_radius=9
                )
                linha.pack(fill="x", pady=4)

                topo = ctk.CTkFrame(
                    linha,
                    fg_color="transparent"
                )
                topo.pack(fill="x", padx=12, pady=(10, 3))

                ctk.CTkLabel(
                    topo,
                    text=f"{sinal}{qtd}  {nome}",
                    font=("Segoe UI", 12, "bold"),
                    text_color=cor
                ).pack(side="left")

                ctk.CTkLabel(
                    topo,
                    text=tipo,
                    font=("Segoe UI", 10, "bold"),
                    text_color=cor
                ).pack(side="right")

                data_texto = (
                    data.strftime("%d/%m/%Y %H:%M")
                    if hasattr(data, "strftime")
                    else str(data or "")
                )

                detalhe = (
                    f"Mov. #{mov_id}  •  {data_texto}  •  "
                    f"Saldo: {anterior} → {posterior}"
                )

                if observacao:
                    detalhe += f"  •  {observacao}"

                ctk.CTkLabel(
                    linha,
                    text=detalhe,
                    font=("Segoe UI", 10),
                    text_color=theme.SECUNDARIO,
                    anchor="w",
                    wraplength=900,
                    justify="left"
                ).pack(fill="x", padx=12, pady=(0, 10))

        except Exception as erro:
            ctk.CTkLabel(
                lista_historico,
                text=f"Erro ao carregar histórico:\n{erro}",
                text_color=theme.VERMELHO,
                wraplength=800,
                justify="left"
            ).pack(anchor="w", padx=10, pady=15)
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    carregar_produtos()
    carregar_historico()
