
import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal

import theme
from database import conectar


def mostrar_inteligencia_abc(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    # CABEÇALHO
    ctk.CTkLabel(
        app.conteudo,
        text="Inteligência ABC",
        font=("Segoe UI", 28, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=30, pady=(25, 5))

    ctk.CTkLabel(
        app.conteudo,
        text="Descubra quais produtos representam maior valor no estoque.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", padx=30, pady=(0, 20))

    # RESUMO
    cards = ctk.CTkFrame(
        app.conteudo,
        fg_color="transparent"
    )
    cards.pack(fill="x", padx=25, pady=(0, 15))

    def criar_card(titulo, valor, cor):
        card = ctk.CTkFrame(
            cards,
            fg_color=theme.CARD,
            corner_radius=12
        )
        card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color=theme.SECUNDARIO,
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=15, pady=(14, 5))

        label = ctk.CTkLabel(
            card,
            text=valor,
            text_color=cor,
            font=("Segoe UI", 23, "bold")
        )
        label.pack(anchor="w", padx=15, pady=(0, 14))
        return label

    card_a = criar_card("Classe A", "0", theme.VERDE)
    card_b = criar_card("Classe B", "0", theme.AZUL)
    card_c = criar_card("Classe C", "0", theme.AMARELO)

    # EXPLICAÇÃO
    explicacao = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=12
    )
    explicacao.pack(fill="x", padx=30, pady=(0, 15))

    ctk.CTkLabel(
        explicacao,
        text=(
            "Critério inicial: A = até 80% do valor acumulado; "
            "B = até 95%; C = restante. A classificação considera "
            "o valor atual em estoque, não as vendas."
        ),
        text_color=theme.SECUNDARIO,
        font=("Segoe UI", 12),
        wraplength=950,
        justify="left"
    ).pack(anchor="w", padx=15, pady=12)

    # LISTA
    painel = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        corner_radius=14
    )
    painel.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    ctk.CTkLabel(
        painel,
        text="Classificação dos produtos",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=18, pady=(15, 8))

    lista = ctk.CTkScrollableFrame(
        painel,
        fg_color="transparent"
    )
    lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def moeda(valor):
        texto = f"{valor:,.2f}"
        texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {texto}"

    def carregar():
        for widget in lista.winfo_children():
            widget.destroy()

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, nome, categoria, quantidade, preco
                FROM produtos
                ORDER BY nome
            """)

            produtos = cursor.fetchall()

            dados = []
            valor_total = Decimal("0")

            for p in produtos:
                quantidade = int(p["quantidade"] or 0)
                preco = Decimal(str(p["preco"] or 0))
                valor = preco * quantidade

                dados.append({
                    "id": p["id"],
                    "nome": p["nome"] or "Sem nome",
                    "categoria": p["categoria"] or "-",
                    "quantidade": quantidade,
                    "preco": preco,
                    "valor": valor
                })

                valor_total += valor

            # Primeiro, os produtos de maior valor.
            dados.sort(key=lambda item: item["valor"], reverse=True)

            acumulado = Decimal("0")
            contagem = {"A": 0, "B": 0, "C": 0}

            for item in dados:
                if valor_total <= 0:
                    classe = "C"
                else:
                    percentual_anterior = acumulado / valor_total
                    acumulado += item["valor"]

                    if percentual_anterior < Decimal("0.80"):
                        classe = "A"
                    elif percentual_anterior < Decimal("0.95"):
                        classe = "B"
                    else:
                        classe = "C"

                item["classe"] = classe
                contagem[classe] += 1

            card_a.configure(text=str(contagem["A"]))
            card_b.configure(text=str(contagem["B"]))
            card_c.configure(text=str(contagem["C"]))

            if not dados:
                ctk.CTkLabel(
                    lista,
                    text="Nenhum produto cadastrado.",
                    text_color=theme.SECUNDARIO
                ).pack(pady=25)
                return

            for item in dados:
                linha = ctk.CTkFrame(
                    lista,
                    fg_color=theme.SIDEBAR,
                    corner_radius=9
                )
                linha.pack(fill="x", pady=4)

                cor_classe = {
                    "A": theme.VERDE,
                    "B": theme.AZUL,
                    "C": theme.AMARELO
                }[item["classe"]]

                topo = ctk.CTkFrame(
                    linha,
                    fg_color="transparent"
                )
                topo.pack(fill="x", padx=12, pady=(10, 3))

                ctk.CTkLabel(
                    topo,
                    text=f"#{item['id']} • {item['nome']}",
                    font=("Segoe UI", 12, "bold"),
                    text_color=theme.TEXTO
                ).pack(side="left", fill="x", expand=True, anchor="w")

                ctk.CTkLabel(
                    topo,
                    text=f"CLASSE {item['classe']}",
                    font=("Segoe UI", 11, "bold"),
                    text_color=cor_classe
                ).pack(side="right", padx=5)

                ctk.CTkLabel(
                    linha,
                    text=(
                        f"Categoria: {item['categoria']}  •  "
                        f"Quantidade: {item['quantidade']}  •  "
                        f"Preço unitário: {moeda(item['preco'])}  •  "
                        f"Valor em estoque: {moeda(item['valor'])}"
                    ),
                    font=("Segoe UI", 11),
                    text_color=theme.SECUNDARIO,
                    wraplength=1000,
                    justify="left"
                ).pack(anchor="w", padx=12, pady=(2, 10))

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível calcular a classificação ABC:\n{erro}"
            )

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

    ctk.CTkButton(
        app.conteudo,
        text="↻  Atualizar classificação",
        height=40,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        command=carregar
    ).pack(anchor="w", padx=30, pady=(0, 15))

    carregar()
