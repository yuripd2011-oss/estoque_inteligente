import customtkinter as ctk
import theme


def criar_card_estatistica(pai, titulo, valor, descricao, cor):
    card = ctk.CTkFrame(
        pai,
        fg_color=theme.CARD,
        corner_radius=16,
        border_width=1,
        border_color=theme.BORDA
    )

    ctk.CTkLabel(
        card,
        text=titulo,
        font=("Segoe UI", 12),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", padx=16, pady=(18, 8))

    ctk.CTkLabel(
        card,
        text=valor,
        font=("Segoe UI", 28, "bold"),
        text_color=cor
    ).pack(anchor="w", padx=16)

    ctk.CTkLabel(
        card,
        text=descricao,
        font=("Segoe UI", 10),
        text_color=theme.SECUNDARIO
    ).pack(anchor="w", padx=16, pady=(5, 18))

    return card


def criar_titulo(pai, titulo, subtitulo=""):
    ctk.CTkLabel(
        pai,
        text=titulo,
        font=("Segoe UI", 25, "bold"),
        text_color=theme.TEXTO
    ).pack(anchor="w", pady=(0, 5))

    if subtitulo:
        ctk.CTkLabel(
            pai,
            text=subtitulo,
            font=("Segoe UI", 12),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", pady=(0, 20))


def criar_entrada(pai, placeholder, **kwargs):
    return ctk.CTkEntry(
        pai,
        placeholder_text=placeholder,
        height=40,
        corner_radius=10,
        fg_color=theme.CARD,
        border_color=theme.BORDA,
        text_color=theme.TEXTO,
        **kwargs
    )
