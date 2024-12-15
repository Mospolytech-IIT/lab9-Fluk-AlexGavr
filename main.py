"""main"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# URL базы данных (используем SQLite для простоты)
DATABASE_URL = "sqlite:///./test.db"

# Создание движка базы данных и сессии
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """Модель пользователя, представляющая таблицу Users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    posts = relationship("Post", back_populates="owner")


class Post(Base):
    """Модель поста, представляющая таблицу Posts."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="posts")

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Приложение FastAPI
app = FastAPI()

# Схемы Pydantic
class UserCreate(BaseModel):
    """Схема для создания нового пользователя."""
    username: str
    email: str
    password: str

class PostCreate(BaseModel):
    """Схема для создания нового поста."""
    title: str
    content: str
    user_id: int

@app.post("/users/")
def create_user(user: UserCreate):
    """Маршрут для создания нового пользователя."""
    db = SessionLocal()
    db_user = User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

@app.get("/users/")
def read_users():
    """Маршрут для получения всех пользователей."""
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

@app.post("/posts/")
def create_post(post: PostCreate):
    """Маршрут для создания нового поста."""
    db = SessionLocal()
    db_post = Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    db.close()
    return db_post

@app.get("/posts/")
def read_posts():
    """Маршрут для получения всех постов."""
    db = SessionLocal()
    posts = db.query(Post).all()
    db.close()
    return posts

@app.get("/posts/user/{user_id}")
def read_posts_by_user(user_id: int):
    """Маршрут для получения постов определенного пользователя."""
    db = SessionLocal()
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    db.close()
    if not posts:
        raise HTTPException(status_code=404, detail="Посты не найдены")
    return posts

@app.put("/users/{user_id}")
def update_user_email(user_id: int, email: str):
    """Маршрут для обновления email пользователя."""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.email = email
    db.commit()
    db.refresh(user)
    db.close()
    return user

@app.put("/posts/{post_id}")
def update_post_content(post_id: int, content: str):
    """Маршрут для обновления содержимого поста."""
    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        db.close()
        raise HTTPException(status_code=404, detail="Пост не найден")
    post.content = content
    db.commit()
    db.refresh(post)
    db.close()
    return post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    """Маршрут для удаления поста."""
    db = SessionLocal()
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        db.close()
        raise HTTPException(status_code=404, detail="Пост не найден")
    db.delete(post)
    db.commit()
    db.close()
    return {"detail": "Пост успешно удален"}

@app.delete("/users/{user_id}")
def delete_user_and_posts(user_id: int):
    """Маршрут для удаления пользователя и всех его постов."""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.query(Post).filter(Post.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    db.close()
    return {"detail": "Пользователь и его посты успешно удалены"}
