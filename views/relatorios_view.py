import panel as pn
import matplotlib.pyplot as plt
from dao.relatorios_dao import obter_df_engajamento_grupos, obter_df_status_encontros

def criar_grafico_engajamento():
    # Relatório 1 (Membro A): Gráfico de Barras Agrupadas
    df = obter_df_engajamento_grupos()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    if not df.empty:
        # Coloca o nome do grupo no eixo X e plota as duas colunas numéricas
        df.set_index("Nome do Grupo").plot(
            kind="bar", ax=ax, color=["#3498db", "#2ecc71"], edgecolor="black"
        )
        ax.set_title("Engajamento: Encontros vs Mensagens por Grupo", fontsize=14, pad=15)
        ax.set_ylabel("Quantidade", fontsize=12)
        ax.set_xlabel("Grupos", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
    else:
        ax.text(0.5, 0.5, "Sem dados suficientes para gerar o gráfico", ha='center', va='center', fontsize=12)
        ax.axis('off')
        
    plt.close(fig) # Previne vazamento de memória do Matplotlib
    return pn.pane.Matplotlib(fig, sizing_mode="stretch_width")

def criar_grafico_status():
    # Relatório 2 (Membro B): Gráfico de Pizza (Ciclo de Vida)
    df = obter_df_status_encontros()
    
    fig, ax = plt.subplots(figsize=(6, 5))
    if not df.empty:
        # Define cores temáticas para os status
        cores_map = {"AGENDADO": "#f1c40f", "EM_ANDAMENTO": "#3498db", "FINALIZADO": "#2ecc71", "CANCELADO": "#e74c3c"}
        cores = [cores_map.get(status, "#95a5a6") for status in df["Status"]]
        
        ax.pie(
            df["Qtd. de Encontros"], labels=df["Status"], autopct='%1.1f%%', 
            startangle=140, colors=cores, wedgeprops={'edgecolor': 'black'}
        )
        ax.set_title("Distribuição do Status dos Encontros", fontsize=14, pad=15)
    else:
        ax.text(0.5, 0.5, "Sem dados suficientes para gerar o gráfico", ha='center', va='center', fontsize=12)
        ax.axis('off')
        
    plt.close(fig)
    return pn.pane.Matplotlib(fig, sizing_mode="stretch_width")

def tela_relatorios():
    # Botão para validar o DoD (Atualizar em tempo real)
    btn_atualizar = pn.widgets.Button(name="🔄 Atualizar Gráficos", button_type="primary", width=250)
    
    # Recipientes vazios que receberão os gráficos gerados
    painel_graf_engajamento = pn.Column(criar_grafico_engajamento(), sizing_mode="stretch_width")
    painel_graf_status = pn.Column(criar_grafico_status(), sizing_mode="stretch_width")

    # Ação de clique: limpa o container atual e insere um novo gráfico re-executando as queries
    def ao_clicar_atualizar(e):
        btn_atualizar.loading = True
        
        painel_graf_engajamento.clear()
        painel_graf_engajamento.append(criar_grafico_engajamento())
        
        painel_graf_status.clear()
        painel_graf_status.append(criar_grafico_status())
        
        btn_atualizar.loading = False

    btn_atualizar.on_click(ao_clicar_atualizar)

    # Montagem do Layout
    return pn.Column(
        pn.pane.Markdown("# 📊 Dashboard Analítico"),
        btn_atualizar,
        pn.layout.Divider(),
        pn.Row(
            pn.Card(painel_graf_engajamento, title="Engajamento Geral", sizing_mode="stretch_width"),
            pn.Card(painel_graf_status, title="Ciclo de Vida dos Encontros", sizing_mode="stretch_width"),
            sizing_mode="stretch_width"
        ),
        sizing_mode="stretch_width"
    )