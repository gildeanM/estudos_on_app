from sqlalchemy.exc import IntegrityError
from database.connection import get_sqlalchemy_session
from models.entities import Usuario

def buscar_usuarios_no_banco(nome_filtro=""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Usuario)
        if nome_filtro:
            query = query.filter(
                Usuario.primeiro_nome.ilike(f"%{nome_filtro}%") | 
                Usuario.sobrenome.ilike(f"%{nome_filtro}%")
            )
        # Converte a lista de objetos ORM para uma lista de dicionários limpos
        return [u.to_dict() for u in query.all()]
    finally:
        session.close()

def salvar_usuario_no_banco(primeiro_nome, sobrenome, email, senha):
    session = get_sqlalchemy_session()
    try:
        novo_u = Usuario(
            primeiro_nome=primeiro_nome,
            sobrenome=sobrenome,
            email=email,
            senha=senha,
            status="Ativo"
        )
        session.add(novo_u)
        session.commit()
        return True, "✅ Usuário cadastrado com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⚠️ Erro: Este e-mail já está cadastrado ou o dado é inválido."
    finally:
        session.close()

def buscar_usuario_por_id(id_usuario):
    session = get_sqlalchemy_session()
    try:
        return session.query(Usuario).get(id_usuario)
    finally:
        session.close()

def atualizar_usuario_no_banco(id_usuario, primeiro_nome, sobrenome, email, senha):
    session = get_sqlalchemy_session()
    try:
        u = session.query(Usuario).get(id_usuario)
        if not u:
            return False, "❌ Usuário não encontrado para atualização."
        
        u.primeiro_nome = primeiro_nome
        u.sobrenome = sobrenome
        u.email = email
        if senha: 
            u.senha = senha
            
        session.commit()
        return True, "✅ Usuário atualizado com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⚠️ Erro de integridade ao atualizar os dados."
    finally:
        session.close()

def deletar_usuario_no_banco(id_usuario):
    session = get_sqlalchemy_session()
    try:
        u = session.query(Usuario).get(id_usuario)
        if not u:
            return False, "❌ Usuário não encontrado."
        
        session.delete(u)
        session.commit()
        return True, "🗑️ Usuário removido com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "⛔ Negado: Este usuário possui vínculo com grupos ou mensagens. Remova as dependências primeiro."
    finally:
        session.close()