
import customtkinter as ctk
import mysql.connector

from datetime import date, timedelta
from database import conectar
import theme


def mostrar_alertas(app):
    """
    Exibe alertas de estoque baixo e vencimento.
    A função pode ser chamada pelo menu do sistema.
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
        text="Central de alertas",
        font=("Segoe UI", 27, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        principal,
        text="Acompanhe os riscos e as necessidades do seu estoque.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(5, 20))

    resumo = ctk.CTkFrame(
        principal,
        fg_color="transparent"
    )
    resumo.pack(fill="x", pady=(0, 18))

    conteudo_alertas = ctk.CTkScrollableFrame(
        principal,
        fg_color=theme.CARD,
        corner_radius=12
    )
    conteudo_alertas.pack(fill="both", expand=True)

    def criar_indicador(parent, titulo, valor, cor):
        card = ctk.CTkFrame(
            parent,
            fg_color=theme.CARD,
            corner_radius=12,
            border_width=1,
            border_color=theme.BORDA
        )
        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 12),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", padx=15, pady=(14, 5))

        numero = ctk.CTkLabel(
            card,
            text=str(valor),
            font=("Segoe UI", 27, "bold"),
            text_color=cor
        )
        numero.pack(anchor="w", padx=15, pady=(0, 14))

        return numero

    indicador_estoque = criar_indicador(
        resumo, "Estoque baixo", "—", theme.AMARELO
    )

    indicador_vencimento = criar_indicador(
        resumo, "Vencem em 30 dias", "—", theme.VERMELHO
    )

    indicador_vencidos = criar_indicador(
        resumo, "Vencidos", "—", theme.ROXO
    )

    def adicionar_alerta(titulo, descricao, cor):
        linha = ctk.CTkFrame(
            conteudo_alertas,
            fg_color=theme.FUNDO,
            corner_radius=9
        )
        linha.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ctk.CTkFrame(
            linha,
            width=4,
            fg_color=cor,
            corner_radius=2
        ).pack(side="left", fill="y", padx=(0, 12))

        textos = ctk.CTkFrame(
            linha,
            fg_color="transparent"
        )
        textos.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 12),
            pady=12
        )

        ctk.CTkLabel(
            textos,
            text=titulo,
            font=("Segoe UI", 13, "bold"),
            text_color=theme.TEXTO,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            textos,
            text=descricao,
            font=("Segoe UI", 11),
            text_color=theme.SECUNDARIO,
            anchor="w",
            justify="left",
            wraplength=650
        ).pack(fill="x", pady=(3, 0))

    def atualizar():
        for widget in conteudo_alertas.winfo_children():
            widget.destroy()

        indicador_estoque.configure(text="—")
        indicador_vencimento.configure(text="—")
        indicador_vencidos.configure(text="—")

        conexao = None
        cursor = None

        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            # Estoque baixo
            cursor.execute("""
                SELECT id, nome, quantidade, estoque_minimo
                FROM produtos
                WHERE quantidade <= estoque_minimo
                ORDER BY quantidade ASC, nome ASC
            """)

            produtos_baixos = cursor.fetchall()
            indicador_estoque.configure(
                text=str(len(produtos_baixos))
            )

            for produto in produtos_baixos:
                adicionar_alerta(
                    f"Estoque baixo: {produto['nome']}",
                    f"Produto #{produto['id']} • "
                    f"Disponível: {produto['quantidade']} • "
                    f"Mínimo: {produto['estoque_minimo']}",
                    theme.AMARELO
                )

            # Verifica se a coluna de validade existe.
            cursor.execute("SHOW COLUMNS FROM produtos")
            colunas = {
                linha["Field"]
                for linha in cursor.fetchall()
            }

            coluna_validade = next(
                (
                    nome
                    for nome in (
                        "data_validade",
                        "validade",
                        "data_vencimento"
                    )
                    if nome in colunas
                ),
                None
            )

            vencendo = []
            vencidos = []

            if coluna_validade:
                # O nome da coluna vem exclusivamente da lista
                # fixa acima, após confirmação no esquema do banco.
                cursor.execute(f"""
                    SELECT id, nome, quantidade,
                           `{coluna_validade}` AS validade
                    FROM produtos
                    WHERE `{coluna_validade}` IS NOT NULL
                      AND quantidade > 0
                      AND `{coluna_validade}` <= %s
                    ORDER BY `{coluna_validade}` ASC
                """, (date.today() + timedelta(days=30),))

                for produto in cursor.fetchall():
                    validade = produto["validade"]

                    if hasattr(validade, "date"):
                        validade = validade.date()

                    if validade < date.today():
                        vencidos.append(produto)
                    else:
                        vencendo.append(produto)

            indicador_vencimento.configure(
                text=str(len(vencendo))
            )
            indicador_vencidos.configure(
                text=str(len(vencidos))
            )

            for produto in vencidos:
                adicionar_alerta(
                    f"Produto vencido: {produto['nome']}",
                    f"Produto #{produto['id']} • "
                    f"Validade: {produto['validade']} • "
                    f"Quantidade: {produto['quantidade']}",
                    theme.ROXO
                )

            for produto in vencendo:
                adicionar_alerta(
                    f"Produto próximo do vencimento: {produto['nome']}",
                    f"Produto #{produto['id']} • "
                    f"Validade: {produto['validade']} • "
                    f"Quantidade: {produto['quantidade']}",
                    theme.VERMELHO
                )

            if not produtos_baixos and not vencendo and not vencidos:
                ctk.CTkLabel(
                    conteudo_alertas,
                    text="Tudo certo! Nenhum alerta encontrado.",
                    font=("Segoe UI", 14),
                    text_color=theme.VERDE
                ).pack(pady=30)

            elif not coluna_validade:
                ctk.CTkLabel(
                    conteudo_alertas,
                    text=(
                        "Aviso: a tabela produtos ainda não possui "
                        "uma coluna de validade reconhecida. "
                        "Os alertas de estoque estão funcionando."
                    ),
                    font=("Segoe UI", 11),
                    text_color=theme.SECUNDARIO,
                    wraplength=650
                ).pack(fill="x", padx=15, pady=15)

        except mysql.connector.Error as erro:
            ctk.CTkLabel(
                conteudo_alertas,
                text=f"Erro ao consultar alertas:\n{erro}",
                text_color=theme.VERMELHO,
                wraplength=650
            ).pack(padx=15, pady=20)

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

    ctk.CTkButton(
        principal,
        text="Atualizar alertas",
        height=38,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        command=atualizar
    ).pack(anchor="e", pady=(0, 12))

    atualizar()
