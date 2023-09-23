from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from core.backend import database as db
from core.backend import constants as C


Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///main.db")
Session = sessionmaker(bind=engine)
session = Session()


class Note:
    def __init__(self, folder_id: int = None, id: int = None, message_id: str = None, user_id: int = None):
        self.id = id
        self.folder_id = folder_id
        self.message_id = message_id
        self.user_id = user_id

    async def connect(self):
        """
        note.id, note.title, note.content, note.folder_id
        """
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            if self.id == None and self.message_id == None:
                # создать заметку в базе
                self.__note = db.NoteTable(
                    title=C.default_note_title,
                    content=C.default_note_content,
                    folder_id=self.folder_id,
                    message_id=self.message_id,
                )
                session.add(self.__note)
                await session.commit()
                self.id = self.__note.id

            else:
                if self.id:
                    q = select(db.NoteTable).where(db.NoteTable.id == self.id)
                    result = await session.execute(q)
                    note = result.fetchone()

                elif self.message_id and self.user_id:
                    q = select(db.FolderTable.id).where(db.FolderTable.user_id == self.user_id)
                    folders_ids = await session.execute(q).fetchall()

                    q = select(db.NoteTable).filter(db.NoteTable.folder_id.in_(folders_ids))
                    result = await session.execute(q)
                    note = result.fetchone()

                if note:
                    self.__note = note[0]
                else:
                    # создать заметку в базе
                    self.__note = db.NoteTable(
                        id=self.id,
                        title=C.default_note_title,
                        content=C.default_note_content,
                        folder_id=self.folder_id,
                        message_id=self.message_id,
                    )
                    session.add(self.__note)
                    await session.commit()

            self.title = self.__note.title
            self.content = self.__note.content
            self.folder_id = self.__note.folder_id
            self.id = self.__note.id
            self.message_id = self.__note.message_id
            # return self.id, self.title, self.content, self.folder_id
            return self

    async def update_content(self, new_content: str):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            q = update(db.NoteTable).where(db.NoteTable.id == self.id).values(content=new_content)
            await session.execute(q)
            await session.commit()
            self.content = new_content
            return self

    async def update_title(self, new_title: str):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            q = update(db.NoteTable).where(db.NoteTable.id == self.id).values(title=new_title)
            await session.execute(q)
            await session.commit()
            self.title = new_title
            return self

    async def update_message_id(self, new_message_id: str):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            q = update(db.NoteTable).where(db.NoteTable.id == self.id).values(message_id=new_message_id)
            await session.execute(q)
            await session.commit()
            return self


class Storage:
    def __init__(self, user_id):
        """
        self.folders -> folders info List [id, name]
        """
        self.user_id = user_id
        self.folders = []

    async def connect(self):
        """
        Preparing table "users"
        """
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            query = select(db.UsersTable).where(db.UsersTable.id == self.user_id)
            result = await session.execute(query)
            storage = result.fetchone()

            if storage:
                self.storage = storage
            else:
                # создать юзера в базе
                self.storage = db.UsersTable(id=self.user_id)
                session.add(self.storage)
                await session.commit()

            query = select(db.FolderTable.id, db.FolderTable.name).filter(
                db.FolderTable.user_id == self.user_id
            )
            result = await session.execute(query)

            if result:
                self.folders = result.fetchall()
            else:
                self.folders = []

            return self

    # async def getFolder(self, id: int = None):
    #     """
    #     self.notes -> notes info List [id, name]
    #     """
    #     f = Folder(user_id=self.user_id, id=id)
    #     return await f.connect()


class Folder:
    def __init__(self, user_id=None, id: int = None):
        """
        set user_id -> Get an existing folder
        set id -> Create a new folder
        """
        self.id = id
        self.user_id = user_id

    async def connect(self):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            if self.id == None:
                # создать папку в базе
                self.folder = db.FolderTable(name=C.default_folder_name, user_id=self.user_id)
                session.add(self.folder)
                await session.commit()
                self.id = self.folder.id

            else:
                query = select(db.FolderTable).where(
                    db.FolderTable.id == self.id and db.FolderTable.user_id == self.user_id
                )
                result = await session.execute(query)
                folder = result.fetchone()
                if folder:
                    self.folder = folder[0]
                else:
                    # создать папку в базе
                    self.folder = db.FolderTable(name=C.default_folder_name, id=self.id, user_id=self.user_id)
                    session.add(self.folder)
                    await session.commit()

            self.name = self.folder.name

            query = select(db.NoteTable.id, db.NoteTable.title).filter(db.NoteTable.folder_id == self.id)
            result = await session.execute(query)

            if result:
                self.notes = result.fetchall()
            else:
                self.notes = []

            return self

    async def create(self, name: str = C.default_folder_name):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            self.folder = db.FolderTable(name=name, user_id=self.user_id)
            session.add(self.folder)
            await session.commit()
            self.id = self.folder.id
            self.name = name

    async def update(self, new_name: str = None):
        async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            q = (
                update(db.FolderTable)
                .where(db.FolderTable.id == self.id)
                .values(name=new_name if new_name else self.name)
            )

            await session.execute(q)
            await session.commit()

            self.name = new_name

    # async def getNote(self, id) -> Note:
    #     n = Note(id=id, folder=self.folder)
    #     return await n.connect()
