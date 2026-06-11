import panel as pn
import pandas as pd
from dao.encontro_dao import buscar_encontros_no_banco, salvar_encontro_no_banco
from dao.grupo_dao import buscar_grupos_no_banco


def obter_df(filtro = ""):
    dados = buscar_encontros_no_banco(filtro)
    return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Título", "Início", "Fim", "Status", "ID Grupo"])

def tela_encontro():
    grupos = buscar_grupos_no_banco()
    opcoes_grupos = {g["Nome"]: g["ID"] for g in grupos} if grupos else {"Nenhum grupo": None}

    input_titulo = pn.widgets.TextInput(name = "Título*", placeholder = "Ex: Daily Scrum")
    input_desc = pn.widgets.TextAreaInput(name = "Descrição", placeholder = "Pauta...")
    select_grupo = pn.widgets.Select(name = "Grupo Destino*", options = opcoes_grupos)

    input_inicio = pn.widgets.DatetimePicker(name = "Início*")
    input_fim = pn.widgets.DatetimePicker(name = "Fim*")
    select_status = pn.widgets.Select(name = "Status*", options = ["AGENDADO", "EM_ANDAMENTO", "FINALIZADO", "CANCELADO"])
    input_limite = pn.widgets.IntInput(name = "Participantes", value = 10, start = 1)

    btn_salvar = pn.widgets.Button(name = "💾 Agendar", button_type = "success", sizing_mode = "stretch_width")
    input_filtro = pn.widgets.TextInput(placeholder = "Filtrar...", width = 250)
    btn_filtrar = pn.widgets.Button(name = "🔍", button_type = "primary", width = 50)


    tabela = pn.widgets.Tabulator(obter_df(), page_size = 5, sizing_mode = "stretch_width")
    alerta = pn.pane.Alert("", alert_type = "success", visible = False)

    def salvar(e):
        if not input_titulo.value or not select_grupo.value or not input_inicio.value or not input_fim.value:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Preencha os campos (*).", "danger", True
            return 

        sucesso, msg = salvar_encontro_no_banco(
            input_titulo.value, input_desc.value, input_inicio.value,
            input_fim.value, select_status.value, input_limite.value, select_grupo.value
        )

        alerta.object, alerta.alert_type, alerta.visible = msg, "success" if sucesso else "danger", True
        if sucesso:
            tabela.value = obter_df()

    btn_salvar.on_click(salvar)
    btn_filtrar.on_click(lambda e: setattr(tabela, "value", obter_df(input_filtro.value)))

    form = pn.Card(pn.Column(input_titulo, input_desc, select_grupo, input_inicio, input_fim, select_status, input_limite, btn_salvar), title = "📅 Novo Encontro", sizing_mode = "stretch_width")
    grid = pn.Column(pn.Row(input_filtro, btn_filtrar, align = "end"), tabela, sizing_mode = "stretch_width")

    return pn.Column(pn.pane.Markdown("# 📅 Encontros"), alerta, pn.Row(pn.Column(form, width = 350), grid, sizing_mode = "stretch_width"), sizing_mode = "stretch_width")
        

