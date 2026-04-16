from . import db

class Step(db.Model):
    __tablename__ = 'step'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id', ondelete='CASCADE'), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    @classmethod
    def create(cls, recipe_id, step_order, description):
        new_step = cls(
            recipe_id=recipe_id,
            step_order=step_order,
            description=description
        )
        db.session.add(new_step)
        db.session.commit()
        return new_step

    @classmethod
    def get_by_id(cls, step_id):
        return cls.query.get(step_id)

    @classmethod
    def get_by_recipe(cls, recipe_id):
        return cls.query.filter_by(recipe_id=recipe_id).order_by(cls.step_order).all()

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
