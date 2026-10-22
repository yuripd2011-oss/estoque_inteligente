
import customtkinter as ctk
import theme


def criar_campo(
    parent,
    titulo,
    placeholder="",
    senha=False
):
    """
    Cria um campo de formulário com título e entrada.
    Retorna o campo para leitura do valor.
    """

    container = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )

    container.pack(
        fill="x",
        pady=(0, 16)
    )

    ctk.CTkLabel(
        container,
        text=titulo,
        font=("Segoe UI", 12, "bold"),
        text_color=theme.TEXTO
    ).pack(
        anchor="w",
        pady=(0, 7)
    )

    campo = ctk.CTkEntry(
        container,
        height=42,
        placeholder_text=placeholder,
        show="*" if senha else "",
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        text_color=theme.TEXTO,
        corner_radius=9
    )

    campo.pack(fill="x")

    return campo


def criar_botao(
    parent,
    texto,
    comando,
    principal=True
):
    """
    Cria um botão reutilizável para autenticação.
    """

    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        height=44,
        corner_radius=9,
        fg_color=theme.AZUL if principal else "transparent",
        hover_color=(
            theme.AZUL_HOVER
            if principal
            else theme.CARD_HOVER
        ),
        border_width=0 if principal else 1,
        border_color=theme.BORDA,
        text_color=theme.TEXTO,
        font=("Segoe UI", 13, "bold"),
        cursor="hand2"
    )


def criar_titulo(
    parent,
    titulo,
    subtitulo
):
    """
    Cria o cabeçalho de uma tela de autenticação.
    """

    ctk.CTkLabel(
        parent,
        text=titulo,
        font=("Segoe UI", 25, "bold"),
        text_color=theme.TEXTO
    ).pack(
        anchor="w",
        pady=(0, 6)
    )

    ctk.CTkLabel(
        parent,
        text=subtitulo,
        font=("Segoe UI", 12),
        text_color=theme.SECUNDARIO,
        wraplength=340,
        justify="left"
    ).pack(
        anchor="w",
        pady=(0, 24)
    )
