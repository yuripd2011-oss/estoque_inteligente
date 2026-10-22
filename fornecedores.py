
import customtkinter as ctk
from tkinter import messagebox
import theme
import database


def mostrar_fornecedores(app):
    for widget in app.conteudo.winfo_children():
        widget.destroy()

    fornecedor_selecionado = {"id": None}

    # CABEÇALHO
    ctk.CTkLabel(
        app.conteudo,
        text="Fornecedores",
        font=("Segoe UI", 30, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w")

    ctk.CTkLabel(
        app.conteudo,
        text="Gerencie seus fornecedores e contatos comerciais.",
        font=("Segoe UI", 13),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", pady=(4, 20))

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
        text="Cadastro de fornecedor",
        font=("Segoe UI", 18, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", padx=16, pady=(15, 12))

    campos = ctk.CTkFrame(formulario, fg_color="transparent")
    campos.pack(fill="x", padx=10)

    for coluna in range(2):
        campos.grid_columnconfigure(coluna, weight=1, uniform="campo")

    def criar_campo(rotulo, linha, coluna, placeholder):
        bloco = ctk.CTkFrame(campos, fg_color="transparent")
        bloco.grid(
            row=linha,
            column=coluna,
            sticky="ew",
            padx=6,
            pady=5
        )

        ctk.CTkLabel(
            bloco,
            text=rotulo,
            text_color=theme.SECUNDARIO,
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(0, 5))

        campo = ctk.CTkEntry(
            bloco,
            placeholder_text=placeholder,
            height=38,
            fg_color=theme.FUNDO,
            border_color=theme.BORDA,
            text_color=theme.TEXTO,
            corner_radius=8
        )
        campo.pack(fill="x")
        return campo

    campo_nome = criar_campo("Nome / Razão social *", 0, 0, "Nome do fornecedor")
    campo_documento = criar_campo("CNPJ / CPF", 0, 1, "Documento")
    campo_telefone = criar_campo("Telefone", 1, 0, "(61) 99999-9999")
    campo_email = criar_campo("E-mail", 1, 1, "contato@empresa.com")
    campo_endereco = criar_campo("Endereço", 2, 0, "Rua, número, cidade")
    campo_observacao = criar_campo("Observações", 2, 1, "Informações adicionais")

    # BOTÕES
    barra_botoes = ctk.CTkFrame(formulario, fg_color="transparent")
    barra_botoes.pack(fill="x", padx=16, pady=(10, 16))

    # LISTAGEM
    painel_lista = ctk.CTkFrame(
        app.conteudo,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        border_width=1,
        corner_radius=14
    )
    painel_lista.pack(fill="both", expand=True)

    topo_lista = ctk.CTkFrame(painel_lista, fg_color="transparent")
    topo_lista.pack(fill="x", padx=16, pady=14)

    ctk.CTkLabel(
        topo_lista,
        text="Lista de fornecedores",
        font=("Segoe UI", 18, "bold"),
        text_color=theme.TEXTO
    ).pack(side="left")

    campo_pesquisa = ctk.CTkEntry(
        topo_lista,
        placeholder_text="Pesquisar fornecedor...",
        width=250,
        height=36,
        fg_color=theme.FUNDO,
        border_color=theme.BORDA,
        text_color=theme.TEXTO
    )
    campo_pesquisa.pack(side="right")

    lista = ctk.CTkScrollableFrame(
        painel_lista,
        fg_color="transparent"
    )
    lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def limpar_campos():
        fornecedor_selecionado["id"] = None

        for campo in (
            campo_nome, campo_documento, campo_telefone,
            campo_email, campo_endereco, campo_observacao
        ):
            campo.delete(0, "end")

        botao_salvar.configure(text="Cadastrar fornecedor")
        botao_cancelar.pack_forget()

    def obter_dados():
        nome = campo_nome.get().strip()

        if not nome:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe o nome ou a razão social."
            )
            campo_nome.focus()
            return None

        email = campo_email.get().strip()

        if email and ("@" not in email or "." not in email.split("@")[-1]):
            messagebox.showwarning(
                "E-mail inválido",
                "Confira o endereço de e-mail informado."
            )
            campo_email.focus()
            return None

        return (
            nome,
            campo_documento.get().strip(),
            campo_telefone.get().strip(),
            email,
            campo_endereco.get().strip(),
            campo_observacao.get().strip()
        )

    def salvar_fornecedor():
        dados = obter_dados()
        if dados is None:
            return

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            if fornecedor_selecionado["id"] is None:
                cursor.execute(
                    """
                    INSERT INTO fornecedores
                    (nome, documento, telefone, email, endereco, observacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    dados
                )
                mensagem = "Fornecedor cadastrado com sucesso!"
            else:
                cursor.execute(
                    """
                    UPDATE fornecedores
                    SET nome=%s, documento=%s, telefone=%s,
                        email=%s, endereco=%s, observacao=%s
                    WHERE id=%s
                    """,
                    dados + (fornecedor_selecionado["id"],)
                )
                mensagem = "Fornecedor atualizado com sucesso!"

            conexao.commit()
            limpar_campos()
            carregar_fornecedores()
            messagebox.showinfo("Sucesso", mensagem)

        except Exception as erro:
            if conexao:
                conexao.rollback()
            messagebox.showerror(
                "Erro ao salvar",
                "Não foi possível salvar o fornecedor.\n\n"
                f"Detalhes: {erro}\n\n"
                "Confira se a tabela fornecedores foi criada."
            )
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def editar_fornecedor(fornecedor):
        fornecedor_selecionado["id"] = fornecedor[0]

        campos_edicao = [
            (campo_nome, fornecedor[1]),
            (campo_documento, fornecedor[2]),
            (campo_telefone, fornecedor[3]),
            (campo_email, fornecedor[4]),
            (campo_endereco, fornecedor[5]),
            (campo_observacao, fornecedor[6])
        ]

        for campo, valor in campos_edicao:
            campo.delete(0, "end")
            campo.insert(0, valor or "")

        botao_salvar.configure(text="Salvar alterações")
        botao_cancelar.pack(side="left", padx=(8, 0))

    def excluir_fornecedor(fornecedor):
        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f"Deseja excluir o fornecedor '{fornecedor[1]}'?"
        )

        if not confirmar:
            return

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            cursor.execute(
                "DELETE FROM fornecedores WHERE id = %s",
                (fornecedor[0],)
            )

            conexao.commit()
            carregar_fornecedores()
            messagebox.showinfo("Sucesso", "Fornecedor excluído.")

        except Exception as erro:
            if conexao:
                conexao.rollback()

            messagebox.showerror(
                "Não foi possível excluir",
                "O fornecedor pode estar vinculado a outros registros.\n\n"
                f"Detalhes: {erro}"
            )
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    def carregar_fornecedores(*_):
        for widget in lista.winfo_children():
            widget.destroy()

        conexao = None
        cursor = None

        try:
            conexao = database.conectar()
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT id, nome, documento, telefone, email, endereco, observacao
                FROM fornecedores
                ORDER BY nome
            """)

            fornecedores = cursor.fetchall()
            termo = campo_pesquisa.get().strip().casefold()

            filtrados = [
                f for f in fornecedores
                if termo in str(f[1] or "").casefold()
                or termo in str(f[2] or "").casefold()
                or termo in str(f[3] or "").casefold()
                or termo in str(f[4] or "").casefold()
            ]

            if not filtrados:
                ctk.CTkLabel(
                    lista,
                    text="Nenhum fornecedor encontrado.",
                    text_color=theme.SECUNDARIO
                ).pack(pady=22)
                return

            for fornecedor in filtrados:
                linha = ctk.CTkFrame(
                    lista,
                    fg_color=theme.CARD_HOVER,
                    corner_radius=9
                )
                linha.pack(fill="x", pady=4)

                texto = (
                    f"{fornecedor[1]}\n"
                    f"Documento: {fornecedor[2] or 'Não informado'}"
                    f"   •   Telefone: {fornecedor[3] or 'Não informado'}\n"
                    f"E-mail: {fornecedor[4] or 'Não informado'}"
                    f"   •   Endereço: {fornecedor[5] or 'Não informado'}"
                )

                ctk.CTkLabel(
                    linha,
                    text=texto,
                    font=("Segoe UI", 11),
                    text_color=theme.TEXTO,
                    justify="left",
                    anchor="w"
                ).pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=14,
                    pady=12
                )

                botoes = ctk.CTkFrame(linha, fg_color="transparent")
                botoes.pack(side="right", padx=8)

                ctk.CTkButton(
                    botoes,
                    text="Editar",
                    width=65,
                    height=30,
                    fg_color=theme.AZUL,
                    hover_color=theme.AZUL_HOVER,
                    command=lambda f=fornecedor: editar_fornecedor(f)
                ).pack(pady=3)

                ctk.CTkButton(
                    botoes,
                    text="Excluir",
                    width=65,
                    height=30,
                    fg_color="#7F1D1D",
                    hover_color=theme.VERMELHO,
                    command=lambda f=fornecedor: excluir_fornecedor(f)
                ).pack(pady=3)

        except Exception as erro:
            ctk.CTkLabel(
                lista,
                text=(
                    "Não foi possível carregar os fornecedores.\n\n"
                    f"{erro}\n\n"
                    "A tabela fornecedores pode ainda não existir."
                ),
                text_color=theme.VERMELHO,
                justify="left",
                wraplength=850
            ).pack(anchor="w", padx=10, pady=15)
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()

    botao_salvar = ctk.CTkButton(
        barra_botoes,
        text="Cadastrar fornecedor",
        height=39,
        width=190,
        fg_color=theme.AZUL,
        hover_color=theme.AZUL_HOVER,
        command=salvar_fornecedor
    )
    botao_salvar.pack(side="left")

    botao_cancelar = ctk.CTkButton(
        barra_botoes,
        text="Cancelar edição",
        height=39,
        width=135,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        command=limpar_campos
    )

    ctk.CTkButton(
        barra_botoes,
        text="Atualizar lista",
        height=39,
        width=120,
        fg_color=theme.CARD_HOVER,
        hover_color=theme.BORDA,
        command=carregar_fornecedores
    ).pack(side="left", padx=8)

    campo_pesquisa.bind("<KeyRelease>", carregar_fornecedores)

    carregar_fornecedores()
