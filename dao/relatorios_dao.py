import pandas as pd
from sqlalchemy import text
from database.connection import get_sqlalchemy_session


def obter_df_engajamento_grupos():
    session = get_sqlalchemy_session()

    query = text("""
        SELECT
            g.nome AS "Nome do Grupo",
            COUNT(DISTINCT e.id_encontro) AS "Total de Encontros",
            COUNT(DISTINCT m.id_mensagem) AS "Total de Mensagens"
        FROM grupo g
        LEFT JOIN encontro e ON g.id_grupo = e.id_grupo
        LEFT JOIN mensagem m ON g.id_grupo = e.id_grupo
        GROUP BY g.nome
        ORDER BY "Total de Encontros" DESC, "Total de Mensagens" DESC;
    """)

    try:
        df = pd.read_sql_query(query, session.bind)
        return df
    finally:
        session.close()

def obter_df_status_encontros():
    session = get_sqlalchemy_session()

    query = text("""
        SELECT 
            status AS "Status",
            COUNT(id_encontro) AS "Qtd. de Encontros",
            COALESCE(SUM(limite_participantes), 0) AS "Vagas Ofertadas"
        FROM encontro
        GROUP BY status
        ORDER BY "Qtd. de Encontros" DESC;
    """)

    try:
        df = pd.read_sql_query(query, session.bind)
        df['Vagas Ofertadas'] = df['Vagas Ofertadas'].astype(int)
        return df
    finally:
        session.close()