import panel as pn
import pandas as pd
from dao.grupo_dao import (
    buscar_grupos_no_banco, salvar_grupo_no_banco,
    atualizar_grupo_no_banco, deletar_grupo_no_banco
)

def obter_df_grupos(filtro=""):
    dados = buscar_grupos_no_banco(filtro)
    return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Nome", "Descrição", "Privacidade", "Limite"])

def tela_grupo():
    # Componentes Visuais
    input_id = pn.widgets.TextInput(visible=False)
    input_nome = pn.widgets.TextInput(name="Nome do Grupo*", placeholder="Ex: Engenharia de Software")
    input_desc = pn.widgets.TextAreaInput(name="Descrição", placeholder="Sobre o que é...")
    select_privacidade = pn.widgets.Select(name="Privacidade*", options={"Público": "PUBLICO", "Privado": "PRIVADO", "Restrito": "RESTRITO"})
    input_limite = pn.widgets.IntInput(name="Limite de Membros*", value=10, start=1)
    
    btn_salvar = pn.widgets.Button(name="💾 Salvar Grupo", button_type="success", sizing_mode="stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)
    input_filtro = pn.widgets.TextInput(placeholder="Filtrar por nome...", width=250)
    btn_filtrar = pn.widgets.Button(name="🔍 Filtrar", button_type="primary", width=80)
    
    tabela = pn.widgets.Tabulator(obter_df_grupos(), page_size=5, selectable=True, sizing_mode="stretch_width")
    alerta = pn.pane.Alert("", alert_type="success", visible=False)

    def exibir_alerta(mensagem, tipo="success"):
        alerta.object, alerta.alert_type, alerta.visible = mensagem, tipo, True

    def limpar_form():
        input_id.value, input_nome.value, input_desc.value, input_limite.value = "", "", "", 10
        btn_salvar.visible = True
        btn_atualizar.visible, btn_cancelar.visible = False, False

    def ao_clicar_salvar(event):
        if not input_nome.value:
            exibir_alerta("⚠️ O nome do grupo é obrigatório.", "danger")
            return
        
        sucesso, msg = salvar_grupo_no_banco(input_nome.value, input_desc.value, select_privacidade.value, input_limite.value)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_grupos()
            limpar_form()

    def ao_clicar_carregar_edicao(event):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha na tabela para editar.", "warning")
            return
        
        linha = tabela.value.iloc[tabela.selection[0]]
        input_id.value = str(linha["ID"])
        input_nome.value = linha["Nome"]
        input_desc.value = linha["Descrição"]
        select_privacidade.value = linha["Privacidade"]
        input_limite.value = int(linha["Limite"])
        
        btn_salvar.visible = False
        btn_atualizar.visible, btn_cancelar.visible = True, True
        exibir_alerta("✏️ Modo de edição ativado.", "info")

    def ao_clicar_atualizar(event):
        sucesso, msg = atualizar_grupo_no_banco(input_id.value, input_nome.value, input_desc.value, select_privacidade.value, input_limite.value)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_grupos()
            limpar_form()

    def ao_clicar_deletar(event):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha na tabela para deletar.", "warning")
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        sucesso, msg = deletar_grupo_no_banco(id_alvo)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_grupos()

    # Mapeamento de Eventos
    btn_salvar.on_click(ao_clicar_salvar)
    btn_editar_tb.on_click(ao_clicar_carregar_edicao)
    btn_atualizar.on_click(ao_clicar_atualizar)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_deletar_tb.on_click(ao_clicar_deletar)
    btn_filtrar.on_click(lambda e: setattr(tabela, 'value', obter_df_grupos(input_filtro.value)))

    # Montagem da Estrutura Visual
    form_card = pn.Card(pn.Column(input_nome, input_desc, select_privacidade, input_limite, btn_salvar, btn_atualizar, btn_cancelar), title="📝 Formulário de Grupo", sizing_mode="stretch_width")
    grid_busca = pn.Column(pn.Row(input_filtro, btn_filtrar, align="end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb), sizing_mode="stretch_width")
    
    return pn.Column(pn.pane.Markdown("# 🏫 Gestão de Grupos"), alerta, pn.Row(pn.Column(form_card, width=350), grid_busca, sizing_mode="stretch_width"), sizing_mode="stretch_width")