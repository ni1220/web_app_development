from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """登入頁面與登入處理。

    GET:  若已登入，重導向首頁；否則渲染登入表單。
    POST: 驗證帳號密碼，成功則登入並重導向首頁，失敗則顯示錯誤。
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 基本驗證
        if not username or not password:
            flash('請輸入帳號與密碼。', 'danger')
            return render_template('auth/login.html')

        # 查詢使用者
        user = User.get_by_username(username)
        if user is None:
            flash('帳號或密碼錯誤。', 'danger')
            return render_template('auth/login.html')

        # 確認帳號是否被停用
        if not user.is_active:
            flash('此帳號已被停用，請聯繫管理員。', 'danger')
            return render_template('auth/login.html')

        # 驗證密碼
        if not check_password_hash(user.password_hash, password):
            flash('帳號或密碼錯誤。', 'danger')
            return render_template('auth/login.html')

        # 登入成功
        login_user(user)
        flash(f'歡迎回來，{user.nickname}！', 'success')

        # 支援登入後跳回原本要去的頁面
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """註冊頁面與帳號建立。

    GET:  若已登入，重導向首頁；否則渲染註冊表單。
    POST: 驗證表單 → 確認帳號未重複 → 雜湊密碼 → 建立帳號 → 重導向登入頁。
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # 必填驗證
        if not username or not nickname or not password or not confirm_password:
            flash('所有欄位皆為必填。', 'danger')
            return render_template('auth/register.html')

        # 密碼一致性驗證
        if password != confirm_password:
            flash('兩次輸入的密碼不一致。', 'danger')
            return render_template('auth/register.html')

        # 密碼長度驗證
        if len(password) < 6:
            flash('密碼長度至少需要 6 個字元。', 'danger')
            return render_template('auth/register.html')

        # 帳號長度驗證
        if len(username) < 3 or len(username) > 50:
            flash('帳號長度需在 3 到 50 個字元之間。', 'danger')
            return render_template('auth/register.html')

        # 確認帳號是否已存在
        if User.get_by_username(username):
            flash('此帳號已被使用，請選擇其他帳號。', 'danger')
            return render_template('auth/register.html')

        # 建立帳號
        password_hash = generate_password_hash(password)
        try:
            User.create(username=username, password_hash=password_hash, nickname=nickname)
            flash('帳號建立成功！請登入。', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            flash('帳號建立失敗，請稍後再試。', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    """登出目前使用者並重導向首頁。"""
    logout_user()
    flash('已成功登出。', 'info')
    return redirect(url_for('index'))
