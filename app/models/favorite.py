from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db


class Favorite(db.Model):
    """收藏資料表 Model。

    作為 User 與 Recipe 之間的多對多中介表，
    記錄哪位使用者收藏了哪道食譜，並含收藏時間。
    同一使用者對同一食譜只能有一筆記錄（UNIQUE 約束）。
    """
    __tablename__ = 'favorite'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='uq_user_recipe'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    recipe_id = db.Column(
        db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Favorite user={self.user_id} recipe={self.recipe_id}>'

    def to_dict(self):
        """將收藏記錄序列化為字典。"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipe_id': self.recipe_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create(cls, user_id, recipe_id):
        """新增一筆收藏記錄。

        Args:
            user_id (int): 收藏的使用者 ID。
            recipe_id (int): 被收藏的食譜 ID。

        Returns:
            Favorite: 新建立的 Favorite 物件。

        Raises:
            IntegrityError: 已收藏（違反 UNIQUE 約束）時拋出。
            SQLAlchemyError: 其他資料庫操作失敗時拋出。
        """
        try:
            new_favorite = cls(user_id=user_id, recipe_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite
        except IntegrityError:
            db.session.rollback()
            # 已存在則直接回傳現有記錄
            return cls.query_favorite(user_id, recipe_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_user(cls, user_id):
        """取得指定使用者的所有收藏（依收藏時間遞減排序）。

        Args:
            user_id (int): 使用者 ID。

        Returns:
            list[Favorite]: 收藏清單。
        """
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def query_favorite(cls, user_id, recipe_id):
        """查詢指定使用者是否收藏了指定食譜。

        Args:
            user_id (int): 使用者 ID。
            recipe_id (int): 食譜 ID。

        Returns:
            Favorite | None: 若已收藏則回傳記錄，否則回傳 None。
        """
        return cls.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

    @classmethod
    def is_favorited(cls, user_id, recipe_id):
        """快速確認是否已收藏（回傳布林值）。

        Args:
            user_id (int): 使用者 ID。
            recipe_id (int): 食譜 ID。

        Returns:
            bool: 已收藏回傳 True，否則 False。
        """
        return cls.query.filter_by(
            user_id=user_id, recipe_id=recipe_id
        ).first() is not None

    def delete(self):
        """刪除此收藏記錄。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete_favorite(cls, user_id, recipe_id):
        """刪除指定使用者對指定食譜的收藏記錄。

        Args:
            user_id (int): 使用者 ID。
            recipe_id (int): 食譜 ID。

        Returns:
            bool: 成功刪除回傳 True，記錄不存在回傳 False。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            fav = cls.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
            if fav:
                db.session.delete(fav)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def delete_by_recipe(cls, recipe_id):
        """刪除指定食譜的所有收藏記錄（通常由 cascade 處理，備用）。

        Args:
            recipe_id (int): 食譜 ID。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            cls.query.filter_by(recipe_id=recipe_id).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
