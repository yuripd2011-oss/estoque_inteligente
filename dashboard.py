
import customtkinter as ctk
import mysql.connector

from datetime import date, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

import theme


# =========================================================
# ESTOQUE INTELIGENTE ULTIMATE — OBSIDIAN
# Dashboard dark premium
# =========================================================

PRETO = "#050505"
FUNDO = "#080808"
PAINEL = "#0B0B0D"
PAINEL_ALT = "#0E0E12"
CAMPO = "#09090B"
BORDA = "#1B1B20"
BORDA_SUAVE = "#151519"

BRANCO = "#F5F5F7"
CINZA = "#92929B"
CINZA_FRACO = "#62626D"

AZUL = "#3B82F6"
CIANO = "#22D3EE"
ROXO = "#A78BFA"
VERDE = "#34D399"
VERMELHO = "#FB7185"
AMARELO = "#FBBF24"

CORES_ROSCA = [
    "#4389FF",
    "#22D3EE",
    "#A78BFA",
    "#34D399",
    "#FBBF24",
    "#F472B6",
    "#FB923C",
]


# =========================================================
# BANCO DE DADOS
# =========================================================

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3307,
        database="estoque_inteligente"
    )


def buscar_indicadores():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                COUNT(*) AS produtos,
                COALESCE(SUM(quantidade), 0) AS unidades,
                COALESCE(SUM(quantidade * preco), 0) AS valor,
                COALESCE(
                    SUM(
                        CASE
                            WHEN quantidade <= estoque_minimo THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS estoque_baixo
            FROM produtos
        """)

        indicadores = cursor.fetchone()

        cursor.execute("""
            SELECT
                COALESCE(categoria, 'Sem categoria') AS categoria,
                SUM(quantidade) AS total
            FROM produtos
            GROUP BY categoria
            ORDER BY total DESC
            LIMIT 7
        """)

        categorias = cursor.fetchall()

        cursor.execute("""
            SELECT
                DATE(criado_em) AS dia,
                tipo,
                SUM(quantidade) AS total
            FROM movimentacoes
            WHERE criado_em >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)
              AND criado_em < DATE_ADD(CURDATE(), INTERVAL 1 DAY)
            GROUP BY DATE(criado_em), tipo
            ORDER BY dia
        """)

        movimentacoes = cursor.fetchall()

        cursor.execute("""
            SELECT
                p.nome,
                m.tipo,
                m.quantidade,
                m.criado_em
            FROM movimentacoes m
            INNER JOIN produtos p ON p.id = m.produto_id
            ORDER BY m.criado_em DESC, m.id DESC
            LIMIT 7
        """)

        recentes = cursor.fetchall()

        return indicadores, categorias, movimentacoes, recentes

    except mysql.connector.Error as erro:
        print(f"Erro no dashboard: {erro}")
        return None

    finally:
        if cursor:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


# =========================================================
# FORMATACAO
# =========================================================

def formatar_moeda(valor):
    valor = float(valor or 0)

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def criar_rotulo(pai, texto, tamanho=12, cor=BRANCO,
                 negrito=False, **kwargs):
    return ctk.CTkLabel(
        pai,
        text=texto,
        font=(
            "Segoe UI",
            tamanho,
            "bold" if negrito else "normal"
        ),
        text_color=cor,
        **kwargs
    )


# =========================================================
# CARD DE INDICADOR
# =========================================================

def criar_card(pai, titulo, numero, cor, icone, descricao):
    card = ctk.CTkFrame(
        pai,
        fg_color=PAINEL,
        corner_radius=15,
        border_width=1,
        border_color=BORDA
    )

    card.grid_columnconfigure(0, weight=1)

    topo = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )
    topo.pack(
        fill="x",
        padx=17,
        pady=(17, 11)
    )

    icone_box = ctk.CTkFrame(
        topo,
        fg_color=PAINEL_ALT,
        corner_radius=9,
        width=37,
        height=37,
        border_width=1,
        border_color=BORDA_SUAVE
    )
    icone_box.pack(side="left")
    icone_box.pack_propagate(False)

    criar_rotulo(
        icone_box,
        icone,
        tamanho=17,
        cor=cor,
        negrito=True
    ).place(relx=0.5, rely=0.5, anchor="center")

    criar_rotulo(
        topo,
        titulo,
        tamanho=10,
        cor=CINZA,
        negrito=True
    ).pack(
        side="left",
        padx=(10, 0)
    )

    criar_rotulo(
        card,
        str(numero),
        tamanho=24 if len(str(numero)) < 14 else 19,
        cor=BRANCO,
        negrito=True
    ).pack(
        anchor="w",
        padx=17,
        pady=(0, 5)
    )

    criar_rotulo(
        card,
        descricao,
        tamanho=10,
        cor=CINZA_FRACO
    ).pack(
        anchor="w",
        padx=17,
        pady=(0, 15)
    )

    ctk.CTkFrame(
        card,
        fg_color=cor,
        height=2,
        corner_radius=1
    ).pack(
        fill="x",
        padx=17,
        pady=(0, 15)
    )

    return card


# =========================================================
# PAINEL DOS GRAFICOS
# =========================================================

def criar_card_grafico(pai, titulo, descricao, identificador):
    card = ctk.CTkFrame(
        pai,
        fg_color=PAINEL,
        corner_radius=15,
        border_width=1,
        border_color=BORDA
    )

    cabecalho = ctk.CTkFrame(
        card,
        fg_color="transparent"
    )
    cabecalho.pack(
        fill="x",
        padx=19,
        pady=(17, 0)
    )

    linha_titulo = ctk.CTkFrame(
        cabecalho,
        fg_color="transparent"
    )
    linha_titulo.pack(fill="x")

    criar_rotulo(
        linha_titulo,
        titulo,
        tamanho=14,
        cor=BRANCO,
        negrito=True
    ).pack(side="left")

    criar_rotulo(
        linha_titulo,
        identificador,
        tamanho=9,
        cor=CINZA_FRACO,
        negrito=True
    ).pack(side="right")

    criar_rotulo(
        cabecalho,
        descricao,
        tamanho=10,
        cor=CINZA
    ).pack(
        anchor="w",
        pady=(5, 0)
    )

    return card


# =========================================================
# GRAFICO DE ROSCA
# =========================================================

def desenhar_grafico_rosca(card, categorias):
    figura = Figure(
        figsize=(5, 3.0),
        dpi=100,
        facecolor=PAINEL
    )

    eixo = figura.add_subplot(111)
    eixo.set_facecolor(PAINEL)

    dados = []

    for item in categorias:
        nome = str(item["categoria"] or "Sem categoria")
        valor = max(0, float(item["total"] or 0))

        if valor > 0:
            dados.append((nome, valor))

    if not dados:
        eixo.text(
            0.5,
            0.5,
            "Nenhum estoque para exibir",
            ha="center",
            va="center",
            color=CINZA,
            fontsize=10,
            transform=eixo.transAxes
        )
        eixo.set_axis_off()

    else:
        nomes = [item[0] for item in dados]
        valores = [item[1] for item in dados]

        cores = [
            CORES_ROSCA[i % len(CORES_ROSCA)]
            for i in range(len(valores))
        ]

        fatias, _ = eixo.pie(
            valores,
            startangle=90,
            counterclock=False,
            colors=cores,
            wedgeprops={
                "width": 0.27,
                "edgecolor": PAINEL,
                "linewidth": 3
            }
        )

        total = sum(valores)

        eixo.text(
            0,
            0.07,
            f"{total:,.0f}".replace(",", "."),
            ha="center",
            va="center",
            fontsize=21,
            fontweight="bold",
            color=BRANCO
        )

        eixo.text(
            0,
            -0.17,
            "UNIDADES",
            ha="center",
            va="center",
            fontsize=8,
            color=CINZA
        )

        legenda = [
            f"{nome[:16]} · {valor:,.0f}".replace(",", ".")
            for nome, valor in zip(nomes, valores)
        ]

        eixo.legend(
            fatias,
            legenda,
            loc="center left",
            bbox_to_anchor=(0.89, 0.5),
            frameon=False,
            labelcolor=BRANCO,
            fontsize=8,
            handlelength=1,
            handletextpad=0.7,
            labelspacing=1.2,
            borderaxespad=0
        )

        eixo.set_aspect("equal")

    figura.subplots_adjust(
        left=0.01,
        right=0.99,
        top=0.96,
        bottom=0.04
    )

    canvas = FigureCanvasTkAgg(figura, master=card)
    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=8,
        pady=(7, 12)
    )


# =========================================================
# GRAFICO DE ENTRADAS E SAIDAS
# =========================================================

def desenhar_grafico_movimentacoes(card, movimentacoes):
    dias = [
        date.today() - timedelta(days=i)
        for i in range(6, -1, -1)
    ]

    entradas = {dia: 0 for dia in dias}
    saidas = {dia: 0 for dia in dias}

    for item in movimentacoes:
        dia = item["dia"]

        if hasattr(dia, "date"):
            dia = dia.date()

        tipo = str(item["tipo"] or "").upper()
        total = int(item["total"] or 0)

        if dia in entradas and tipo == "ENTRADA":
            entradas[dia] = total
        elif dia in saidas and tipo == "SAIDA":
            saidas[dia] = total

    nomes_dias = [dia.strftime("%d/%m") for dia in dias]
    valores_entrada = [entradas[dia] for dia in dias]
    valores_saida = [saidas[dia] for dia in dias]

    figura = Figure(
        figsize=(5, 3.0),
        dpi=100,
        facecolor=PAINEL
    )

    eixo = figura.add_subplot(111)
    eixo.set_facecolor(PAINEL)

    posicoes = list(range(7))
    largura = 0.30

    barras_entrada = eixo.bar(
        [p - largura / 2 for p in posicoes],
        valores_entrada,
        width=largura,
        color=AZUL,
        label="Entradas",
        zorder=3,
        edgecolor="none"
    )

    barras_saida = eixo.bar(
        [p + largura / 2 for p in posicoes],
        valores_saida,
        width=largura,
        color=ROXO,
        label="Saídas",
        zorder=3,
        edgecolor="none"
    )

    eixo.set_xticks(posicoes)
    eixo.set_xticklabels(nomes_dias)

    eixo.grid(
        axis="y",
        color=BORDA,
        linewidth=0.7,
        alpha=0.85
    )
    eixo.set_axisbelow(True)

    eixo.tick_params(
        axis="x",
        colors=CINZA,
        labelsize=8,
        length=0,
        pad=9
    )

    eixo.tick_params(
        axis="y",
        colors=CINZA_FRACO,
        labelsize=8,
        length=0
    )

    eixo.yaxis.set_major_locator(
        MaxNLocator(nbins=4, integer=True)
    )

    for lado in ["top", "right", "left"]:
        eixo.spines[lado].set_visible(False)

    eixo.spines["bottom"].set_color(BORDA)

    maior = max(
        max(valores_entrada, default=0),
        max(valores_saida, default=0)
    )

    eixo.set_ylim(0, maior * 1.3 if maior > 0 else 1)

    for barras in [barras_entrada, barras_saida]:
        for barra in barras:
            altura = barra.get_height()

            if altura > 0:
                eixo.annotate(
                    str(int(altura)),
                    (
                        barra.get_x() + barra.get_width() / 2,
                        altura
                    ),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color=BRANCO,
                    fontsize=8,
                    fontweight="bold"
                )

    legenda = eixo.legend(
        loc="upper left",
        frameon=False,
        ncol=2,
        fontsize=8,
        handlelength=1.2,
        columnspacing=1.4
    )

    for texto in legenda.get_texts():
        texto.set_color(CINZA)

    figura.subplots_adjust(
        left=0.09,
        right=0.97,
        top=0.91,
        bottom=0.17
    )

    canvas = FigureCanvasTkAgg(figura, master=card)
    canvas.draw()

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(7, 12)
    )


# =========================================================
# HISTORICO RECENTE
# =========================================================

def criar_historico(pai, recentes):
    historico = ctk.CTkFrame(
        pai,
        fg_color=PAINEL,
        corner_radius=15,
        border_width=1,
        border_color=BORDA
    )

    topo = ctk.CTkFrame(
        historico,
        fg_color="transparent"
    )
    topo.pack(
        fill="x",
        padx=18,
        pady=(16, 12)
    )

    criar_rotulo(
        topo,
        "Atividade recente",
        tamanho=14,
        cor=BRANCO,
        negrito=True
    ).pack(side="left")

    criar_rotulo(
        topo,
        "ULTIMOS 7 REGISTROS",
        tamanho=9,
        cor=CINZA_FRACO,
        negrito=True
    ).pack(side="right")

    if not recentes:
        criar_rotulo(
            historico,
            "Nenhuma movimentação registrada.",
            tamanho=11,
            cor=CINZA
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 18)
        )

        return historico

    for indice, item in enumerate(recentes):
        tipo = str(item["tipo"] or "").upper()
        entrada = tipo == "ENTRADA"

        cor = VERDE if entrada else VERMELHO
        sinal = "+" if entrada else "−"

        linha = ctk.CTkFrame(
            historico,
            fg_color=CAMPO if indice % 2 == 0 else "transparent",
            corner_radius=8
        )
        linha.pack(
            fill="x",
            padx=10,
            pady=(0, 4)
        )

        simbolo = ctk.CTkFrame(
            linha,
            fg_color="#102019" if entrada else "#211015",
            corner_radius=8,
            width=34,
            height=34
        )
        simbolo.pack(
            side="left",
            padx=(9, 10),
            pady=7
        )
        simbolo.pack_propagate(False)

        criar_rotulo(
            simbolo,
            sinal,
            tamanho=17,
            cor=cor,
            negrito=True
        ).place(relx=0.5, rely=0.5, anchor="center")

        centro = ctk.CTkFrame(
            linha,
            fg_color="transparent"
        )
        centro.pack(
            side="left",
            fill="x",
            expand=True,
            pady=7
        )

        criar_rotulo(
            centro,
            str(item["nome"]),
            tamanho=11,
            cor=BRANCO,
            negrito=True
        ).pack(anchor="w")

        data = item["criado_em"]
        data_formatada = (
            data.strftime("%d/%m/%Y %H:%M")
            if data else "—"
        )

        criar_rotulo(
            centro,
            data_formatada,
            tamanho=9,
            cor=CINZA
        ).pack(anchor="w", pady=(2, 0))

        criar_rotulo(
            linha,
            f"{sinal}{item['quantidade']} un.",
            tamanho=11,
            cor=cor,
            negrito=True
        ).pack(side="right", padx=16)

        criar_rotulo(
            linha,
            "ENTRADA" if entrada else "SAÍDA",
            tamanho=9,
            cor=cor,
            negrito=True
        ).pack(side="right", padx=8)

    return historico


# =========================================================
# DASHBOARD PRINCIPAL
# =========================================================

def mostrar_dashboard(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    app.conteudo.configure(fg_color=PRETO)

    # Cabeçalho principal
    cabecalho = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    cabecalho.pack(
        fill="x",
        pady=(0, 22)
    )

    titulo_linha = ctk.CTkFrame(
        cabecalho,
        fg_color="transparent"
    )
    titulo_linha.pack(fill="x")

    criar_rotulo(
        titulo_linha,
        "Dashboard",
        tamanho=29,
        cor=BRANCO,
        negrito=True
    ).pack(side="left")

    status = ctk.CTkFrame(
        titulo_linha,
        fg_color="#0C1712",
        corner_radius=7,
        border_width=1,
        border_color="#193A2B"
    )
    status.pack(
        side="right",
        pady=(8, 0)
    )

    criar_rotulo(
        status,
        "●  SISTEMA CONECTADO",
        tamanho=9,
        cor=VERDE,
        negrito=True
    ).pack(padx=10, pady=7)

    criar_rotulo(
        cabecalho,
        "Resumo operacional e acompanhamento do inventário.",
        tamanho=11,
        cor=CINZA
    ).pack(anchor="w", pady=(5, 0))

    resultado = buscar_indicadores()

    if resultado is None:
        erro_card = ctk.CTkFrame(
            app.conteudo,
            fg_color=PAINEL,
            corner_radius=12,
            border_width=1,
            border_color=BORDA
        )
        erro_card.pack(fill="x", pady=10)

        criar_rotulo(
            erro_card,
            "Não foi possível carregar os dados do dashboard.",
            tamanho=13,
            cor=VERMELHO,
            negrito=True
        ).pack(anchor="w", padx=18, pady=(16, 6))

        criar_rotulo(
            erro_card,
            "Confira a conexão com o MySQL e veja a mensagem no terminal.",
            tamanho=11,
            cor=CINZA
        ).pack(anchor="w", padx=18, pady=(0, 16))

        return

    indicadores, categorias, movimentacoes, recentes = resultado

    # Indicadores
    linha_cards = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    linha_cards.pack(
        fill="x",
        pady=(0, 20)
    )

    dados_cards = [
        (
            "PRODUTOS",
            indicadores["produtos"],
            AZUL,
            "▦",
            "Itens cadastrados"
        ),
        (
            "UNIDADES",
            indicadores["unidades"],
            CIANO,
            "◈",
            "Quantidade total"
        ),
        (
            "VALOR EM ESTOQUE",
            formatar_moeda(indicadores["valor"]),
            ROXO,
            "R$",
            "Valor do inventário"
        ),
        (
            "ESTOQUE BAIXO",
            indicadores["estoque_baixo"],
            AMARELO,
            "!",
            "Itens para verificar"
        )
    ]

    for coluna, dados in enumerate(dados_cards):
        linha_cards.grid_columnconfigure(
            coluna,
            weight=1,
            uniform="indicadores"
        )

        card = criar_card(
            linha_cards,
            *dados
        )

        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=(
                0 if coluna == 0 else 6,
                0 if coluna == 3 else 6
            )
        )

    # Gráficos
    graficos = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    graficos.pack(
        fill="both",
        expand=True,
        pady=(0, 18)
    )

    graficos.grid_columnconfigure(0, weight=1, uniform="graficos")
    graficos.grid_columnconfigure(1, weight=1, uniform="graficos")
    graficos.grid_rowconfigure(0, weight=1)

    card_categoria = criar_card_grafico(
        graficos,
        "Distribuição do estoque",
        "Unidades por categoria",
        "01"
    )
    card_categoria.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 7)
    )

    desenhar_grafico_rosca(card_categoria, categorias)

    card_mov = criar_card_grafico(
        graficos,
        "Entradas e saídas",
        "Movimentações dos últimos sete dias",
        "02"
    )
    card_mov.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(7, 0)
    )

    desenhar_grafico_movimentacoes(card_mov, movimentacoes)

    # Histórico
    criar_historico(
        app.conteudo,
        recentes
    ).pack(
        fill="x",
        pady=(0, 10)
    )
