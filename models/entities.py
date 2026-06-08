from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.connection import Base


# ENTIDADE USUÁRIO (Membro A - Schema Fiel)
# =====================================================================
class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    primeiro_nome = Column(String(50), nullable=False)
    sobrenome = Column(String(50))
    email = Column(String(100), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    status = Column(String(20), default="Ativo") 

    def to_dict(self):
        return {
            "ID": str(self.id_usuario)[:8] + "...",
            "Nome": f"{self.primeiro_nome} {self.sobrenome or ''}".strip(),
            "E-mail": self.email,
            "Status": self.status
        }


# ENTIDADE GRUPO (Membro B - Schema Fiel)
# =====================================================================
class Grupo(Base):
    __tablename__ = "grupo"

    id_grupo = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(64), nullable=False)
    descricao = Column(Text)
    foto_grupo = Column(String(255))
    privacidade = Column(String(50), nullable=False)
    limite_membros = Column(Integer, nullable=False)
    data_criacao = Column(DateTime(timezone=True), default=datetime.utcnow)

    def to_dict(self):
        return {
            "ID": self.id_grupo,
            "Nome": self.nome,
            "Descrição": self.descricao if self.descricao else "",
            "Privacidade": self.privacidade,
            "Limite": self.limite_membros
        }