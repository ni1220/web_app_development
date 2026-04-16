from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db


class Recipe(db.Model):
    """食譜資料表 Model。

    一道食譜包含基本資訊（標題、描述、難度、烹飪時間、封面圖、分類），
    並透過一對多關聯連結食材（Ingredient）與步驟（Step）。
    """
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(10))       # 簡單 / 中等 / 困難
    cook_time = db.Column(db.Integer)            # 單位：分鐘
    cover_image = db.Column(db.String(255))
    category = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 一對多關聯（刪除食譜時自動刪除子資料）
    ingredients = db.relationship(
        'Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan'
    )
    steps = db.relationship(
        'Step', backref='recipe', order_by='Step.step_order',
        lazy=True, cascade='all, delete-orphan'
    )
    favorites = db.relationship(
        'Favorite', backref='recipe', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Recipe {self.title}>'

    def to_dict(self):
        """將食譜序列化為字典（含食材與步驟）。"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'cook_time': self.cook_time,
            'cover_image': self.cover_image,
            'category': self.category,
            'author_id': self.author_id,
            'author_nickname': self.author.nickname if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ingredients': [i.to_dict() for i in self.ingredients],
            'steps': [s.to_dict() for s in self.steps],
        }

    @property
    def favorites_count(self):
        """取得此食譜的收藏總數。"""
        return len(self.favorites)

    @classmethod
    def create(cls, title, author_id, description=None, difficulty=None,
               cook_time=None, cover_image=None, category=None):
        """新增一筆食譜記錄。

        Args:
            title (str): 食譜名稱（必填）。
            author_id (int): 建立者的使用者 ID（必填）。
            description (str, optional): 食譜描述。
            difficulty (str, optional): 難度，例如「簡單」「中等」「困難」。
            cook_time (int, optional): 烹飪時間（分鐘）。
            cover_image (str, optional): 封面圖片檔案路徑。
            category (str, optional): 分類標籤，例如「中式」「甜點」。

        Returns:
            Recipe: 新建立的 Recipe 物件。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            new_recipe = cls(
                title=title,
                description=description,
                difficulty=difficulty,
                cook_time=cook_time,
                cover_image=cover_image,
                category=category,
                author_id=author_id,
            )
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_id(cls, recipe_id):
        """依 ID 取得單筆食譜。

        Args:
            recipe_id (int): 食譜主鍵。

        Returns:
            Recipe | None: 找到則回傳 Recipe，否則回傳 None。
        """
        return db.session.get(cls, recipe_id)

    @classmethod
    def get_all(cls):
        """取得所有食譜（依建立時間遞減排序）。

        Returns:
            list[Recipe]: 所有食譜的清單。
        """
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_author(cls, author_id):
        """取得指定使用者建立的所有食譜。

        Args:
            author_id (int): 使用者 ID。

        Returns:
            list[Recipe]: 該使用者的食譜清單。
        """
        return cls.query.filter_by(author_id=author_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def search(cls, keyword=None, filters=None):
        """依關鍵字與篩選條件搜尋食譜。

        Args:
            keyword (str, optional): 搜尋關鍵字，對標題與描述進行模糊比對。
            filters (dict, optional): 篩選條件字典，支援鍵：
                - 'category' (str): 分類標籤
                - 'difficulty' (str): 難度

        Returns:
            list[Recipe]: 符合條件的食譜清單。
        """
        query = cls.query
        if keyword:
            search_str = f'%{keyword}%'
            query = query.filter(
                (cls.title.like(search_str)) | (cls.description.like(search_str))
            )
        if filters:
            if filters.get('category'):
                query = query.filter(cls.category == filters['category'])
            if filters.get('difficulty'):
                query = query.filter(cls.difficulty == filters['difficulty'])
        return query.order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        """更新食譜欄位。

        Args:
            **kwargs: 欄位名稱與新值的組合。

        Returns:
            Recipe: 更新後的 Recipe 物件。

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
        """刪除此食譜（cascade 自動刪除食材、步驟與收藏記錄）。

        Raises:
            SQLAlchemyError: 資料庫操作失敗時拋出。
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
