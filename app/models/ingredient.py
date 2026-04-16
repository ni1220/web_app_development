from sqlalchemy.exc import SQLAlchemyError
from app import db


class Ingredient(db.Model):
    """食材資料表 Model。

    每筆記錄代表某道食譜所需的一項食材，
    透過 recipe_id 外鍵關聯至 Recipe。
    """
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)   # 支援「適量」或分數如「1/2」
    unit = db.Column(db.String(20))                        # 例如：克、匙、毫升

    def __repr__(self):
        return f'<Ingredient {self.name} ({self.quantity}{self.unit or ""})>'

    def to_dict(self):
        """將食材序列化為字典。"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit or '',
        }

    @classmethod
    def create(cls, recipe_id, name, quantity, unit=None):
        """新增一筆食材記錄。

        Args:
            recipe_id (int): 所屬食譜的 ID（必填）。
            name (str): 食材名稱（必填）。
            quantity (str): 份量，例如「100」「1/2」「適量」（必填）。
            unit (str, optional): 單位，例如「克」「匙」。

        Returns:
            Ingredient: 新建立的 Ingredient 物件。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            new_ingredient = cls(
                recipe_id=recipe_id,
                name=name,
                quantity=quantity,
                unit=unit,
            )
            db.session.add(new_ingredient)
            db.session.commit()
            return new_ingredient
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def create_bulk(cls, recipe_id, ingredients_data):
        """批次新增多筆食材（同一 session，只 commit 一次）。

        Args:
            recipe_id (int): 所屬食譜的 ID。
            ingredients_data (list[dict]): 食材資料清單，每筆包含
                'name', 'quantity', 以及可選的 'unit'。

        Returns:
            list[Ingredient]: 新建立的食材物件清單。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            items = []
            for data in ingredients_data:
                item = cls(
                    recipe_id=recipe_id,
                    name=data['name'],
                    quantity=data['quantity'],
                    unit=data.get('unit'),
                )
                db.session.add(item)
                items.append(item)
            db.session.commit()
            return items
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_id(cls, ingredient_id):
        """依 ID 取得單筆食材。

        Args:
            ingredient_id (int): 食材主鍵。

        Returns:
            Ingredient | None: 找到則回傳，否則回傳 None。
        """
        return db.session.get(cls, ingredient_id)

    @classmethod
    def get_by_recipe(cls, recipe_id):
        """取得指定食譜的所有食材。

        Args:
            recipe_id (int): 食譜 ID。

        Returns:
            list[Ingredient]: 食材清單。
        """
        return cls.query.filter_by(recipe_id=recipe_id).all()

    def update(self, **kwargs):
        """更新食材欄位。

        Args:
            **kwargs: 欄位名稱與新值的組合。

        Returns:
            Ingredient: 更新後的物件。

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
        """刪除此食材記錄。

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
        """刪除指定食譜的所有食材記錄。

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
