from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    sub_menus: Mapped[list["SubMenu"]] = relationship(
        "SubMenu", back_populates="menu", cascade="all, delete-orphan"
    )


class SubMenu(Base):
    __tablename__ = "sub_menus"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    menu_id: Mapped[str] = mapped_column(
        ForeignKey("menus.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="sub_menus")
    dishes: Mapped[list["Dish"]] = relationship(
        "Dish", back_populates="sub_menu", cascade="all, delete-orphan"
    )


class Dish(Base):
    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    sub_menu_id: Mapped[str] = mapped_column(
        ForeignKey("sub_menus.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[str] = mapped_column(String)

    sub_menu: Mapped["SubMenu"] = relationship("SubMenu", back_populates="dishes")
