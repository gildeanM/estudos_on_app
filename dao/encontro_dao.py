from sqlalchemy.exc import IntegrityError
from database.connection import get_sqlalchemy_session
from models.entities import Encontro


def buscar_encontros_no_banco(filtro = ""):
    session = get_sqlalchemy_session()
    try:
        query = session.query(Encontro)
        if filtro:
            query = query.filter(Encontro.titulo.ilike(f"%{filtro}"))
        return [e.to_dict() for e in query.all()]
    finally:
        session.close()

def salvar_encontro_no_banco(titulo, descricao, inicio, fim, status, limite, id_grupo):
    session = get_sqlalchemy_session()

    try:
        novo_e = Encontro(
            titulo = titulo, descricao = descricao, data_hora_inicio = inicio,
            data_hora_fim = fim, status = status, limite_participantes = limite, id_grupo = id_grupo
        )
        session.add(novo_e)
        session.commit()
        return True, "✅ Encontro agendado com sucesso!"

    except IntegrityError as e:
        session.rollback()
        
        if "chk_encontro_datas" in str(e):
            return False, "⚠️ A data de término deve ser posterior à data de início."
        return False, "⚠️ Erro nas restrições de integridade do banco."

    finally:
        session.close()

