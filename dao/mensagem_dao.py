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

def buscar_mensagem_por_id(id_mensagem):
    session = get_sqlalchemy_session()
    try:
        return session.query(Mensagem).get(int(id_mensagem))
    finally:
        session.close()

def atualizar_mensagem_no_banco(id_mensagem, conteudo, tipo, id_usuario, id_grupo):
    from datetime import datetime
    session = get_sqlalchemy_session()
    try:
        m = session.query(Mensagem).get(id_mensagem)
        if not m:
            return False, "❌ Mensagem não encontrada."
        
        m.conteudo = conteudo
        m.tipo_mensagem = tipo
        m.id_usuario = id_usuario
        m.id_grupo = id_grupo
        m.editada = True
        m.data_edicao = datetime.utcnow()

        session.commit()
        return True, "✅ Mensagem atualizado com sucesso!"

    except IntegrityError as err:
        session.rollback()
        return False, f"⚠️ Erro ao atualizar: {err}"
    finally:
        session.close()

def deletar_mensagem_no_banco(id_mensagem):
    session = get_sqlalchemy_session()
    try:
        m = session.query(Mensagem).get(int(id_mensagem))
        if not m:
            return False, "❌ Mensagem não encontrado."
        
        session.delete(m)
        session.commit()
        return True, "🗑️ Mensagem removida com sucesso!"

    except IntegrityError:
        session.rollback()        
        return False, "⛔ Negado: Esta mensagem possui dependências (como respostas)."
    finally:
        session.close()    