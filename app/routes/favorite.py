from flask import Blueprint, render_template, redirect, url_for, jsonify, abort, flash
from flask_login import login_required, current_user
from app.models.favorite import Favorite
from app.models.recipe import Recipe

bp = Blueprint('favorite', __name__, url_prefix='/favorites')


@bp.route('/')
@login_required
def list_favorites():
    """個人收藏清單頁面。

    顯示目前登入使用者所有已收藏的食譜（依收藏時間遞減排序）。
    """
    favorites = Favorite.get_by_user(current_user.id)
    # 從收藏記錄中取出食譜物件，方便模板直接使用
    recipes = [fav.recipe for fav in favorites if fav.recipe is not None]
    return render_template('favorite/list.html', recipes=recipes)


@bp.route('/<int:recipe_id>', methods=['POST'])
@login_required
def toggle(recipe_id):
    """切換指定食譜的收藏狀態（收藏 ↔ 取消收藏）。

    回傳 JSON，供前端 JavaScript 動態更新按鈕狀態。

    Response JSON:
        {"status": "favorited"}   — 已收藏
        {"status": "unfavorited"} — 已取消收藏
        {"error": "..."}          — 操作失敗
    """
    recipe = Recipe.get_by_id(recipe_id)
    if recipe is None:
        abort(404)

    try:
        existing = Favorite.query_favorite(current_user.id, recipe_id)
        if existing:
            Favorite.delete_favorite(current_user.id, recipe_id)
            return jsonify({'status': 'unfavorited'})
        else:
            Favorite.create(current_user.id, recipe_id)
            return jsonify({'status': 'favorited'})
    except Exception as e:
        return jsonify({'error': '操作失敗，請稍後再試。'}), 500
