from . import db

class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20))

    @classmethod
    def create(cls, recipe_id, name, quantity, unit=None):
        new_ingredient = cls(
            recipe_id=recipe_id,
            name=name,
            quantity=quantity,
            unit=unit
        )
        db.session.add(new_ingredient)
        db.session.commit()
        return new_ingredient

    @classmethod
    def get_by_id(cls, ingredient_id):
        return cls.query.get(ingredient_id)

    @classmethod
    def get_by_recipe(cls, recipe_id):
        return cls.query.filter_by(recipe_id=recipe_id).all()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def delete_by_recipe(cls, recipe_id):
        cls.query.filter_by(recipe_id=recipe_id).delete()
        db.session.commit()
