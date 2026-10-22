import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation
from datetime import date, datetime

import theme
import database


def mostrar_produtos(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    estado = {"produto_id": None}

    # PREPARAÇÃO DO BANCO: ADICIONA COLUNAS SEM APAGAR DADOS
    conexao = None
    cursor = None

    try:
        conexao = database.conectar()
        cursor = conexao.cursor()
        cursor.execute("SHOW COLUMNS FROM produtos")
        colunas_existentes = {linha[0].lower() for linha in cursor.fetchall()}

        if "codigo_barras" not in colunas_existentes:
            cursor.execute(
                "ALTER TABLE produtos ADD COLUMN codigo_barras VARCHAR(100) NULL"
            )

        if "validade" not in colunas_existentes:
            cursor.execute(
                "ALTER TABLE produtos ADD COLUMN validade DATE NULL"
            )

        conexao.commit()

    except Exception as erro:
        if conexao:
            conexao.rollback()
        messagebox.showerror(
            "Erro no banco",
            f"Não foi possível preparar os campos novos:\n\n{erro}"
        )
        return

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    # CABEÇALHO
    topo = ctk.CTkFrame(app.conteudo, fg_color="transparent")
    topo.pack(fill="x", pady=(0, 18))

    ctk.CTkLabel(
        topo,
        text="Produtos",
        font=("Segoe UI", 30, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        topo,
        text="Catálogo, código de barras e controle de validade.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(4, 0))

    # INDICADORES
    indicadores = ctk.CTkFrame(app.conteudo, fg_color="transparent")
    indicadores.pack(fill="x", pady=(0, 18))

    for i in range(4):
        indicadores.grid_columnconfigure(i, weight=1, uniform="indicadores")

    def criar_indicador(coluna, titulo, cor):
        card = ctk.CTkFrame(
            indicadores,
            fg_color=theme.CARD,
            border_color=theme.BORDA,
            border_width=1,
            corner_radius=13
        )
        card.grid(
            row=0,
            column=coluna,
            sticky="nsew",
            padx=(0 if coluna == 0 else 7, 0)
        )

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 11),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", padx=14, pady=(12, 4))

        valor = ctk.CTkLabel(
            card,
            text="—",
            font=("Segoe UI", 21, "bold"),
            text_color=cor
        )
        valor.pack(anchor="w", padx=14, pady=(0, 12))
        return valor

    indicador_total = criar_indicador(
        0, "Produtos cadastrados", theme.AZUL
    )
    indicador_unidades = criar_indicador(
        1, "Unidades em estoque", theme.VERDE
    )
    indicador_valor = criar_indicador(
        2, "Valor do estoque", theme.ROXO
    )
    indicador_validade = criar_indicador(
        3, "Vencidos / próximos", theme.AMARELO
    )

    # FORMULÁRIO
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
        text="Cadastro de produto",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).grid(
        row=0, column=0, columnspan=4,
        sticky="w", padx=16, pady=(14, 12)
    )

    for coluna in range(4):
        formulario.grid_columnconfigure(
            coluna, weight=1, uniform="campos"
        )

    def criar_campo(rotulo, linha, coluna, placeholder):
        bloco = ctk.CTkFrame(
            formulario, fg_color="transparent"
        )
        bloco.grid(
            row=linha, column=coluna,
            sticky="ew", padx=8, pady=5
        )

        ctk.CTkLabel(
            bloco,
            text=rotulo,
            font=("Segoe UI", 11),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", pady=(0, 5))

        campo = ctk.CTkEntry(
            bloco,
            placeholder_text=placeholder,
            height=37,
            fg_color=theme.FUNDO,
            border_color=theme.BORDA,
            text_color=theme.TEXTO,
            corner_radius=8
        )
        campo.pack(fill="x")
        return campo

    campo_nome = criar_campo(
        "Nome *", 1, 0, "Ex.: Teclado gamer"
    )
    campo_categoria = criar_campo(
        "Categoria", 1, 1, "Ex.: Periféricos"
    )
    campo_quantidade = criar_campo(
        "Quantidade *", 1, 2, "Ex.: 25"
    )
    campo_preco = criar_campo(
        "Preço unitário *", 1, 3, "Ex.: 149,90"
    )

    campo_barras = criar_campo(
        "Código de barras", 2, 0, "Digite ou leia o código"
    )
    campo_validade = criar_campo(
        "Validade (AAAA-MM-DD)", 2, 1, "Ex.: 2027-12-31"
    )
    campo_minimo = criar_campo(
        "Estoque mínimo", 2, 2, "Ex.: 5"
    )

    ctk.CTkLabel(
        formulario,
        text="* Obrigatório | Validade opcional",
        font=("Segoe UI", 10),
        text_color=theme.SECUNDARIO
    ).grid(row=2, column=3, sticky="w", padx=8)

    botoes_form = ctk.CTkFrame(
        formulario, fg_color="transparent"
    )
    botoes_form.grid(
        row=3, column=0, columnspan=4,
        sticky="w", padx=8, pady=(8, 15)
    )

    # LISTAGEM
    painel = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=14
    )
    painel.pack(fill="both", expand=True)

    barra = ctk.CTkFrame(painel, fg_color="transparent")
    barra.pack(fill="x", padx=16, pady=14)

    ctk.CTkLabel(
        barra,
        text="Catálogo de produtos",
        font=("Segoe UI", 17, "bold"),
        text_color=theme.TEXTO
    ).pack(side="left")

    pesquisa = ctk.CTkEntry(
        barra,
        placeholder_text="Pesquisar nome, categoria ou código...",
        width=310,
        height=36,
        fg_color=theme.FUNDO,
        border_color=theme.BORDA,
        corner_radius=8
    )
    pesquisa.pack(side="right")

    cabecalho = ctk.CTkFrame(
        painel, fg_color=theme.SIDEBAR, corner_radius=8
    )
    cabecalho.pack(fill="x", padx=12)

    colunas_tabela = [
        ("ID / PRODUTO", 3),
        ("CATEGORIA", 2),
        ("QTD.", 1),
        ("PREÇO", 1),
        ("MÍN.", 1),
        ("VALIDADE", 2),
        ("STATUS", 2)
    ]

    for i, (texto, peso) in enumerate(colunas_tabela):
        cabecalho.grid_columnconfigure(
            i, weight=peso, uniform="tabela"
        )
        ctk.CTkLabel(
            cabecalho,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            text_color=theme.SECUNDARIO,
            anchor="w"
        ).grid(
            row=0, column=i, sticky="ew",
            padx=7, pady=10
        )

    lista = ctk.CTkScrollableFrame(
        painel, fg_color="transparent", corner_radius=0
    )
    lista.pack(fill="both", expand=True, padx=12, pady=(4, 10))

    def limpar_campos():
        for campo in (
            campo_nome, campo_categoria, campo_quantidade,
            campo_preco, campo_barras, campo_validade,
            campo_minimo
        ):
            campo.delete(0, "end")

        estado["produto_id"] = None
        botao_salvar.configure(text="Cadastrar produto")
        botao_cancelar.pack_forget()

    def ler_decimal(texto, rotulo):
        texto = texto.strip().replace("R$", "").replace(" ", "")
        texto = texto.replace(".", "").replace(",", ".")

        try:
            valor = Decimal(texto)
        except InvalidOperation:
            raise ValueError(
                f"Informe um valor válido para {rotulo}."
            )

        if not valor.is_finite() or valor < 0:
            raise ValueError(
                f"{rotulo} não pode ser negativo."
            )

        return valor

    def salvar_produto():
        nome = campo_nome.get().strip()
        categoria = campo_categoria.get().strip() or "Geral"
        codigo = campo_barras.get().strip() or None
        validade_texto = campo_validade.get().strip()
        validade = None

        if not nome:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe o nome do produto."
            )
            campo_nome.focus()
            return

        try:
            quantidade = int(campo_quantidade.get().strip())
            minimo_texto = campo_minimo.get().strip()
            minimo = int(minimo_texto) if minimo_texto else 0
            preco = ler_decimal(
                campo_preco.get(), "preço"
            )

            if quantidade < 0 or minimo < 0:
                raise ValueError(
                    "Quantidade e estoque mínimo não podem ser negativos."
                )

            if validade_texto:
                try:
                    validade = datetime.strptime(
                        validade_texto, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    raise ValueError(
                        "Validade inválida. Use AAAA-MM-DD."
                    )

        except ValueError as erro:
            messagebox.showwarning(
                "Dados inválidos", str(erro)
            )
            return

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            if codigo:
                cursor.execute(
                    """
                    SELECT id FROM produtos
                    WHERE codigo_barras = %s AND id <> %s
                    """,
                    (codigo, estado["produto_id"] or 0)
                )

                if cursor.fetchone():
                    messagebox.showwarning(
                        "Código já cadastrado",
                        "Outro produto já utiliza esse código de barras."
                    )
                    return

            if estado["produto_id"] is None:
                cursor.execute(
                    """
                    INSERT INTO produtos
                    (nome, categoria, quantidade, preco,
                     estoque_minimo, codigo_barras, validade)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        nome, categoria, quantidade, preco,
                        minimo, codigo, validade
                    )
                )
                mensagem = "Produto cadastrado com sucesso!"

            else:
                cursor.execute(
                    """
                    UPDATE produtos
                    SET nome=%s, categoria=%s, quantidade=%s,
                        preco=%s, estoque_minimo=%s,
                        codigo_barras=%s, validade=%s
                    WHERE id=%s
                    """,
                    (
                        nome, categoria, quantidade, preco,
                        minimo, codigo, validade,
                        estado["produto_id"]
                    )
                )
                mensagem = "Produto atualizado com sucesso!"

            conexao.commit()
            limpar_campos()
            carregar_produtos()
            messagebox.showinfo("Sucesso", mensagem)

        except Exception as erro:
            if conexao:
                conexao.rollback()
            messagebox.showerror(
                "Erro no banco",
                f"Não foi possível salvar o produto:\n\n{erro}"
            )

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def editar_produto(produto):
        estado["produto_id"] = produto[0]

        valores = [
            (campo_nome, produto[1] or ""),
            (campo_categoria, produto[2] or ""),
            (campo_quantidade, str(produto[3] or 0)),
            (
                campo_preco,
                f"{Decimal(str(produto[4] or 0)):.2f}".replace(".", ",")
            ),
            (campo_barras, produto[6] or ""),
            (
                campo_validade,
                produto[7].strftime("%Y-%m-%d")
                if produto[7] else ""
            ),
            (campo_minimo, str(produto[5] or 0))
        ]

        for campo, valor in valores:
            campo.delete(0, "end")
            campo.insert(0, valor)

        botao_salvar.configure(text="Salvar alterações")
        botao_cancelar.pack(side="left", padx=(8, 0))
        campo_nome.focus_set()

    def excluir_produto(produto):
        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o produto '{produto[1]}'?\n\n"
            "Se houver movimentações vinculadas, o banco poderá impedir a exclusão."
        )

        if not confirmar:
            return

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM produtos WHERE id=%s",
                (produto[0],)
            )
            conexao.commit()
            carregar_produtos()
            messagebox.showinfo("Sucesso", "Produto excluído.")

        except Exception as erro:
            if conexao:
                conexao.rollback()
            messagebox.showerror(
                "Não foi possível excluir",
                "O produto pode possuir movimentações vinculadas.\n\n"
                f"Detalhes: {erro}"
            )

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def carregar_produtos(*_):
        for widget in lista.winfo_children():
            widget.destroy()

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()
            cursor.execute(
                """
                SELECT id, nome, categoria, quantidade, preco,
                       estoque_minimo, codigo_barras, validade
                FROM produtos
                ORDER BY nome
                """
            )
            produtos = cursor.fetchall()

            hoje = date.today()
            total_unidades = sum(
                int(p[3] or 0) for p in produtos
            )
            valor_total = sum(
                Decimal(str(p[4] or 0)) * int(p[3] or 0)
                for p in produtos
            )
            alertas_validade = sum(
                1 for p in produtos
                if p[7] and (p[7] - hoje).days <= 30
            )

            indicador_total.configure(text=str(len(produtos)))
            indicador_unidades.configure(
                text=f"{total_unidades:,}".replace(",", ".")
            )
            indicador_valor.configure(
                text=("R$ {:,.2f}".format(valor_total))
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )
            indicador_validade.configure(
                text=str(alertas_validade)
            )

            termo = pesquisa.get().strip().casefold()

            filtrados = [
                p for p in produtos
                if termo in str(p[1] or "").casefold()
                or termo in str(p[2] or "").casefold()
                or termo in str(p[6] or "").casefold()
                or termo == str(p[0])
            ]

            if not filtrados:
                ctk.CTkLabel(
                    lista,
                    text="Nenhum produto encontrado.",
                    text_color=theme.SECUNDARIO
                ).pack(pady=25)
                return

            for produto in filtrados:
                (
                    produto_id, nome, categoria, quantidade,
                    preco, minimo, codigo, vencimento
                ) = produto

                quantidade = int(quantidade or 0)
                minimo = int(minimo or 0)

                if quantidade == 0:
                    status_estoque = "SEM ESTOQUE"
                    cor_status = theme.VERMELHO
                elif quantidade <= minimo:
                    status_estoque = "ESTOQUE BAIXO"
                    cor_status = theme.AMARELO
                else:
                    status_estoque = "DISPONÍVEL"
                    cor_status = theme.VERDE

                if vencimento:
                    dias = (vencimento - hoje).days
                    if dias < 0:
                        status_validade = "VENCIDO"
                        cor_validade = theme.VERMELHO
                    elif dias <= 30:
                        status_validade = f"VENCE EM {dias}D"
                        cor_validade = theme.AMARELO
                    else:
                        status_validade = vencimento.strftime("%d/%m/%Y")
                        cor_validade = theme.SECUNDARIO
                else:
                    status_validade = "Sem validade"
                    cor_validade = theme.SECUNDARIO

                if vencimento and (vencimento - hoje).days <= 30:
                    status = status_validade
                    cor_status = cor_validade
                else:
                    status = status_estoque

                linha = ctk.CTkFrame(
                    lista, fg_color=theme.CARD_HOVER,
                    corner_radius=8
                )
                linha.pack(fill="x", pady=3)

                for i, (_, peso) in enumerate(colunas_tabela):
                    linha.grid_columnconfigure(
                        i, weight=peso, uniform="tabela"
                    )

                ctk.CTkLabel(
                    linha,
                    text=f"#{produto_id}  {nome}",
                    text_color=theme.TEXTO,
                    anchor="w",
                    font=("Segoe UI", 11, "bold")
                ).grid(
                    row=0, column=0, sticky="ew",
                    padx=7, pady=11
                )

                ctk.CTkLabel(
                    linha,
                    text=categoria or "Geral",
                    text_color=theme.SECUNDARIO,
                    anchor="w"
                ).grid(row=0, column=1, sticky="ew", padx=7)

                ctk.CTkLabel(
                    linha,
                    text=str(quantidade),
                    text_color=theme.TEXTO,
                    anchor="w"
                ).grid(row=0, column=2, sticky="ew", padx=7)

                preco_formatado = (
                    "R$ {:,.2f}".format(Decimal(str(preco or 0)))
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

                ctk.CTkLabel(
                    linha,
                    text=preco_formatado,
                    text_color=theme.TEXTO,
                    anchor="w"
                ).grid(row=0, column=3, sticky="ew", padx=7)

                ctk.CTkLabel(
                    linha,
                    text=str(minimo),
                    text_color=theme.SECUNDARIO,
                    anchor="w"
                ).grid(row=0, column=4, sticky="ew", padx=7)

                ctk.CTkLabel(
                    linha,
                    text=status_validade,
                    text_color=cor_validade,
                    anchor="w",
                    font=("Segoe UI", 10, "bold")
                ).grid(row=0, column=5, sticky="ew", padx=7)

                ctk.CTkLabel(
                    linha,
                    text=status,
                    text_color=cor_status,
                    anchor="w",
                    font=("Segoe UI", 9, "bold")
                ).grid(row=0, column=6, sticky="ew", padx=7)

                ctk.CTkLabel(
                    lista,
                    text=f"Código de barras: {codigo or 'não informado'}",
                    text_color=theme.SECUNDARIO,
                    font=("Segoe UI", 10),
                    anchor="w"
                ).pack(fill="x", padx=10, pady=(0, 2))

                botoes = ctk.CTkFrame(
                    lista, fg_color="transparent"
                )
                botoes.pack(fill="x", padx=4, pady=(0, 5))

                ctk.CTkButton(
                    botoes,
                    text="Editar",
                    width=70,
                    height=27,
                    fg_color=theme.AZUL,
                    hover_color=theme.AZUL_HOVER,
                    command=lambda p=produto: editar_produto(p)
                ).pack(side="right", padx=3)

                ctk.CTkButton(
                    botoes,
                    text="Excluir",
                    width=70,
                    height=27,
                    fg_color="#7F1D1D",
                    hover_color=theme.VERMELHO,
                    command=lambda p=produto: excluir_produto(p)
                ).pack(side="right", padx=3)

        except Exception as erro:
            ctk.CTkLabel(
                lista,
                text=f"Erro ao carregar produtos:\n{erro}",
                text_color=theme.VERMELHO,
                justify="left"
            ).pack(anchor="w", padx=10, pady=15)

        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    # BOTÕES DO FORMULÁRIO
    botao_salvar = ctk.CTkButton(
        botoes_form,
        text="Cadastrar produto",
        width=175,
        height=38,
        corner_radius=9,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        command=salvar_produto
    )
    botao_salvar.pack(side="left")

    botao_cancelar = ctk.CTkButton(
        botoes_form,
        text="Cancelar edição",
        width=125,
        height=38,
        corner_radius=9,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        command=limpar_campos
    )

    ctk.CTkButton(
        botoes_form,
        text="Atualizar lista",
        width=120,
        height=38,
        corner_radius=9,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        command=carregar_produtos
    ).pack(side="left", padx=8)

    pesquisa.bind("<KeyRelease>", carregar_produtos)
    campo_barras.bind(
        "<Return>",
        lambda _evento: campo_validade.focus_set()
    )
    campo_validade.bind(
        "<Return>",
        lambda _evento: salvar_produto()
    )

    carregar_produtos()