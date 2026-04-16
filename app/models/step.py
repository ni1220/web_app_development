from sqlalchemy.exc import SQLAlchemyError
from app import db


class Step(db.Model):
    """烹飪步驟資料表 Model。

    每筆記錄代表某道食譜的一個步驟，
    透過 recipe_id 外鍵關聯至 Recipe，
    並以 step_order 欄位維護步驟順序。
    """
    __tablename__ = 'step'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False
    )
    step_order = db.Column(db.Integer, nullable=False)   # 步驟編號（1, 2, 3...）
    description = db.Column(db.Text, nullable=False)      # 步驟說明文字

    def __repr__(self):
        return f'<Step recipe={self.recipe_id} order={self.step_order}>'

    def to_dict(self):
        """將步驟序列化為字典。"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'step_order': self.step_order,
            'description': self.description,
        }

    @classmethod
    def create(cls, recipe_id, step_order, description):
        """新增一筆步驟記錄。

        Args:
            recipe_id (int): 所屬食譜的 ID（必填）。
            step_order (int): 步驟編號，從 1 開始（必填）。
            description (str): 步驟說明文字（必填）。

        Returns:
            Step: 新建立的 Step 物件。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            new_step = cls(
                recipe_id=recipe_id,
                step_order=step_order,
                description=description,
            )
            db.session.add(new_step)
            db.session.commit()
            return new_step
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def create_bulk(cls, recipe_id, steps_data):
        """批次新增多筆步驟（同一 session，只 commit 一次）。

        Args:
            recipe_id (int): 所屬食譜的 ID。
            steps_data (list[dict]): 步驟資料清單，每筆包含
                'step_order' 與 'description'。

        Returns:
            list[Step]: 新建立的步驟物件清單。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            items = []
            for data in steps_data:
                item = cls(
                    recipe_id=recipe_id,
                    step_order=data['step_order'],
                    description=data['description'],
                )
                db.session.add(item)
                items.append(item)
            db.session.commit()
            return items
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_id(cls, step_id):
        """依 ID 取得單筆步驟。

        Args:
            step_id (int): 步驟主鍵。

        Returns:
            Step | None: 找到則回傳，否則回傳 None。
        """
        return db.session.get(cls, step_id)

    @classmethod
    def get_by_recipe(cls, recipe_id):
        """取得指定食譜的所有步驟（依 step_order 排序）。

        Args:
            recipe_id (int): 食譜 ID。

        Returns:
            list[Step]: 步驟清單（已排序）。
        """
        return cls.query.filter_by(recipe_id=recipe_id).order_by(cls.step_order).all()

    def update(self, **kwargs):
        """更新步驟欄位。

        Args:
            **kwargs: 欄位名稱與新值的組合。

        Returns:
            Step: 更新後的物件。

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
        """刪除此步驟記錄。

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
    def delete_by_recipe(cls, recipe_id):
        """刪除指定食譜的所有步驟記錄。

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
