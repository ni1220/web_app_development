from flask import Blueprint, render_template, request
from app.models.recipe import Recipe

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/')
def search():
    """
    GET:  接收 URL 查詢參數 q（關鍵字）、category、difficulty。
          呼叫 Recipe.search(keyword, filters) 進行搜尋。
          渲染 recipe/list.html，傳入搜尋結果與查詢參數。
          無結果時顯示「找不到符合的食譜」提示。
    """
    pass
