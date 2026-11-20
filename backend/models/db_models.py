from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Utilisateur(Base):
    """
    Table UTILISATEUR : representation des joueurs et administrateurs.
    Conforme au MCD/MLD d'Abdellah (AGEA).
    """
    __tablename__ = "utilisateur"

    id_utilisateur: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pseudo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="joueur")
    date_inscription: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relations
    instances: Mapped[List["Instance"]] = relationship(
        "Instance", back_populates="utilisateur", cascade="all, delete-orphan"
    )
    soumissions: Mapped[List["Soumission"]] = relationship(
        "Soumission", back_populates="utilisateur", cascade="all, delete-orphan"
    )
    obtentions_badges: Mapped[List["ObtentionBadge"]] = relationship(
        "ObtentionBadge", back_populates="utilisateur", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Utilisateur id={self.id_utilisateur} pseudo='{self.pseudo}' role='{self.role}'>"


class Challenge(Base):
    """
    Table CHALLENGE : catalogue des epreuves CTF.
    """
    __tablename__ = "challenge"

    id_challenge: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titre: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    difficulte: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("difficulte >= 1 AND difficulte <= 5", name="check_difficulte_range"),
        nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    flag_attendu: Mapped[str] = mapped_column(String(255), nullable=False)
    image_docker: Mapped[str] = mapped_column(String(150), nullable=False)

    # Relations
    instances: Mapped[List["Instance"]] = relationship(
        "Instance", back_populates="challenge", cascade="all, delete-orphan"
    )
    soumissions: Mapped[List["Soumission"]] = relationship(
        "Soumission", back_populates="challenge", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Challenge id={self.id_challenge} titre='{self.titre}' points={self.points}>"


class Instance(Base):
    """
    Table INSTANCE : suivi du cycle de vie des conteneurs isoles lances a la volee.
    """
    __tablename__ = "instance"

    id_instance: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur: Mapped[int] = mapped_column(
        Integer, ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"), nullable=False, index=True
    )
    id_challenge: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenge.id_challenge", ondelete="CASCADE"), nullable=False, index=True
    )
    url_cible: Mapped[str] = mapped_column(String(255), nullable=False)
    date_lancement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="starting"  # starting, running, stopped, error
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", back_populates="instances")
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="instances")

    def __repr__(self) -> str:
        return f"<Instance id={self.id_instance} user={self.id_utilisateur} chal={self.id_challenge} statut='{self.statut}'>"


class Soumission(Base):
    """
    Table SOUMISSION : trace des flags soumis par les joueurs pour les validations et le score.
    """
    __tablename__ = "soumission"

    id_soumission: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_utilisateur: Mapped[int] = mapped_column(
        Integer, ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"), nullable=False, index=True
    )
    id_challenge: Mapped[int] = mapped_column(
        Integer, ForeignKey("challenge.id_challenge", ondelete="CASCADE"), nullable=False, index=True
    )
    flag_soumis: Mapped[str] = mapped_column(String(255), nullable=False)
    est_valide: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_soumission: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", back_populates="soumissions")
    challenge: Mapped["Challenge"] = relationship("Challenge", back_populates="soumissions")

    def __repr__(self) -> str:
        return f"<Soumission id={self.id_soumission} user={self.id_utilisateur} valid={self.est_valide}>"


class Badge(Base):
    """
    Table BADGE : recompenses obtenues lors de l'atteinte d'un seuil de points.
    """
    __tablename__ = "badge"

    id_badge: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_badge: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    seuil_points: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relations
    obtentions: Mapped[List["ObtentionBadge"]] = relationship(
        "ObtentionBadge", back_populates="badge", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Badge id={self.id_badge} nom='{self.nom_badge}' seuil={self.seuil_points}>"


class ObtentionBadge(Base):
    """
    Table OBTENTION_BADGE : table d'association reliant un utilisateur au badge qu'il a debloque.
    Cle primaire composite (id_utilisateur, id_badge).
    """
    __tablename__ = "obtention_badge"

    id_utilisateur: Mapped[int] = mapped_column(
        Integer, ForeignKey("utilisateur.id_utilisateur", ondelete="CASCADE"), primary_key=True
    )
    id_badge: Mapped[int] = mapped_column(
        Integer, ForeignKey("badge.id_badge", ondelete="CASCADE"), primary_key=True
    )
    date_obtention: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relations
    utilisateur: Mapped["Utilisateur"] = relationship("Utilisateur", back_populates="obtentions_badges")
    badge: Mapped["Badge"] = relationship("Badge", back_populates="obtentions")

    def __repr__(self) -> str:
        return f"<ObtentionBadge user={self.id_utilisateur} badge={self.id_badge}>"
