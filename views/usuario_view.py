import panel as pn
import pandas as pd
from dao.usuario_dao import (
    buscar_usuarios_no_banco, salvar_usuario_no_banco, 
    atualizar_usuario_no_banco, deletar_usuario_no_banco, buscar_usuario_por_id
)

def obter_df_usuarios(filtro=""):
    dados = buscar_usuarios_no_banco(filtro)
    return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Nome", "E-mail", "Status"])

def tela_usuario():
    # Componentes Visuais
    input_id = pn.widgets.TextInput(visible=False)
    input_p_nome = pn.widgets.TextInput(name="Primeiro Nome*", placeholder="Ex: Gildean")
    input_sobrenome = pn.widgets.TextInput(name="Sobrenome", placeholder="Ex: Silva")
    input_email = pn.widgets.TextInput(name="E-mail*", placeholder="exemplo@email.com")
    input_senha = pn.widgets.PasswordInput(name="Senha*", placeholder="Digite a senha de acesso")
    
    btn_salvar = pn.widgets.Button(name="💾 Salvar Novo", button_type="success", sizing_mode="stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)
    input_filtro = pn.widgets.TextInput(placeholder="Filtrar por nome...", width=250)
    btn_filtrar = pn.widgets.Button(name="🔍 Filtrar", button_type="primary", width=80)
    
    tabela = pn.widgets.Tabulator(obter_df_usuarios(), page_size=5, selectable=True, sizing_mode="stretch_width")
    alerta = pn.pane.Alert("", alert_type="success", visible=False)

    def exibir_alerta(mensagem, tipo="success"):
        alerta.object, alerta.alert_type, alerta.visible = mensagem, tipo, True

    def limpar_form():
        input_id.value, input_p_nome.value, input_sobrenome.value, input_email.value, input_senha.value = "", "", "", "", ""
        btn_salvar.visible = True
        btn_atualizar.visible, btn_cancelar.visible = False, False

    def ao_clicar_salvar(event):
        if not input_p_nome.value or not input_email.value or not input_senha.value:
            exibir_alerta("⚠️ Preencha os campos obrigatórios (*).", "danger")
            return
        
        sucesso, msg = salvar_usuario_no_banco(input_p_nome.value, input_sobrenome.value, input_email.value, input_senha.value)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_usuarios()
            limpar_form()

    def ao_clicar_carregar_edicao(event):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha na tabela para editar.", "warning")
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        u = buscar_usuario_por_id(id_alvo)
        
        if u:
            input_id.value = str(u.id_usuario)
            input_p_nome.value = u.primeiro_nome
            input_sobrenome.value = u.sobrenome or ""
            input_email.value = u.email
            input_senha.value = u.senha
            
            btn_salvar.visible = False
            btn_atualizar.visible, btn_cancelar.visible = True, True
            exibir_alerta("✏️ Modo de edição ativado.", "info")

    def ao_clicar_atualizar(event):
        sucesso, msg = atualizar_usuario_no_banco(input_id.value, input_p_nome.value, input_sobrenome.value, input_email.value, input_senha.value)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_usuarios()
            limpar_form()

    def ao_clicar_deletar(event):
        if not tabela.selection:
            exibir_alerta("⚠️ Selecione uma linha na tabela para deletar.", "warning")
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        sucesso, msg = deletar_usuario_no_banco(id_alvo)
        exibir_alerta(msg, "success" if sucesso else "danger")
        if sucesso:
            tabela.value = obter_df_usuarios()

    # Mapeamento de Eventos
    btn_salvar.on_click(ao_clicar_salvar)
    btn_editar_tb.on_click(ao_clicar_carregar_edicao)
    btn_atualizar.on_click(ao_clicar_atualizar)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_deletar_tb.on_click(ao_clicar_deletar)
    btn_filtrar.on_click(lambda e: setattr(tabela, 'value', obter_df_usuarios(input_filtro.value)))

    # Montagem da Estrutura Visual
    form_card = pn.Card(pn.Column(input_p_nome, input_sobrenome, input_email, input_senha, btn_salvar, btn_atualizar, btn_cancelar), title="📝 Formulário de Usuário", sizing_mode="stretch_width")
    grid_busca = pn.Column(pn.Row(input_filtro, btn_filtrar, align="end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb), sizing_mode="stretch_width")
    
    return pn.Column(pn.pane.Markdown("# 👥 Gestão de Usuários"), alerta, pn.Row(pn.Column(form_card, width=350), grid_busca, sizing_mode="stretch_width"), sizing_mode="stretch_width")