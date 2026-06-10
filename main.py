import panel as pn
from views.usuario_view import tela_usuario
from views.grupo_view import tela_grupo

pn.extension('tabulator', sizing_mode="stretch_width")


def tela_encontro(): return pn.Column(pn.pane.Markdown("# 📅 Gestão de Encontros"), pn.pane.Alert("Aguardando Dia 4", alert_type="warning"))
def tela_mensagem(): return pn.Column(pn.pane.Markdown("# 💬 Histórico de Mensagens"), pn.pane.Alert("Aguardando Dia 4", alert_type="warning"))
def tela_relatorios(): return pn.Column(pn.pane.Markdown("# 📊 Relatórios"), pn.pane.Alert("Aguardando Sprint 2", alert_type="info"))

def roteador_de_telas(aba_selecionada):
    if aba_selecionada == "Usuários": return tela_usuario()
    elif aba_selecionada == "Grupos": return tela_grupo()
    elif aba_selecionada == "Encontros": return tela_encontro()
    elif aba_selecionada == "Mensagens": return tela_mensagem()
    elif aba_selecionada == "Relatórios": return tela_relatorios()
    return pn.pane.Markdown("# ❌ Erro: Tela não encontrada.")

menu_navegacao = pn.widgets.RadioButtonGroup(
    options=["Usuários", "Grupos", "Encontros", "Mensagens", "Relatórios"],
    button_type="success", orientation="vertical", sizing_mode="stretch_width"
)

conteudo_dinamico = pn.bind(roteador_de_telas, menu_navegacao)

template = pn.template.FastListTemplate(
    title="Estudos On — Painel de Gestão",
    sidebar=[pn.pane.Markdown("## 📌 Navegação"), menu_navegacao, pn.layout.Divider()],
    main=[conteudo_dinamico],
    accent_base_color="#2ecc71", header_background="#2c3e50"
)

app = template