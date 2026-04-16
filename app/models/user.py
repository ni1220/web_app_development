from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError
from app import db


class User(UserMixin, db.Model):
    """使用者資料表 Model。

    繼承 UserMixin 以支援 Flask-Login 的登入狀態管理。
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯設定
    recipes = db.relationship('Recipe', backref='author', lazy=True)
    favorites = db.relationship(
        'Favorite', backref='user', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """將使用者資料序列化為字典（不含密碼）。"""
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(cls, username, password_hash, nickname, is_admin=False):
        """新增一筆使用者記錄。

        Args:
            username (str): 唯一的使用者帳號。
            password_hash (str): 使用 werkzeug 雜湊後的密碼。
            nickname (str): 顯示暱稱。
            is_admin (bool): 是否為管理員，預設 False。

        Returns:
            User: 新建立的 User 物件。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            new_user = cls(
                username=username,
                password_hash=password_hash,
                nickname=nickname,
                is_admin=is_admin,
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_id(cls, user_id):
        """依 ID 取得單筆使用者。

        Args:
            user_id (int): 使用者主鍵。

        Returns:
            User | None: 找到則回傳 User，否則回傳 None。
        """
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_username(cls, username):
        """依帳號取得使用者。

        Args:
            username (str): 使用者帳號。

        Returns:
            User | None: 找到則回傳 User，否則回傳 None。
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_all(cls):
        """取得所有使用者（依建立時間遞減排序）。

        Returns:
            list[User]: 所有使用者的清單。
        """
        return cls.query.order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        """更新使用者欄位。

        Args:
            **kwargs: 欄位名稱與新值的組合，例如 nickname='新暱稱'。

        Returns:
            User: 更新後的 User 物件。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def delete(self):
        """刪除此使用者記錄。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
