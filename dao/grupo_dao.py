from sqlalchemy.exc import IntegrityError
from database.connection import get_sqlalchemy_session
from models.entities import Grupo

def buscar_grupos_no_banco(nome_filtro=""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Grupo)
        if nome_filtro:
            query = query.filter(Grupo.nome.ilike(f"%{nome_filtro}%"))
        return [g.to_dict() for g in query.all()]
    finally:
        session.close()

def salvar_grupo_no_banco(nome, descricao, privacidade, limite_membros):
    session = get_sqlalchemy_session()
    try:
        novo_g = Grupo(
            nome=nome,
            descricao=descricao,
            privacidade=privacidade,
            limite_membros=limite_membros
        )
        session.add(novo_g)
        session.commit()
        return True, "✅ Grupo criado com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⚠️ Erro: Violação de restrição ao criar o grupo."
    finally:
        session.close()

def atualizar_grupo_no_banco(id_grupo, nome, descricao, privacidade, limite_membros):
    session = get_sqlalchemy_session()
    try:
        g = session.query(Grupo).get(int(id_grupo))
        if not g:
            return False, "❌ Grupo não encontrado para atualização."
        
        g.nome = nome
        g.descricao = descricao
        g.privacidade = privacidade
        g.limite_membros = limite_membros
        
        session.commit()
        return True, "✅ Grupo atualizado com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⚠️ Erro de integridade ao atualizar o grupo."
    finally:
        session.close()

def deletar_grupo_no_banco(id_grupo):
    session = get_sqlalchemy_session()
    try:
        g = session.query(Grupo).get(int(id_grupo))
        if not g:
            return False, "❌ Grupo não encontrado."
        
        session.delete(g)
        session.commit()
        return True, "🗑️ Grupo removido com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⛔ Negado: Não é possível deletar um grupo que possui membros ativos ou encontros agendados."
    finally:
        session.close()