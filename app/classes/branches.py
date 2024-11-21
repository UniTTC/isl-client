from typing import List


class Branch:
    def __init__(self, branch: str, address: str, phone: List[str], email: List[str]):
        self.branch = branch
        self.address = address
        self.phone = phone
        self.email = email

    def __repr__(self):
        return f"Branch(branch='{self.branch}', address='{self.address}', phone={self.phone}, email={self.email})"


branches = [
    Branch(
        branch="Центральный аппарат",
        address="г.Астана, ул. Кунаева, 10",
        phone=["+7 (7172) 611-456"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Актаутранстелеком",
        address="13 микрорайон, 55 здание, 5 этаж, БЦ «Кораблик»",
        phone=["8 (7292) 46-23-78", "8 (7292) 46-27-70"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Актобетранстелеком",
        address="г. Актобе, ул.Мангилик ел 7б, Бизнес центр Batys Tower (для юр лиц - 5 этаж, для физ лиц - 7 этаж)",
        phone=["8 (7132) 97-42-55", "8 (7132) 97-47-11"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Алматытранстелеком",
        address="г. Алматы, ул. Карасай Батыра, 55 (504 кабинет, 5 этаж - для юр лиц; 609 кабинет, 6 этаж - для физ лиц)",
        phone=["8 (7272) 96-42-95", "8 (7272) 96-51-47"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Астанатранстелеком",
        address="г. Астана, пр.Туран д.42, этаж 3 (для юр лиц), ул.Гейдара Алиева, д.10/1 (для физ лиц)",
        phone=["8 (7172) 60-00-01"],
        email=["astana@ttc.kz", "support@ttc.kz"]
    ),
    Branch(
        branch="Атыраутранстелеком",
        address="г. Атырау, ул. Сырым Датова 42",
        phone=["8 (7122) 95-35-53", "8 (7122) 95-35-52", "8 (7122) 95-35-51", "8 (7122) 95-34-88"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Жамбылтранстелеком",
        address="г. Жамбыл, ул. Турксибская, 2 (офис для физ и юр лиц)",
        phone=["8 (7262) 96-08-33", "8 (7262) 96-11-55"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Карагандытранстелеком",
        address="100000, ул. Нуркена Абдирова-5, «Бизнес центр», 5 этаж (юр и физ); ул. Мануильского, 4 (для физ лиц)",
        phone=["8 (7212) 60-45-13", "8 (7212) 60-45-10"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Кокшетаутранстелеком",
        address="г. Кокшетау, ул. Акан Серы, 116а - БЦ Forum, 4 этаж (офис для физ и юр лиц)",
        phone=["8 (7162) 29-42-60", "8 (7162) 29-29-00"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Костанайтранстелеком",
        address="г. Костанай, ул. Толстого 135а (офис для физ и юр лиц)",
        phone=["8 (7142) 90-06-65", "8 (7142) 90-16-53"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Кызылордатранстелеком",
        address="г. Кызылорда, пр.Астана 2, (офис для физ и юр лиц)",
        phone=["8 (7242) 29-05-05"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Павлодартранстелеком",
        address="г. Павлодар, ул. Кудайбергена Сураганова, 7 (офис для физ и юр лиц)",
        phone=["8 (7182) 37-37-77", "8 (7182) 37-22-27"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Семейтранстелеком",
        address="г. Семей, улица Каюма Мухамедханова, 23 (офис для физ и юр лиц)",
        phone=["8 (7222) 38-11-60", "8 (7222) 38-00-81"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Оскементранстелеком",
        address="г. Оскемен, ул. Максима Горького, 48, кабинет 311 (офис для физ и юр лиц)",
        phone=["8 (7232) 50-03-33", "8 (7232) 50-20-99"],
        email=["support@ttc.kz"]
    ),
    Branch(
        branch="Шымкенттранстелеком",
        address="г. Шымкент, пр-т. Кабанбай Батыра, 3 (офис для физ и юр лиц)",
        phone=["8 (7252) 95-31-66", "8 (7252) 95-20-79"],
        email=["support@ttc.kz"]
    )
]
