
import csv
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

import database
import theme


def mostrar_relatorios(app):
    # Limpa a tela anterior
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    movimentos_exportacao = []
    valores = {}

    # =====================================================
    # CABEÇALHO
    # =====================================================

    ctk.CTkLabel(
        app.conteudo,
        text="Relatórios",
        font=("Segoe UI", 30, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=24, pady=(22, 4))

    ctk.CTkLabel(
        app.conteudo,
        text="Acompanhe o estoque, consulte movimentações e exporte dados.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", padx=24, pady=(0, 18))

    # =====================================================
    # INDICADORES
    # =====================================================

    indicadores = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    indicadores.pack(fill="x", padx=18, pady=(0, 14))

    for coluna in range(3):
        indicadores.grid_columnconfigure(
            coluna,
            weight=1,
            uniform="indicador"
        )

    def criar_indicador(coluna, titulo, chave, cor):
        card = ctk.CTkFrame(
            indicadores,
            fg_color=theme.CARD,
            border_color=theme.BORDA,
            border_width=1,
            corner_radius=12
        )
        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=6,
            pady=4
        )

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 12),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", padx=14, pady=(14, 5))

        valores[chave] = ctk.CTkLabel(
            card,
            text="—",
            font=("Segoe UI", 23, "bold"),
            text_color=cor
        )
        valores[chave].pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

    criar_indicador(
        0, "Produtos cadastrados", "produtos", theme.AZUL
    )
    criar_indicador(
        1, "Unidades em estoque", "unidades", theme.CIANO
    )
    criar_indicador(
        2, "Valor total do estoque", "valor", theme.VERDE
    )

    # =====================================================
    # FILTROS
    # =====================================================

    filtros = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=12
    )
    filtros.pack(fill="x", padx=24, pady=(0, 14))

    ctk.CTkLabel(
        filtros,
        text="Filtrar movimentações por período",
        font=("Segoe UI", 15, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=14, pady=(12, 8))

    linha_filtros = ctk.CTkFrame(
        filtros,
        fg_color="transparent"
    )
    linha_filtros.pack(
        fill="x",
        padx=12,
        pady=(0, 12)
    )

    # Campo da data inicial
    grupo_inicio = ctk.CTkFrame(
        linha_filtros,
        fg_color="transparent"
    )
    grupo_inicio.pack(side="left", padx=5)

    ctk.CTkLabel(
        grupo_inicio,
        text="Data inicial",
        text_color=theme.SECUNDARIO
    ).pack(anchor="w")

    campo_inicio = ctk.CTkEntry(
        grupo_inicio,
        placeholder_text="AAAA-MM-DD",
        width=155,
        height=36
    )
    campo_inicio.pack(pady=(4, 0))

    # Campo da data final
    grupo_fim = ctk.CTkFrame(
        linha_filtros,
        fg_color="transparent"
    )
    grupo_fim.pack(side="left", padx=5)

    ctk.CTkLabel(
        grupo_fim,
        text="Data final",
        text_color=theme.SECUNDARIO
    ).pack(anchor="w")

    campo_fim = ctk.CTkEntry(
        grupo_fim,
        placeholder_text="AAAA-MM-DD",
        width=155,
        height=36
    )
    campo_fim.pack(pady=(4, 0))

    # =====================================================
    # ÁREA DE RESULTADOS
    # =====================================================

    resultados = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=12
    )
    resultados.pack(
        fill="both",
        expand=True,
        padx=24,
        pady=(0, 18)
    )

    ctk.CTkLabel(
        resultados,
        text="Resumo das movimentações",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=16, pady=(14, 8))

    resumo = ctk.CTkFrame(
        resultados,
        fg_color="transparent"
    )
    resumo.pack(fill="x", padx=12, pady=(0, 8))

    texto_entradas = ctk.CTkLabel(
        resumo,
        text="Entradas: —",
        font=("Segoe UI", 12, "bold"),
        text_color=theme.VERDE
    )
    texto_entradas.pack(side="left", padx=8)

    texto_saidas = ctk.CTkLabel(
        resumo,
        text="Saídas: —",
        font=("Segoe UI", 12, "bold"),
        text_color=theme.VERMELHO
    )
    texto_saidas.pack(side="left", padx=8)

    texto_baixo = ctk.CTkLabel(
        resumo,
        text="Estoque baixo: —",
        font=("Segoe UI", 12, "bold"),
        text_color=theme.AMARELO
    )
    texto_baixo.pack(side="left", padx=8)

    lista = ctk.CTkScrollableFrame(
        resultados,
        fg_color="transparent"
    )
    lista.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=(0, 10)
    )

    # =====================================================
    # VALIDAÇÃO DAS DATAS
    # =====================================================

    def obter_periodo():
        inicio = campo_inicio.get().strip()
        fim = campo_fim.get().strip()

        try:
            if inicio:
                datetime.strptime(inicio, "%Y-%m-%d")

            if fim:
                datetime.strptime(fim, "%Y-%m-%d")

        except ValueError:
            messagebox.showwarning(
                "Data inválida",
                "Digite as datas no formato AAAA-MM-DD.\n\n"
                "Exemplo: 2026-10-22",
                parent=app
            )
            return None

        if inicio and fim and inicio > fim:
            messagebox.showwarning(
                "Período inválido",
                "A data inicial não pode ser posterior à data final.",
                parent=app
            )
            return None

        return inicio, fim

    # =====================================================
    # GERAR RELATÓRIO
    # =====================================================

    def carregar_relatorio():
        nonlocal movimentos_exportacao

        periodo = obter_periodo()

        if periodo is None:
            return

        inicio, fim = periodo
        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            # Indicadores gerais do estoque
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(quantidade), 0),
                    COALESCE(SUM(quantidade * preco), 0)
                FROM produtos
            """)

            total_produtos, total_unidades, valor_estoque = (
                cursor.fetchone()
            )

            valores["produtos"].configure(
                text=str(total_produtos)
            )

            valores["unidades"].configure(
                text=str(total_unidades)
            )

            valor_formatado = (
                f"R$ {float(valor_estoque):,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            valores["valor"].configure(
                text=valor_formatado
            )

            # Produtos com estoque baixo
            cursor.execute("""
                SELECT COUNT(*)
                FROM produtos
                WHERE quantidade <= estoque_minimo
            """)

            estoque_baixo = cursor.fetchone()[0]

            texto_baixo.configure(
                text=f"Estoque baixo: {estoque_baixo}"
            )

            # Histórico de movimentações
            sql = """
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
                INNER JOIN produtos p
                    ON p.id = m.produto_id
                WHERE 1 = 1
            """

            parametros = []

            if inicio:
                sql += " AND m.criado_em >= %s"
                parametros.append(inicio + " 00:00:00")

            if fim:
                sql += " AND m.criado_em <= %s"
                parametros.append(fim + " 23:59:59")

            sql += " ORDER BY m.criado_em DESC, m.id DESC"

            cursor.execute(sql, tuple(parametros))
            movimentos_exportacao = cursor.fetchall()

            # Total de unidades movimentadas
            entradas = sum(
                int(movimento[3] or 0)
                for movimento in movimentos_exportacao
                if str(movimento[2]).upper() == "ENTRADA"
            )

            saidas = sum(
                int(movimento[3] or 0)
                for movimento in movimentos_exportacao
                if str(movimento[2]).upper() in ("SAIDA", "SAÍDA")
            )

            texto_entradas.configure(
                text=f"Entradas: {entradas}"
            )

            texto_saidas.configure(
                text=f"Saídas: {saidas}"
            )

            # Limpa o histórico anterior
            for widget in lista.winfo_children():
                widget.destroy()

            if not movimentos_exportacao:
                ctk.CTkLabel(
                    lista,
                    text="Nenhuma movimentação encontrada nesse período.",
                    font=("Segoe UI", 13),
                    text_color=theme.SECUNDARIO
                ).pack(anchor="w", padx=8, pady=16)

            else:
                for movimento in movimentos_exportacao:
                    (
                        id_movimento,
                        nome_produto,
                        tipo_movimento,
                        quantidade,
                        saldo_anterior,
                        saldo_posterior,
                        observacao,
                        criado_em
                    ) = movimento

                    if hasattr(criado_em, "strftime"):
                        data_texto = criado_em.strftime(
                            "%d/%m/%Y %H:%M"
                        )
                    else:
                        data_texto = str(criado_em or "")

                    tipo = str(tipo_movimento).upper()

                    if tipo in ("ENTRADA",):
                        cor = theme.VERDE
                    else:
                        cor = theme.VERMELHO

                    linha = ctk.CTkFrame(
                        lista,
                        fg_color=theme.CARD_HOVER,
                        corner_radius=9
                    )
                    linha.pack(fill="x", pady=3)

                    topo = ctk.CTkFrame(
                        linha,
                        fg_color="transparent"
                    )
                    topo.pack(
                        fill="x",
                        padx=12,
                        pady=(9, 3)
                    )

                    ctk.CTkLabel(
                        topo,
                        text=(
                            f"#{id_movimento}  •  "
                            f"{nome_produto}"
                        ),
                        font=("Segoe UI", 12, "bold"),
                        text_color=theme.TEXTO,
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)

                    ctk.CTkLabel(
                        topo,
                        text=f"{tipo}: {quantidade} un.",
                        font=("Segoe UI", 12, "bold"),
                        text_color=cor
                    ).pack(side="right", padx=(8, 0))

                    ctk.CTkLabel(
                        linha,
                        text=(
                            f"{data_texto}  •  "
                            f"Saldo: {saldo_anterior} → "
                            f"{saldo_posterior}  •  "
                            f"{observacao or 'Sem observação'}"
                        ),
                        font=("Segoe UI", 10),
                        text_color=theme.SECUNDARIO,
                        anchor="w",
                        justify="left",
                        wraplength=850
                    ).pack(
                        fill="x",
                        padx=12,
                        pady=(0, 9)
                    )

        except Exception as erro:
            messagebox.showerror(
                "Erro ao gerar relatório",
                "Não foi possível carregar os dados.\n\n"
                f"Detalhes: {erro}",
                parent=app
            )

        finally:
            if cursor:
                cursor.close()

            if conexao:
                conexao.close()

    # =====================================================
    # EXPORTAR CSV
    # =====================================================

    def exportar_csv():
        if not movimentos_exportacao:
            messagebox.showwarning(
                "Sem dados",
                "Não há movimentações para exportar. "
                "Clique em Gerar relatório primeiro.",
                parent=app
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar relatório",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfile="relatorio_movimentacoes.csv"
        )

        if not caminho:
            return

        try:
            with open(
                caminho,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as arquivo:

                escritor = csv.writer(
                    arquivo,
                    delimiter=";"
                )

                escritor.writerow([
                    "ID",
                    "Produto",
                    "Tipo",
                    "Quantidade",
                    "Saldo anterior",
                    "Saldo posterior",
                    "Observação",
                    "Data"
                ])

                for movimento in movimentos_exportacao:
                    escritor.writerow([
                        movimento[0],
                        movimento[1],
                        movimento[2],
                        movimento[3],
                        movimento[4],
                        movimento[5],
                        movimento[6] or "",
                        movimento[7]
                    ])

            messagebox.showinfo(
                "Exportação concluída",
                f"Relatório salvo em:\n{caminho}",
                parent=app
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro na exportação",
                f"Não foi possível salvar o arquivo.\n\n{erro}",
                parent=app
            )

    # =====================================================
    # BOTÕES — AGORA EM UMA LINHA VISÍVEL
    # =====================================================

    botoes = ctk.CTkFrame(
        linha_filtros,
        fg_color="transparent"
    )
    botoes.pack(
        side="left",
        padx=(16, 4),
        pady=(18, 0)
    )

    ctk.CTkButton(
        botoes,
        text="Gerar relatório",
        command=carregar_relatorio,
        height=36,
        width=145,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        font=("Segoe UI", 12, "bold")
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        botoes,
        text="Exportar CSV",
        command=exportar_csv,
        height=36,
        width=125,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        font=("Segoe UI", 12, "bold")
    ).pack(side="left")

    # Enter atualiza o relatório nos dois campos
    campo_inicio.bind(
        "<Return>",
        lambda evento: carregar_relatorio()
    )

    campo_fim.bind(
        "<Return>",
        lambda evento: carregar_relatorio()
    )

    # Carrega os dados ao entrar na página
    carregar_relatorio()
