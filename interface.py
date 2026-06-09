import panel as pn
import pandas as pd
from sqlalchemy.exc import IntegrityError
from database.connection import get_sqlalchemy_session
from models.entities import Usuario, Grupo

pn.extension('tabulator', sizing_mode="stretch_width")

# =====================================================================
# CAMADA DE DADOS: FUNÇÕES DE BUSCA (Ajustadas para o Schema Real)
# =====================================================================

def buscar_usuarios_do_banco(nome_filtro=""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Usuario)
        if nome_filtro:
            # Filtra combinando primeiro_nome ou sobrenome
            query = query.filter(
                Usuario.primeiro_nome.ilike(f"%{nome_filtro}%") | 
                Usuario.sobrenome.ilike(f"%{nome_filtro}%")
            )
        usuarios = query.all()
        dados = [u.to_dict() for u in usuarios]
        return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Nome", "E-mail", "Status"])
    finally:
        session.close()

def buscar_grupos_do_banco(nome_filtro=""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Grupo)
        if nome_filtro:
            query = query.filter(Grupo.nome.ilike(f"%{nome_filtro}%"))
        grupos = query.all()
        dados = [g.to_dict() for g in grupos]
        return pd.DataFrame(dados) if dados else pd.DataFrame(columns=["ID", "Nome", "Descrição", "Privacidade", "Limite"])
    finally:
        session.close()

