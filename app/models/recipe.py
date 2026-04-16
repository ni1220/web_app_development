from datetime import datetime
from . import db

class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(10))
    cook_time = db.Column(db.Integer)
    cover_image = db.Column(db.String(255))
    category = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯設定
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan')
    steps = db.relationship('Step', backref='recipe', order_by='Step.step_order', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='recipe', lazy=True, cascade='all, delete-orphan')

    @classmethod
    def create(cls, title, author_id, description=None, difficulty=None, cook_time=None, cover_image=None, category=None):
        new_recipe = cls(
            title=title,
            description=description,
            difficulty=difficulty,
            cook_time=cook_time,
            cover_image=cover_image,
            category=category,
            author_id=author_id
        )
        db.session.add(new_recipe)
        db.session.commit()
        return new_recipe

    @classmethod
    def get_by_id(cls, recipe_id):
        return cls.query.get(recipe_id)

    @classmethod
    def get_all(cls):
        return cls.query.order_by(cls.created_at.desc()).all()

    @classmethod
    def search(cls, keyword, filters=None):
        query = cls.query
        if keyword:
            search_str = f"%{keyword}%"
            query = query.filter((cls.title.like(search_str)) | (cls.description.like(search_str)))
        if filters:
            if 'category' in filters:
                query = query.filter_by(category=filters['category'])
            if 'difficulty' in filters:
                query = query.filter_by(difficulty=filters['difficulty'])
        return query.order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
