from flask import Blueprint, render_template, request
from app.models.recipe import Recipe

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/')
def search():
    """搜尋食譜。

    接受 URL 查詢參數：
        q         (str): 關鍵字，對食譜名稱與描述進行模糊比對。
        category  (str): 分類篩選。
        difficulty(str): 難度篩選（簡單 / 中等 / 困難）。
    """
    keyword = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    filters = {}
    if category:
        filters['category'] = category
    if difficulty:
        filters['difficulty'] = difficulty

    # 有關鍵字或篩選條件才執行搜尋，否則回傳空清單
    if keyword or filters:
        recipes = Recipe.search(keyword=keyword or None, filters=filters or None)
    else:
        recipes = []

    return render_template(
        'recipe/list.html',
        recipes=recipes,
        keyword=keyword,
        selected_category=category,
        selected_difficulty=difficulty,
        is_search=True,          # 供模板判斷是否為搜尋結果頁
    )
