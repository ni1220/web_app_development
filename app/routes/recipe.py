from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.step import Step
from app.models.favorite import Favorite

bp = Blueprint('recipe', __name__, url_prefix='/recipes')


@bp.route('/')
def list_recipes():
    """
    GET:  顯示食譜列表。
          接受 URL 參數 category, difficulty 進行篩選。
          呼叫 Recipe.get_all() 或帶篩選條件查詢。
          渲染 recipe/list.html。
    """
    pass


@bp.route('/<int:recipe_id>')
def detail(recipe_id):
    """
    GET:  顯示指定 recipe_id 的食譜詳情。
          呼叫 Recipe.get_by_id(recipe_id)，不存在則 abort(404)。
          取得 recipe.ingredients 與 recipe.steps。
          若已登入，查詢 Favorite.query_favorite() 確認收藏狀態。
          渲染 recipe/detail.html。
    """
    pass


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """
    GET:  顯示新增食譜表單。
          渲染 recipe/create.html。
    POST: 接收表單欄位 title, description, difficulty, cook_time, category,
          cover_image（檔案），以及多筆食材與步驟資料。
          驗證必填欄位 title。
          若有圖片，儲存至 static/uploads/。
          呼叫 Recipe.create()，再逐一建立 Ingredient 與 Step。
          成功 → 重導向 /recipes/<新食譜 id>。
          失敗 → 顯示錯誤並重新渲染表單。
    """
    pass


@bp.route('/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(recipe_id):
    """
    GET:  顯示編輯食譜表單，預填現有資料。
          驗證目前使用者為作者或管理員，否則 abort(403)。
          渲染 recipe/edit.html。
    POST: 接收更新後的表單欄位。
          更新 recipe.update()。
          刪除舊的食材與步驟後重新建立。
          成功 → 重導向 /recipes/<recipe_id>。
    """
    pass


@bp.route('/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete(recipe_id):
    """
    POST: 刪除指定 recipe_id 的食譜。
          驗證使用者為作者或管理員，否則 abort(403)。
          呼叫 recipe.delete()（cascade 刪除子資料）。
          成功 → 重導向 /recipes。
    """
    pass
