from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database.connection import Base

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
            "ID": str(self.id_usuario),
            "Nome": f"{self.primeiro_nome} {self.sobrenome or ''}".strip(),
            "E-mail": self.email,
            "Status": self.status
        }

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

class Encontro(Base):
    __tablename__ = "encontro"

    id_encontro = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(128), nullable=False)
    descricao = Column(String(255))
    data_hora_inicio = Column(DateTime(timezone=True), nullable=False)
    data_hora_fim = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False)
    limite_participantes = Column(Integer)
    id_grupo = Column(Integer, ForeignKey("grupo.id_grupo", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        return {
            "ID": str(self.id_encontro)[:8] + "...",
            "Título": self.titulo,
            "Início": self.data_hora_inicio.strftime("%d/%m %H:%M") if self.data_hora_inicio else "",
            "Fim": self.data_hora_fim.strftime("%d/%m %H:%M") if self.data_hora_fim else "",
            "Status": self.status,
            "ID Grupo": self.id_grupo

        }

class Mensagem(Base):
    __tablename__ = "mensagem"

    id_mensagem = Column(BigInteger, primary_key=True, autoincrement=True)
    conteudo = Column(Text, nullable=False)
    data_envio = Column(DateTime, default=datetime.utcnow)
    tipo_mensagem = Column(String)
    editada = Column(Boolean, default=False)
    data_edicao = Column(DateTime)
    id_mensagem_respondida = Column(BigInteger, ForeignKey("mensagem.id_mensagem", ondelete="SET NULL"))
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario"))
    id_grupo = Column(Integer, ForeignKey("grupo.id_grupo"))

    def to_dict(self):
        return {
            "ID": self.id_mensagem,
            "Conteúdo": self.conteudo[:30] + "..." if len(self.conteudo) > 30 else self.conteudo,
            "Tipo": self.tipo_mensagem,
            "Envio": self.data_envio.strftime("%d/%m %H:%M") if self.data_envio else "",
            "Autor ID": str(self.id_usuario)[:8] + "..." if self.id_usuario else "N/A"
        }