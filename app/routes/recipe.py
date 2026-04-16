import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.step import Step
from app.models.favorite import Favorite

bp = Blueprint('recipe', __name__, url_prefix='/recipes')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """檢查上傳的檔案副檔名是否允許。"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_cover_image(file):
    """儲存上傳的封面圖片，回傳相對路徑字串。"""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename):
        return None
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    # 回傳相對於 static 的路徑，供模板的 url_for('static', ...) 使用
    return f'uploads/{filename}'


def parse_ingredients(form):
    """從 request.form 解析多筆食材資料。

    表單欄位格式：
        ingredient_name_0, ingredient_quantity_0, ingredient_unit_0
        ingredient_name_1, ingredient_quantity_1, ingredient_unit_1 ...

    Returns:
        list[dict]: 食材資料清單，每筆含 name, quantity, unit。
    """
    ingredients = []
    index = 0
    while True:
        name = form.get(f'ingredient_name_{index}', '').strip()
        quantity = form.get(f'ingredient_quantity_{index}', '').strip()
        unit = form.get(f'ingredient_unit_{index}', '').strip()
        if not name and not quantity:
            break
        if name:
            ingredients.append({'name': name, 'quantity': quantity or '適量', 'unit': unit or None})
        index += 1
    return ingredients


def parse_steps(form):
    """從 request.form 解析多筆步驟資料。

    表單欄位格式：
        step_description_0, step_description_1 ...（step_order 依索引自動產生）

    Returns:
        list[dict]: 步驟資料清單，每筆含 step_order, description。
    """
    steps = []
    index = 0
    while True:
        description = form.get(f'step_description_{index}', '').strip()
        if not description:
            break
        steps.append({'step_order': index + 1, 'description': description})
        index += 1
    return steps


@bp.route('/')
def list_recipes():
    """食譜列表頁面。

    接受 URL 查詢參數 category, difficulty 進行篩選。
    """
    category = request.args.get('category', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    filters = {}
    if category:
        filters['category'] = category
    if difficulty:
        filters['difficulty'] = difficulty

    recipes = Recipe.search(filters=filters if filters else None)

    return render_template(
        'recipe/list.html',
        recipes=recipes,
        selected_category=category,
        selected_difficulty=difficulty,
    )


@bp.route('/<int:recipe_id>')
def detail(recipe_id):
    """食譜詳情頁面，顯示食材清單、烹飪步驟與收藏狀態。"""
    recipe = Recipe.get_by_id(recipe_id)
    if recipe is None:
        abort(404)

    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = Favorite.is_favorited(current_user.id, recipe_id)

    return render_template(
        'recipe/detail.html',
        recipe=recipe,
        is_favorited=is_favorited,
    )


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """新增食譜表單與處理。"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        difficulty = request.form.get('difficulty', '').strip()
        cook_time_str = request.form.get('cook_time', '').strip()
        category = request.form.get('category', '').strip()

        # 必填驗證
        if not title:
            flash('食譜名稱為必填欄位。', 'danger')
            return render_template('recipe/create.html')

        # 烹飪時間型別轉換
        cook_time = None
        if cook_time_str:
            try:
                cook_time = int(cook_time_str)
                if cook_time <= 0:
                    raise ValueError
            except ValueError:
                flash('烹飪時間請輸入正整數（分鐘）。', 'danger')
                return render_template('recipe/create.html')

        # 處理封面圖片上傳
        cover_image = None
        if 'cover_image' in request.files:
            cover_image = save_cover_image(request.files['cover_image'])

        # 解析食材與步驟
        ingredients_data = parse_ingredients(request.form)
        steps_data = parse_steps(request.form)

        try:
            # 儲存食譜
            recipe = Recipe.create(
                title=title,
                author_id=current_user.id,
                description=description or None,
                difficulty=difficulty or None,
                cook_time=cook_time,
                cover_image=cover_image,
                category=category or None,
            )
            # 批次儲存食材與步驟
            if ingredients_data:
                Ingredient.create_bulk(recipe.id, ingredients_data)
            if steps_data:
                Step.create_bulk(recipe.id, steps_data)

            flash('食譜新增成功！', 'success')
            return redirect(url_for('recipe.detail', recipe_id=recipe.id))

        except Exception as e:
            flash('食譜新增失敗，請稍後再試。', 'danger')
            return render_template('recipe/create.html')

    return render_template('recipe/create.html')


@bp.route('/<int:recipe_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(recipe_id):
    """編輯食譜表單與更新處理。"""
    recipe = Recipe.get_by_id(recipe_id)
    if recipe is None:
        abort(404)

    # 權限檢查：只有作者或管理員才能編輯
    if recipe.author_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        difficulty = request.form.get('difficulty', '').strip()
        cook_time_str = request.form.get('cook_time', '').strip()
        category = request.form.get('category', '').strip()

        if not title:
            flash('食譜名稱為必填欄位。', 'danger')
            return render_template('recipe/edit.html', recipe=recipe)

        cook_time = None
        if cook_time_str:
            try:
                cook_time = int(cook_time_str)
                if cook_time <= 0:
                    raise ValueError
            except ValueError:
                flash('烹飪時間請輸入正整數（分鐘）。', 'danger')
                return render_template('recipe/edit.html', recipe=recipe)

        # 處理封面圖片：若有新上傳則替換，否則保留舊的
        cover_image = recipe.cover_image
        if 'cover_image' in request.files and request.files['cover_image'].filename:
            new_image = save_cover_image(request.files['cover_image'])
            if new_image:
                cover_image = new_image

        # 解析食材與步驟
        ingredients_data = parse_ingredients(request.form)
        steps_data = parse_steps(request.form)

        try:
            recipe.update(
                title=title,
                description=description or None,
                difficulty=difficulty or None,
                cook_time=cook_time,
                cover_image=cover_image,
                category=category or None,
            )
            # 刪除舊食材與步驟後重新建立
            Ingredient.delete_by_recipe(recipe_id)
            Step.delete_by_recipe(recipe_id)
            if ingredients_data:
                Ingredient.create_bulk(recipe_id, ingredients_data)
            if steps_data:
                Step.create_bulk(recipe_id, steps_data)

            flash('食譜更新成功！', 'success')
            return redirect(url_for('recipe.detail', recipe_id=recipe_id))

        except Exception:
            flash('食譜更新失敗，請稍後再試。', 'danger')
            return render_template('recipe/edit.html', recipe=recipe)

    return render_template('recipe/edit.html', recipe=recipe)


@bp.route('/<int:recipe_id>/delete', methods=['POST'])
@login_required
def delete(recipe_id):
    """刪除食譜（Cascade 自動清除食材、步驟、收藏）。"""
    recipe = Recipe.get_by_id(recipe_id)
    if recipe is None:
        abort(404)

    if recipe.author_id != current_user.id and not current_user.is_admin:
        abort(403)

    try:
        recipe.delete()
        flash('食譜已成功刪除。', 'success')
    except Exception:
        flash('食譜刪除失敗，請稍後再試。', 'danger')

    return redirect(url_for('recipe.list_recipes'))
