import customtkinter as ctk
import mysql.connector
from decimal import Decimal
from tkinter import messagebox

import theme
from database import conectar


def mostrar_compras_inteligentes(app):
    """
    Tela de compras inteligentes.
    Analisa o estoque e sugere reposições.
    """

    for widget in app.conteudo.winfo_children():
        widget.destroy()

    # =====================================================
    # CABEÇALHO
    # =====================================================

    cabecalho = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    cabecalho.pack(fill="x", padx=30, pady=(25, 15))

    ctk.CTkLabel(
        cabecalho,
        text="Compras inteligentes",
        font=("Segoe UI", 28, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        cabecalho,
        text="Planeje reposições e evite a falta de produtos.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(5, 0))

    # =====================================================
    # INDICADORES
    # =====================================================

    indicadores = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    indicadores.pack(fill="x", padx=25, pady=5)

    def criar_card(titulo, valor, cor):
        card = ctk.CTkFrame(
            indicadores,
            fg_color=theme.CARD,
            corner_radius=14
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 12),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", padx=15, pady=(15, 5))

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 24, "bold"),
            text_color=cor
        )
        label_valor.pack(anchor="w", padx=15, pady=(0, 15))

        return label_valor

    card_repor = criar_card(
        "Produtos para repor",
        "0",
        theme.AMARELO
    )

    card_unidades = criar_card(
        "Unidades sugeridas",
        "0",
        theme.AZUL
    )

    card_custo = criar_card(
        "Custo estimado",
        "R$ 0,00",
        theme.VERDE
    )

    # =====================================================
    # ORIENTAÇÃO
    # =====================================================

    aviso = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=12
    )
    aviso.pack(fill="x", padx=30, pady=(10, 15))

    ctk.CTkLabel(
        aviso,
        text=(
            "A recomendação usa o estoque mínimo cadastrado. "
            "A quantidade sugerida considera uma reposição "
            "até o dobro desse mínimo."
        ),
        font=("Segoe UI", 12),
        text_color=theme.SECUNDARIO,
        wraplength=900,
        justify="left"
    ).pack(anchor="w", padx=15, pady=12)

    # =====================================================
    # TABELA
    # =====================================================

    tabela_container = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=14
    )
    tabela_container.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=(0, 15)
    )

    ctk.CTkLabel(
        tabela_container,
        text="Recomendações de compra",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=18, pady=(15, 10))

    colunas = (
        "id",
        "nome",
        "categoria",
        "estoque",
        "minimo",
        "comprar",
        "preco",
        "total"
    )

    tabela = ctk.CTkScrollableFrame(
        tabela_container,
        fg_color="transparent"
    )
    tabela.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    larguras = [45, 180, 125, 80, 80, 90, 100, 110]

    cabecalho_tabela = ctk.CTkFrame(
        tabela,
        fg_color=theme.SIDEBAR,
        corner_radius=8
    )
    cabecalho_tabela.pack(fill="x", pady=(0, 5))

    titulos = [
        "ID",
        "Produto",
        "Categoria",
        "Estoque",
        "Mínimo",
        "Comprar",
        "Preço",
        "Total"
    ]

    for titulo, largura in zip(titulos, larguras):
        ctk.CTkLabel(
            cabecalho_tabela,
            text=titulo,
            width=largura,
            font=("Segoe UI", 11, "bold"),
            text_color=theme.SECUNDARIO,
            anchor="w"
        ).pack(side="left", padx=3, pady=10)

    # =====================================================
    # FUNÇÕES
    # =====================================================

    def formatar_moeda(valor):
        valor = Decimal(str(valor or 0))
        texto = f"{valor:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    def carregar_recomendacoes():
        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id,
                    nome,
                    categoria,
                    quantidade,
                    preco,
                    estoque_minimo
                FROM produtos
                ORDER BY nome
            """)

            produtos = cursor.fetchall()

            for widget in tabela.winfo_children():
                if widget is not cabecalho_tabela:
                    widget.destroy()

            # A tabela usa um frame próprio para o cabeçalho.
            # Limpa apenas as linhas antigas abaixo.

            total_produtos = 0
            total_unidades = 0
            custo_total = Decimal("0.00")

            for produto in produtos:
                estoque = int(produto["quantidade"] or 0)
                minimo = int(produto["estoque_minimo"] or 0)
                preco = Decimal(str(produto["preco"] or 0))

                if estoque > minimo:
                    continue

                quantidade_comprar = max((minimo * 2) - estoque, 0)

                if quantidade_comprar == 0:
                    continue

                total = preco * quantidade_comprar

                total_produtos += 1
                total_unidades += quantidade_comprar
                custo_total += total

                linha = ctk.CTkFrame(
                    tabela,
                    fg_color=theme.SIDEBAR,
                    corner_radius=7
                )
                linha.pack(fill="x", pady=3)

                valores = [
                    str(produto["id"]),
                    str(produto["nome"] or "")[:22],
                    str(produto["categoria"] or "-")[:15],
                    str(estoque),
                    str(minimo),
                    str(quantidade_comprar),
                    formatar_moeda(preco),
                    formatar_moeda(total)
                ]

                for indice, (valor, largura) in enumerate(
                    zip(valores, larguras)
                ):
                    cor = theme.TEXTO

                    if indice == 5:
                        cor = theme.AZUL

                    ctk.CTkLabel(
                        linha,
                        text=valor,
                        width=largura,
                        font=("Segoe UI", 11),
                        text_color=cor,
                        anchor="w"
                    ).pack(side="left", padx=3, pady=11)

            card_repor.configure(text=str(total_produtos))
            card_unidades.configure(text=str(total_unidades))
            card_custo.configure(text=formatar_moeda(custo_total))

            if total_produtos == 0:
                ctk.CTkLabel(
                    tabela,
                    text="Nenhum produto precisa de reposição.",
                    font=("Segoe UI", 13),
                    text_color=theme.VERDE
                ).pack(pady=30)

        except mysql.connector.Error as erro:
            messagebox.showerror(
                "Erro no banco de dados",
                f"Não foi possível carregar as recomendações:\n{erro}"
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar as recomendações:\n{erro}"
            )

        finally:
            if cursor is not None:
                cursor.close()

            if conexao is not None and conexao.is_connected():
                conexao.close()

    # =====================================================
    # BOTÃO ATUALIZAR
    # =====================================================

    botoes = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    botoes.pack(fill="x", padx=30, pady=(0, 20))

    ctk.CTkButton(
        botoes,
        text="↻  Atualizar recomendações",
        height=40,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        font=("Segoe UI", 12, "bold"),
        command=carregar_recomendacoes
    ).pack(side="left")

    carregar_recomendacoes()
