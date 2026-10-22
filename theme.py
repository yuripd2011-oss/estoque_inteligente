import customtkinter as ctk


# =========================================================
# ESTOQUE INTELIGENTE ULTIMATE — OBSIDIAN
# Tema escuro premium
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# FUNDOS
# =========================================================

FUNDO = "#080A0F"
SIDEBAR = "#0B0E14"
CARD = "#111620"
CARD_HOVER = "#171E2B"
CAMPO = "#0C111A"


# =========================================================
# BORDAS
# =========================================================

BORDA = "#202838"
BORDA_ATIVA = "#354766"


# =========================================================
# TEXTOS
# =========================================================

TEXTO = "#F5F7FF"
SECUNDARIO = "#9AA6BB"
TEXTO_FRACO = "#657187"


# =========================================================
# CORES PRINCIPAIS
# =========================================================

AZUL = "#4F8CFF"
AZUL_HOVER = "#3475F5"
AZUL_CLARO = "#79ADFF"


# =========================================================
# ESTADOS E DESTAQUES
# =========================================================

VERDE = "#35D49A"
VERMELHO = "#FF647C"
AMARELO = "#FFC857"
ROXO = "#A78BFA"
CIANO = "#42D9F5"


# =========================================================
# FONTES
# =========================================================

FONTE = "Segoe UI"
FONTE_TITULO = "Segoe UI"
FONTE_MONO = "Consolas"


# =========================================================
# DIMENSÕES
# =========================================================

RAIO_CARD = 16
RAIO_BOTAO = 10
ALTURA_BOTAO = 42
ESPACAMENTO = 20


# =========================================================
# CONFIGURAÇÃO DA JANELA
# =========================================================

def configurar_janela(janela):
    janela.title("Estoque Inteligente Ultimate")
    janela.geometry("1360x820")
    janela.minsize(1050, 650)
    janela.configure(fg_color=FUNDO)

    try:
        janela.state("zoomed")
    except Exception:
        pass
