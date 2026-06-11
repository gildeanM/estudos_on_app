from database.connection import get_sqlalchemy_session
from models.entities import Mensagem

def buscar_mensagens_no_banco(filtro = ""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Mensagem)
        if filtro:
            query = query.filter(Mensagem.conteudo.ilike(f"%{filtro}"))
        return [m.to_dict() for m in query.all()]
    finally:
        session.close()

def salvar_mensagem_no_banco(conteudo, tipo, id_usuario, id_grupo):
    session = get_sqlalchemy_session()
    try:
        nova_m = Mensagem(conteudo = conteudo, tipo_mensagem = tipo, id_usuario = id_usuario, id_grupo = id_grupo)
        session.add(nova_m)
        session.commit()
        return True, "✅ Mensagem enviada!"
    except Exception as e:
        session.rollback()
        return False, f"⚠️ Erro ao enviar mensagem: {e}"
    finally:
        session.close()