from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.recipe import Recipe

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """個人資料頁面與更新處理。

    GET:  顯示目前登入使用者的個人資料，以及他建立的食譜清單。
    POST: 更新暱稱；若有填寫新密碼，同時更新密碼（需驗證舊密碼）。
    """
    if request.method == 'POST':
        action = request.form.get('action', '')

        # --- 更新暱稱 ---
        if action == 'update_nickname':
            nickname = request.form.get('nickname', '').strip()
            if not nickname:
                flash('暱稱不可為空。', 'danger')
            elif len(nickname) > 50:
                flash('暱稱不可超過 50 個字元。', 'danger')
            else:
                try:
                    current_user.update(nickname=nickname)
                    flash('暱稱已更新。', 'success')
                except Exception:
                    flash('更新失敗，請稍後再試。', 'danger')

        # --- 更新密碼 ---
        elif action == 'update_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            if not current_password or not new_password or not confirm_password:
                flash('所有密碼欄位皆為必填。', 'danger')
            elif not check_password_hash(current_user.password_hash, current_password):
                flash('目前密碼錯誤。', 'danger')
            elif new_password != confirm_password:
                flash('兩次新密碼輸入不一致。', 'danger')
            elif len(new_password) < 6:
                flash('新密碼長度至少需要 6 個字元。', 'danger')
            else:
                try:
                    current_user.update(password_hash=generate_password_hash(new_password))
                    flash('密碼已成功更新。', 'success')
                except Exception:
                    flash('密碼更新失敗，請稍後再試。', 'danger')

        return redirect(url_for('profile.index'))

    # 取得此使用者建立的所有食譜
    my_recipes = Recipe.get_by_author(current_user.id)
    return render_template('profile/index.html', my_recipes=my_recipes)
