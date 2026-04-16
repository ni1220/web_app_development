from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from app.models.recipe import Recipe
from app.models.user import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """自訂裝飾器：確認目前使用者為管理員，否則回傳 403。"""
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
    """管理員儀表板：顯示系統統計數據與最新食譜。"""
    total_recipes = len(Recipe.get_all())
    total_users = len(User.get_all())
    latest_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_recipes=total_recipes,
        total_users=total_users,
        latest_recipes=latest_recipes,
    )


@bp.route('/recipes')
@login_required
@admin_required
def manage_recipes():
    """管理員食譜列表：顯示所有食譜（含作者資訊）。"""
    recipes = Recipe.get_all()
    return render_template('admin/recipes.html', recipes=recipes)


@bp.route('/recipes/<int:recipe_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_recipe(recipe_id):
    """管理員強制刪除任意食譜。"""
    recipe = Recipe.get_by_id(recipe_id)
    if recipe is None:
        abort(404)

    try:
        recipe.delete()
        flash(f'食譜「{recipe.title}」已刪除。', 'success')
    except Exception:
        flash('刪除失敗，請稍後再試。', 'danger')

    return redirect(url_for('admin.manage_recipes'))


@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """管理員使用者列表：顯示所有使用者帳號。"""
    users = User.get_all()
    return render_template('admin/users.html', users=users)


@bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """切換使用者帳號的啟用 / 停用狀態。"""
    user = User.get_by_id(user_id)
    if user is None:
        abort(404)

    # 防止管理員停用自己的帳號
    if user.id == current_user.id:
        flash('無法停用自己的帳號。', 'danger')
        return redirect(url_for('admin.manage_users'))

    try:
        user.update(is_active=not user.is_active)
        status = '啟用' if user.is_active else '停用'
        flash(f'帳號「{user.nickname}」已{status}。', 'success')
    except Exception:
        flash('操作失敗，請稍後再試。', 'danger')

    return redirect(url_for('admin.manage_users'))
