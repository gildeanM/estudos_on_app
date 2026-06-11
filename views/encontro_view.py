import panel as pn
import pandas as pd
from dao.encontro_dao import (
    buscar_encontros_no_banco, salvar_encontro_no_banco,
    atualizar_encontro_no_banco, deletar_encontro_no_banco, buscar_encontro_por_id
)
from dao.grupo_dao import buscar_grupos_no_banco

def obter_df(filtro=""):
    dados = buscar_encontros_no_banco(filtro)

    return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Título", "Início", "Fim", "Status", "ID Grupo"])

def tela_encontro():
    grupos = buscar_grupos_no_banco()
    opcoes_grupos = {g["Nome"]: g["ID"] for g in grupos} if grupos else {"Nenhum grupo": None}
    
    input_id = pn.widgets.TextInput(visible=False)
    input_titulo = pn.widgets.TextInput(name="Título*", placeholder="Ex: Daily Scrum")
    input_desc = pn.widgets.TextAreaInput(name="Descrição", placeholder="Pauta...")
    select_grupo = pn.widgets.Select(name="Grupo Destino*", options=opcoes_grupos)
    
    input_inicio = pn.widgets.DatetimePicker(name="Início*")
    input_fim = pn.widgets.DatetimePicker(name="Fim*")
    select_status = pn.widgets.Select(name="Status*", options=["AGENDADO", "EM_ANDAMENTO", "FINALIZADO", "CANCELADO"])
    input_limite = pn.widgets.IntInput(name="Participantes", value=10, start=1)
    
    btn_salvar = pn.widgets.Button(name="💾 Agendar", button_type="success", sizing_mode="stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)
    input_filtro = pn.widgets.TextInput(placeholder="Filtrar por título...", width=250)
    btn_filtrar = pn.widgets.Button(name="🔍", button_type="primary", width=50)
    
    tabela = pn.widgets.Tabulator(obter_df(), page_size=5, selectable=True, sizing_mode="stretch_width")
    alerta = pn.pane.Alert("", alert_type="success", visible=False)

    def exibir_alerta(mensagem, tipo="success"):
        alerta.object, alerta.alert_type, alerta.visible = mensagem, tipo, True

    def limpar_form():
        input_id.value, input_titulo.value, input_desc.value, input_limite.value = "", "", "", 10
        btn_salvar.visible = True
        btn_atualizar.visible, btn_cancelar.visible = False, False

    def salvar(e):
        if not input_titulo.value or not select_grupo.value or not input_inicio.value or not input_fim.value:
            exibir_alerta("⚠️ Preencha os campos (*).", "danger")
            return
        sucesso, msg = salvar_encontro_no_banco(
            input_titulo.value, input_desc.value, input_inicio.value, 
            input_fim.value, select_status.value, input_limite.value, select_grupo.value
        )
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df()
            limpar_form()

    def carregar_edicao(e):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione um encontro na tabela para editar.", "warning")
            return
                
        id_real = tabela.value.iloc[tabela.selection[0]]["ID"]
        e_obj = buscar_encontro_por_id(id_real)
        
        if e_obj:
            input_id.value = str(e_obj.id_encontro)
            input_titulo.value = e_obj.titulo
            input_desc.value = e_obj.descricao or ""
            input_inicio.value = e_obj.data_hora_inicio
            input_fim.value = e_obj.data_hora_fim
            select_status.value = e_obj.status
            input_limite.value = e_obj.limite_participantes or 10
            select_grupo.value = e_obj.id_grupo
            
            btn_salvar.visible = False
            btn_atualizar.visible, btn_cancelar.visible = True, True
            exibir_alerta("✏️ Modo de edição ativado.", "info")

    def atualizar(e):
        sucesso, msg = atualizar_encontro_no_banco(
            input_id.value, input_titulo.value, input_desc.value, input_inicio.value,
            input_fim.value, select_status.value, input_limite.value, select_grupo.value
        )
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df()
            limpar_form()

    def deletar(e):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha para deletar.", "warning")
            return
        
        id_real = tabela.value.iloc[tabela.selection[0]]["ID"]
        sucesso, msg = deletar_encontro_no_banco(id_real)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df()

    btn_salvar.on_click(salvar)
    btn_editar_tb.on_click(carregar_edicao)
    btn_atualizar.on_click(atualizar)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_deletar_tb.on_click(deletar)
    btn_filtrar.on_click(lambda e: setattr(tabela, 'value', obter_df(input_filtro.value)))

    form = pn.Card(pn.Column(input_titulo, input_desc, select_grupo, input_inicio, input_fim, select_status, input_limite, btn_salvar, btn_atualizar, btn_cancelar), title="📅 Novo Encontro", sizing_mode="stretch_width")
    grid = pn.Column(pn.Row(input_filtro, btn_filtrar, align="end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb), sizing_mode="stretch_width")
    
    return pn.Column(pn.pane.Markdown("# 📅 Encontros"), alerta, pn.Row(pn.Column(form, width=350), grid, sizing_mode="stretch_width"), sizing_mode="stretch_width")