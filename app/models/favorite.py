from datetime import datetime
from . import db

class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, user_id, recipe_id):
        new_favorite = cls(
            user_id=user_id,
            recipe_id=recipe_id
        )
        db.session.add(new_favorite)
        db.session.commit()
        return new_favorite

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def query_favorite(cls, user_id, recipe_id):
        return cls.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_favorite(cls, user_id, recipe_id):
        fav = cls.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()

    @classmethod
    def delete_by_recipe(cls, recipe_id):
        cls.query.filter_by(recipe_id=recipe_id).delete()
        db.session.commit()
