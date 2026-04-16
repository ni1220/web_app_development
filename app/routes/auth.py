from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET:  顯示登入表單頁。若已登入，直接重導向首頁。
    POST: 接收表單欄位 username, password。
          驗證帳密 → 呼叫 login_user() → 重導向首頁。
          失敗 → 顯示錯誤訊息並重新渲染登入頁。
    """
    pass


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET:  顯示註冊表單頁。若已登入，直接重導向首頁。
    POST: 接收表單欄位 username, password, nickname。
          驗證欄位 → 確認帳號未重複 → hash 密碼 → User.create()
          成功 → 重導向 /auth/login。
          失敗 → 顯示錯誤訊息並重新渲染註冊頁。
    """
    pass


@bp.route('/logout')
@login_required
def logout():
    """
    GET:  呼叫 logout_user() 登出目前使用者。
          重導向首頁。
    """
    pass
