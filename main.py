
import customtkinter as ctk
import tkinter.messagebox as messagebox

import theme
from login import TelaLogin

from dashboard import mostrar_dashboard as carregar_dashboard
from produtos import mostrar_produtos
from movimentacoes import mostrar_movimentacoes
from fornecedores import mostrar_fornecedores
from relatorios import mostrar_relatorios

from compras_inteligentes import mostrar_compras_inteligentes
from auditoria import mostrar_auditoria
from inteligencia_abc import mostrar_inteligencia_abc
from alertas import mostrar_alertas


# O backup.py ainda pode estar vazio.
# Esta importacao opcional evita que isso impeça o sistema de abrir.
try:
    from backup import mostrar_backup
except ImportError:
    mostrar_backup = None


class EstoqueUltimate(ctk.CTk):

    def __init__(self, usuario=None, papel="usuario"):
        super().__init__()

        self.usuario_atual = usuario or "Usuario"
        self.papel_atual = papel or "usuario"

        theme.configurar_janela(self)

        self.sidebar = ctk.CTkFrame(
            self,
            width=235,
            corner_radius=0,
            fg_color=theme.SIDEBAR
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.conteudo = ctk.CTkFrame(
            self,
            fg_color=theme.FUNDO,
            corner_radius=0
        )
        self.conteudo.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.criar_sidebar()
        self.mostrar_dashboard()

        self.protocol("WM_DELETE_WINDOW", self.fechar_sistema)

    # =====================================================
    # MENU LATERAL
    # =====================================================

    def criar_sidebar(self):
        marca = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        marca.pack(
            fill="x",
            padx=18,
            pady=(25, 30)
        )

        ctk.CTkLabel(
            marca,
            text="EI",
            width=45,
            height=45,
            corner_radius=12,
            fg_color=theme.AZUL,
            text_color="white",
            font=("Segoe UI", 20, "bold")
        ).pack(side="left")

        textos = ctk.CTkFrame(
            marca,
            fg_color="transparent"
        )
        textos.pack(side="left", padx=10)

        ctk.CTkLabel(
            textos,
            text="Estoque Inteligente",
            font=("Segoe UI", 14, "bold"),
            text_color=theme.TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text="ULTIMATE • v2.0",
            font=("Segoe UI", 10),
            text_color=theme.SECUNDARIO
        ).pack(anchor="w", pady=(3, 0))

        ctk.CTkLabel(
            self.sidebar,
            text="GESTÃO DE ESTOQUE",
            font=("Segoe UI", 10, "bold"),
            text_color=theme.SECUNDARIO
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 10)
        )

        self.criar_item_menu(
            "Dashboard",
            self.mostrar_dashboard
        )
        self.criar_item_menu(
            "Produtos",
            self.pagina_produtos
        )
        self.criar_item_menu(
            "Entradas e saídas",
            self.pagina_movimentacoes
        )
        self.criar_item_menu(
            "Fornecedores",
            self.pagina_fornecedores
        )
        self.criar_item_menu(
            "Compras inteligentes",
            self.pagina_compras
        )
        self.criar_item_menu(
            "Auditoria e perdas",
            self.pagina_auditoria
        )
        self.criar_item_menu(
            "Classificação ABC",
            self.pagina_abc
        )
        self.criar_item_menu(
            "Alertas",
            self.pagina_alertas
        )
        self.criar_item_menu(
            "Relatórios",
            self.pagina_relatorios
        )
        self.criar_item_menu(
            "Backup",
            self.pagina_backup
        )

        ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        ).pack(fill="both", expand=True)

        rodape = ctk.CTkFrame(
            self.sidebar,
            fg_color=theme.CARD,
            corner_radius=12
        )
        rodape.pack(
            fill="x",
            padx=12,
            pady=15
        )

        ctk.CTkLabel(
            rodape,
            text=self.usuario_atual,
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXTO
        ).pack(
            anchor="w",
            padx=12,
            pady=(12, 3)
        )

        ctk.CTkLabel(
            rodape,
            text=f"Perfil: {self.papel_atual}",
            font=("Segoe UI", 10),
            text_color=theme.VERDE
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 12)
        )

        ctk.CTkButton(
            self.sidebar,
            text="Sair do sistema",
            height=38,
            fg_color="transparent",
            hover_color=theme.CARD_HOVER,
            text_color=theme.VERMELHO,
            command=self.fechar_sistema
        ).pack(fill="x", padx=12, pady=(0, 12))

    def criar_item_menu(self, texto, comando):
        ctk.CTkButton(
            self.sidebar,
            text=texto,
            command=comando,
            height=41,
            corner_radius=9,
            fg_color="transparent",
            hover_color=theme.CARD_HOVER,
            text_color=theme.TEXTO,
            font=("Segoe UI", 12),
            anchor="w"
        ).pack(fill="x", padx=12, pady=2)

    # =====================================================
    # NAVEGACAO
    # =====================================================

    def executar_pagina(self, funcao):
        self.limpar_conteudo()

        try:
            funcao(self)
        except Exception as erro:
            messagebox.showerror(
                "Erro ao abrir página",
                "Não foi possível abrir esta funcionalidade.\n\n"
                f"Detalhes: {erro}"
            )

    def limpar_conteudo(self):
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        self.executar_pagina(carregar_dashboard)

    def pagina_produtos(self):
        self.executar_pagina(mostrar_produtos)

    def pagina_movimentacoes(self):
        self.executar_pagina(mostrar_movimentacoes)

    def pagina_fornecedores(self):
        self.executar_pagina(mostrar_fornecedores)

    def pagina_relatorios(self):
        self.executar_pagina(mostrar_relatorios)

    def pagina_compras(self):
        self.executar_pagina(mostrar_compras_inteligentes)

    def pagina_auditoria(self):
        self.executar_pagina(mostrar_auditoria)

    def pagina_abc(self):
        self.executar_pagina(mostrar_inteligencia_abc)

    def pagina_alertas(self):
        self.executar_pagina(mostrar_alertas)

    def pagina_backup(self):
        if mostrar_backup is None:
            self.limpar_conteudo()

            ctk.CTkLabel(
                self.conteudo,
                text="Backup do sistema",
                font=("Segoe UI", 26, "bold"),
                text_color=theme.TEXTO
            ).pack(anchor="w", padx=30, pady=(30, 10))

            ctk.CTkLabel(
                self.conteudo,
                text=(
                    "O módulo de backup ainda precisa ser implementado.\n"
                    "As demais funcionalidades continuam disponíveis."
                ),
                font=("Segoe UI", 13),
                text_color=theme.SECUNDARIO,
                justify="left"
            ).pack(anchor="w", padx=30, pady=10)
            return

        self.executar_pagina(mostrar_backup)

    # =====================================================
    # ENCERRAMENTO
    # =====================================================

    def fechar_sistema(self):
        if messagebox.askyesno(
            "Sair",
            "Deseja realmente fechar o Estoque Inteligente Ultimate?"
        ):
            self.destroy()


# =========================================================
# INICIALIZACAO: LOGIN PRIMEIRO, SISTEMA DEPOIS
# =========================================================

def iniciar_sistema():
    sessao = {}

    def autenticar(usuario, papel):
        sessao["usuario"] = usuario
        sessao["papel"] = papel
        login.quit()

    login = TelaLogin(ao_entrar=autenticar)

    if not login.verificar_banco():
        login.destroy()
        return

    login.mainloop()

    # O dashboard so abre quando o login for validado.
    if sessao.get("usuario"):
        app = EstoqueUltimate(
            usuario=sessao["usuario"],
            papel=sessao["papel"]
        )
        app.mainloop()


if __name__ == "__main__":
    iniciar_sistema()
