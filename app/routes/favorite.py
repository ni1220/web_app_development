from flask import Blueprint, render_template, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from app.models.favorite import Favorite
from app.models.recipe import Recipe

bp = Blueprint('favorite', __name__, url_prefix='/favorites')


@bp.route('/')
@login_required
def list_favorites():
    """
    GET:  顯示目前登入使用者的所有收藏食譜。
          呼叫 Favorite.get_by_user(current_user.id)。
          渲染 favorite/list.html。
          未登入 → Flask-Login 自動重導向 /auth/login。
    """
    pass


@bp.route('/<int:recipe_id>', methods=['POST'])
@login_required
def toggle(recipe_id):
    """
    POST: 切換指定 recipe_id 的收藏狀態（toggle）。
          確認食譜存在，否則 abort(404)。
          查詢 Favorite.query_favorite(current_user.id, recipe_id)。
          若已收藏 → Favorite.delete_favorite() 取消收藏 → 回傳 {"status": "unfavorited"}。
          若未收藏 → Favorite.create()  新增收藏  → 回傳 {"status": "favorited"}。
    """
    pass
