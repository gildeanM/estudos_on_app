import panel as pn
import pandas as pd 
from dao.mensagem_dao import (
    buscar_mensagens_no_banco, salvar_mensagem_no_banco,
    atualizar_mensagem_no_banco, deletar_mensagem_no_banco, buscar_mensagem_por_id
)
from dao.grupo_dao import buscar_grupos_no_banco
from dao.usuario_dao import buscar_usuarios_no_banco



def obter_df(filtro = ""):
    dados = buscar_mensagens_no_banco(filtro)
    return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Conteúdo", "Tipo", "Envio", "Autor ID"])


def tela_mensagem():
    grupos = buscar_grupos_no_banco()
    usuarios = buscar_usuarios_no_banco()

    opcoes_grupos = {g["Nome"]: g["ID"] for g in grupos} if grupos else {"Nenhum grupo": None}
    opcoes_usuarios = {u["Nome"]: u["ID"] for u in usuarios} if usuarios else {"Nenhum usuário": None}

    input_id = pn.widgets.TextInput(visible=False)
    input_conteudo = pn.widgets.TextAreaInput(name = "Mensagem*", placeholder = "Escreva aqui...")
    select_tipo = pn.widgets.Select(name = "Tipo*", options = ["TEXTO", "AVISO", "SISTEMA"])
    select_autor = pn.widgets.Select(name = "Autor (Simulação)*", options = opcoes_usuarios)
    select_grupo = pn.widgets.Select(name = "Enviar para o Grupo", options = opcoes_grupos)

    btn_salvar = pn.widgets.Button(name = "📨 Enviar Mensagem", button_type = "success", sizing_mode = "stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)
    input_filtro = pn.widgets.TextInput(placeholder = "Filtrar por conteúdo...", width = 250)
    btn_filtrar = pn.widgets.Button(name = "🔍", button_type = "primary", width = 50)

    tabela = pn.widgets.Tabulator(obter_df(), page_size = 5, sizing_mode = "stretch_width")
    alerta = pn.pane.Alert("", alert_type = "success", visible = False)

    def exibir_alerta(mensagem, tipo="success"):
        alerta.object, alerta.alert_type, alerta.visible = mensagem, tipo, True

    def limpar_form():
        input_id.value, input_conteudo.value = "", ""
        btn_salvar.visible = True
        btn_atualizar.visible, btn_cancelar.visible = False, False

    def salvar(m):
        if not input_conteudo.value or not select_autor.value or not select_grupo.value:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Preencha os campos obrigatórios.", "danger", True
            return 
        
        sucesso, msg = salvar_mensagem_no_banco(input_conteudo.value, select_tipo.value, select_autor.value, select_grupo.value)
        exibir_alerta(msg, "success" if sucesso else "danger")

        if sucesso:
            tabela.value = obter_df()
            limpar_form()

    def carregar_edicao(m):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma mensagem para editar.", "warning")
            return
                
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        m_obj = buscar_mensagem_por_id(id_alvo)
        
        if m_obj:
            input_id.value = str(m_obj.id_mensagem)
            input_conteudo.value = m_obj.conteudo    
            select_tipo.value = m_obj.tipo_mensagem            
            select_autor.value = m_obj.id_usuario            
            select_grupo.value = m_obj.id_grupo
            
            btn_salvar.visible = False
            btn_atualizar.visible, btn_cancelar.visible = True, True
            exibir_alerta("✏️ Modo de edição de mensagem ativado.", "info")
    
    def atualizar(m):
        sucesso, msg = atualizar_mensagem_no_banco(input_id.value, input_conteudo.value, select_tipo.value, select_autor.value, select_grupo.value)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df()
            limpar_form()
    
    def deletar(m):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha para deletar.", "warning")
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        sucesso, msg = deletar_mensagem_no_banco(id_alvo)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df()

    btn_salvar.on_click(salvar)
    btn_editar_tb.on_click(carregar_edicao)
    btn_atualizar.on_click(atualizar)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_deletar_tb.on_click(deletar)
    btn_filtrar.on_click(lambda e: setattr(tabela, 'value', obter_df(input_filtro.value)))

    form = pn.Card(pn.Column(select_autor, select_grupo, select_tipo, input_conteudo, btn_salvar, btn_atualizar, btn_cancelar), title = "💬 Nova Mensagem", sizing_mode = "stretch_width")
    grid = pn.Column(pn.Row(input_filtro, btn_filtrar, align = "end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb),sizing_mode = "stretch_width")

    return pn.Column(pn.pane.Markdown("# 💬 Mensagens"), alerta, pn.Row(pn.Column(form, width = 350), grid, sizing_mode = "stretch_width"), sizing_mode = "stretch_width")