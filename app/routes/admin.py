from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required
from functools import wraps
from flask_login import current_user
from app.models.recipe import Recipe
from app.models.user import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    自訂裝飾器：確認目前登入使用者為管理員。
    若非管理員，abort(403)。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    GET:  顯示管理員儀表板。
          統計食譜總數、使用者總數、最新幾筆食譜。
          渲染 admin/dashboard.html。
    """
    pass


@bp.route('/recipes')
@login_required
@admin_required
def manage_recipes():
    """
    GET:  顯示所有食譜的管理清單（含作者資訊）。
          呼叫 Recipe.get_all()。
          渲染 admin/recipes.html。
    """
    pass


@bp.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_recipe(recipe_id):
    """
    POST: 管理員強制刪除指定 recipe_id 的食譜。
          呼叫 Recipe.get_by_id(recipe_id)，不存在則 abort(404)。
          呼叫 recipe.delete()。
          重導向 /admin/recipes。
    """
    pass


@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """
    GET:  顯示所有使用者的管理清單。
          呼叫 User.get_all()。
          渲染 admin/users.html。
    """
    pass


@bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """
    POST: 切換指定 user_id 的帳號啟用狀態（is_active toggle）。
          呼叫 User.get_by_id(user_id)，不存在則 abort(404)。
          切換 user.is_active 欄位後更新。
          重導向 /admin/users。
    """
    pass
