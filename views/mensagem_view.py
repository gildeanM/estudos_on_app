import panel as pn
import pandas as pd 
from dao.mensagem_dao import buscar_mensagens_no_banco, salvar_mensagem_no_banco
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


    input_conteudo = pn.widgets.TextAreaInput(name = "Mensagem*", placeholder = "Escreva aqui...")
    select_tipo = pn.widgets.Select(name = "Tipo*", options = ["TEXTO", "AVISO", "SISTEMA"])
    select_autor = pn.widgets.Select(name = "Autor (Simulação)*", options = opcoes_usuarios)
    select_grupo = pn.widgets.Select(name = "Enviar para o Grupo", options = opcoes_grupos)

    btn_salvar = pn.widgets.Button(name = "📨 Enviar Mensagem", button_type = "success", sizing_mode = "stretch_width")
    input_filtro = pn.widgets.TextInput(placeholder = "Filtrar por conteúdo...", width = 250)
    btn_filtrar = pn.widgets.Button(name = "🔍", button_type = "primary", width = 50)

    tabela = pn.widgets.Tabulator(obter_df(), page_size = 5, sizing_mode = "stretch_width")
    alerta = pn.pane.Alert("", alert_type = "success", visible = False)

    def salvar(e):
        if not input_conteudo.value or not select_autor.value or not select_grupo.value:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Preencha os campos obrigatórios.", "danger", True
            return 
        
        sucesso, msg = salvar_mensagem_no_banco(input_conteudo.value, select_tipo.value, select_autor.value, select_grupo.value)
        alerta.object, alerta.alert_type, alerta.visible = msg, "success" if sucesso else "danger", True

        if sucesso:
            tabela.value = obter_df()
            input_conteudo.value = ""
    
    btn_salvar.on_click(salvar)
    btn_filtrar.on_click(lambda e: setattr(tabela, 'value', obter_df(input_filtro.value)))

    form = pn.Card(pn.Column(select_autor, select_grupo, select_tipo, input_conteudo, btn_salvar), title = "💬 Nova Mensagem", sizing_mode = "stretch_width")
    grid = pn.Column(pn.Row(input_filtro, btn_filtrar, align = "end"), tabela, sizing_mode = "stretch_width")

    return pn.Column(pn.pane.Markdown("# 💬 Mensagens"), alerta, pn.Row(pn.Column(form, width = 350), grid, sizing_mode = "stretch_width"), sizing_mode = "stretch_width")