# =====================================================================
# TELA DE USUÁRIOS (Membro A - Ajustada para primeiro_nome/sobrenome)
# =====================================================================
def tela_usuario():
    input_id = pn.widgets.TextInput(visible=False)
    input_p_nome = pn.widgets.TextInput(name="Primeiro Nome*", placeholder="Ex: Gildean")
    input_sobrenome = pn.widgets.TextInput(name="Sobrenome", placeholder="Ex: Silva")
    input_email = pn.widgets.TextInput(name="E-mail*", placeholder="exemplo@email.com")
    input_senha = pn.widgets.PasswordInput(name="Senha*", placeholder="Digite a senha de acesso")

    btn_salvar = pn.widgets.Button(name="💾 Salvar Usuário", button_type="success", sizing_mode="stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)
    
    input_filtro = pn.widgets.TextInput(placeholder="Filtrar por nome...", width=250)
    btn_filtrar = pn.widgets.Button(name="🔍 Filtrar", button_type="primary", width=80)
    
    df_inicial = buscar_usuarios_do_banco()
    tabela = pn.widgets.Tabulator(buscar_usuarios_do_banco(), page_size=5, selectable=True, sizing_mode="stretch_width")
    alerta = pn.pane.Alert("", alert_type="success", visible=False)


    def limpar_form():
        input_id.value = ""
        input_p_nome.value = ""
        input_sobrenome.value = ""
        input_email.value = ""
        input_senha.value = ""
        btn_salvar.visible = True
        btn_atualizar.visible = False
        btn_cancelar.visible = False

    def salvar_usuario(event):
            if not input_p_nome.value or not input_email.value or not input_senha.value:
                alerta.object, alerta.alert_type, alerta.visible = "⚠️ Preencha os campos obrigatórios (*).", "danger", True
                return
            
            session = get_sqlalchemy_session()
            try:
                novo_u = Usuario(primeiro_nome=input_p_nome.value, sobrenome=input_sobrenome.value, email=input_email.value, senha=input_senha.value, status="Ativo")
                session.add(novo_u)
                session.commit()
                alerta.object, alerta.alert_type, alerta.visible = "✅ Usuário cadastrado!", "success", True
                tabela.value = buscar_usuarios_do_banco()
                limpar_form()
            except IntegrityError:
                session.rollback()
                alerta.object, alerta.alert_type, alerta.visible = "⚠️ Erro: E-mail já cadastrado ou dado inválido.", "danger", True
            finally:
                session.close()

    def carregar_para_edicao(event):
        if not tabela.selection:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Selecione uma linha na tabela para editar.", "warning", True
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        session = get_sqlalchemy_session()
        u = session.query(Usuario).get(id_alvo)
        session.close()
        
        if u:
            input_id.value = str(u.id_usuario)
            input_p_nome.value = u.primeiro_nome
            input_sobrenome.value = u.sobrenome or ""
            input_email.value = u.email
            input_senha.value = u.senha
            
            btn_salvar.visible = False
            btn_atualizar.visible = True
            btn_cancelar.visible = True
            alerta.object, alerta.alert_type, alerta.visible = "✏️ Modo de edição ativado.", "info", True

    def atualizar_usuario(event):
        session = get_sqlalchemy_session()
        try:
            u = session.query(Usuario).get(input_id.value)
            if u:
                u.primeiro_nome = input_p_nome.value
                u.sobrenome = input_sobrenome.value
                u.email = input_email.value
                if input_senha.value: u.senha = input_senha.value
                session.commit()
                alerta.object, alerta.alert_type, alerta.visible = "✅ Usuário atualizado!", "success", True
                tabela.value = buscar_usuarios_do_banco()
                limpar_form()
        except IntegrityError:
            session.rollback()
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Erro de integridade ao atualizar.", "danger", True
        finally:
            session.close()

    def deletar_usuario(event):
        if not tabela.selection:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Selecione uma linha na tabela para deletar.", "warning", True
            return
        
        id_alvo = tabela.value.iloc[tabela.selection[0]]["ID"]
        session = get_sqlalchemy_session()
        try:
            u = session.query(Usuario).get(id_alvo)
            session.delete(u)
            session.commit()
            alerta.object, alerta.alert_type, alerta.visible = "🗑️ Usuário removido com sucesso!", "success", True
            tabela.value = buscar_usuarios_do_banco()
        except IntegrityError: 
            session.rollback()
            alerta.object, alerta.alert_type, alerta.visible = "⛔ Negado: Este usuário possui vínculo com grupos ou mensagens. Remova as dependências primeiro.", "danger", True
        finally:
            session.close() 

    btn_salvar.on_click(salvar_usuario)
    btn_atualizar.on_click(atualizar_usuario)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_editar_tb.on_click(carregar_para_edicao)
    btn_deletar_tb.on_click(deletar_usuario)
    btn_filtrar.on_click(lambda e: setattr(tabela, "value", buscar_usuarios_do_banco(input_filtro.value)))


    form_card = pn.Card(pn.Column(input_p_nome, input_sobrenome, input_email, input_senha, btn_salvar, btn_atualizar, btn_cancelar), title="📝 Cadastrar Novo Usuário", sizing_mode="stretch_width")
    grid_busca = pn.Column(pn.Row(input_filtro, btn_filtrar, align="end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb),sizing_mode="stretch_width")
    
    return pn.Column(pn.pane.Markdown("# 👥 Gestão de Usuários"), alerta, pn.Row(pn.Column(form_card, width=350), grid_busca, sizing_mode="stretch_width"), sizing_mode="stretch_width")

# =====================================================================
# TELA DE GRUPOS (Membro B)
# =====================================================================
def tela_grupo():
    input_id = pn.widgets.TextInput(visible=False)
    input_nome = pn.widgets.TextInput(name="Nome do Grupo*", placeholder="Ex: Engenharia de Software 2026")
    input_desc = pn.widgets.TextAreaInput(name="Descrição (Opcional)", placeholder="Sobre o que é...")
    
    # Opções ajustadas exatamente para passar na restrição CHECK do banco
    select_privacidade = pn.widgets.Select(
        name="Privacidade*", 
        options={"Público": "PUBLICO", "Privado": "PRIVADO", "Restrito": "RESTRITO"}, 
        value="PUBLICO"
    )
    
    # Campo obrigatório para evitar o NotNullViolation
    input_limite = pn.widgets.IntInput(name="Limite de Membros*", value=10, start=1)
    
    btn_salvar = pn.widgets.Button(name="💾 Salvar Grupo", button_type="success", sizing_mode="stretch_width")
    btn_atualizar = pn.widgets.Button(name="🔄 Confirmar Atualização", button_type="primary", sizing_mode="stretch_width", visible=False)
    btn_cancelar = pn.widgets.Button(name="❌ Cancelar Edição", button_type="default", sizing_mode="stretch_width", visible=False)

    btn_editar_tb = pn.widgets.Button(name="✏️ Editar Selecionado", button_type="warning", width=160)
    btn_deletar_tb = pn.widgets.Button(name="🗑️ Deletar Selecionado", button_type="danger", width=160)    
    
    input_filtro = pn.widgets.TextInput(placeholder="Filtrar por nome...", width=250)
    btn_filtrar = pn.widgets.Button(name="🔍 Filtrar", button_type="primary", width=80)
    
    df_inicial = buscar_grupos_do_banco()
    tabela = pn.widgets.Tabulator(df_inicial, page_size=5, sizing_mode="stretch_width", disabled=True)
    alerta = pn.pane.Alert("", alert_type="success", visible=False)

    def limpar_form():
        input_id.value = ""
        input_nome.value = ""
        input_desc.value = ""
        input_limite.value = 10
        btn_salvar.visible = True
        btn_atualizar.visible = False
        btn_cancelar.visible = False

    def salvar_grupo(event):
        if not input_nome.value or not input_limite.value:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Os campos Nome e Limite de Membros são obrigatórios.", "danger", True             
            return
        
        if input_limite.value <= 0:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ O limite de membros deve ser maior que zero.", "danger", True            
            return
        
        session = get_sqlalchemy_session()
        try:
            novo_g = Grupo(
                nome=input_nome.value, 
                descricao=input_desc.value,
                privacidade=select_privacidade.value,  # Envia 'PUBLICO', 'PRIVADO' ou 'RESTRITO'
                limite_membros=input_limite.value
            )
            session.add(novo_g)
            session.commit()                    
                        
            alerta.object, alerta.alert_type, alerta.visible = "✅ Grupo criado com sucesso respeitando todas as restrições!", "success", True            
            tabela.value = buscar_grupos_do_banco()
            limpar_form()
        except IntegrityError:
            session.rollback()            
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Erro nas restrições de integridade.", "danger", True
        finally:
            session.close()

    def carregar_para_edicao(event):
        if not tabela.selection:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Selecione uma linha na tabela para editar.", "warning", True
            return
        
        id_alvo = int(tabela.value.iloc[tabela.selection[0]]["ID"])
        session = get_sqlalchemy_session()
        g = session.query(Grupo).get(id_alvo)
        session.close()
        
        if g:
            input_id.value = str(g.id_grupo)
            input_nome.value = g.nome
            input_desc.value = g.descricao or ""
            select_privacidade.value = g.privacidade
            input_limite.value = g.limite_membros
            
            btn_salvar.visible = False
            btn_atualizar.visible = True
            btn_cancelar.visible = True
            alerta.object, alerta.alert_type, alerta.visible = "✏️ Modo de edição ativado.", "info", True
    

    def atualizar_grupo(event):
        session = get_sqlalchemy_session()
        try:
            g = session.query(Grupo).get(input_id.value)
            if g:
                g.nome = input_nome.value
                g.descricao = input_desc.value
                g.privacidade = select_privacidade.value
                g.limite_membros = input_limite.value
                session.commit()
                alerta.object, alerta.alert_type, alerta.visible = "✅ Grupo atualizado!", "success", True
                tabela.value = buscar_grupos_do_banco()
                limpar_form()
        except IntegrityError:
            session.rollback()
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Erro de integridade.", "danger", True
        finally:
            session.close()

    def deletar_grupo(event):
        if not tabela.selection:
            alerta.object, alerta.alert_type, alerta.visible = "⚠️ Selecione uma linha na tabela para deletar.", "warning", True
            return
        
        id_alvo = int(tabela.value.iloc[tabela.selection[0]]["ID"])
        session = get_sqlalchemy_session()
        try:
            g = session.query(Grupo).get(id_alvo)
            session.delete(g)
            session.commit()
            alerta.object, alerta.alert_type, alerta.visible = "🗑️ Grupo removido com sucesso!", "success", True
            tabela.value = buscar_grupos_do_banco()
        except IntegrityError: 
            session.rollback()
            alerta.object, alerta.alert_type, alerta.visible = "⛔ Negado: Não é possível deletar um grupo que já possui membros matriculados ou encontros agendados.", "danger", True
        finally:
            session.close() 

    btn_salvar.on_click(salvar_grupo)
    btn_atualizar.on_click(atualizar_grupo)
    btn_cancelar.on_click(lambda e: limpar_form())
    btn_editar_tb.on_click(carregar_para_edicao)
    btn_deletar_tb.on_click(deletar_grupo)
    btn_filtrar.on_click(lambda e: setattr(tabela, "value", buscar_grupos_do_banco(input_filtro.value)))

    form_card = pn.Card(
        pn.Column(input_nome, input_desc, select_privacidade, input_limite, btn_salvar, btn_atualizar, btn_cancelar), 
        title="📝 Criar Novo Grupo", 
        sizing_mode="stretch_width"
    )
    grid_busca = pn.Column(pn.Row(input_filtro, btn_filtrar, align="end"), tabela, pn.Row(btn_editar_tb, btn_deletar_tb),sizing_mode="stretch_width")
    
    return pn.Column(pn.pane.Markdown("# 🏫 Gestão de Grupos de Estudo"), alerta, pn.Row(pn.Column(form_card, width=350), grid_busca, sizing_mode="stretch_width"), sizing_mode="stretch_width")
# =====================================================================
# OUTRAS TELAS (Placeholders)
# =====================================================================
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