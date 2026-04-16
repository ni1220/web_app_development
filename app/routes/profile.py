from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """
    GET:  顯示目前登入使用者的個人資料頁。
          渲染 profile/index.html。
    POST: 接收表單欄位 nickname（必填），以及選填的 password, confirm_password。
          更新 nickname。
          若有填寫 password，驗證兩次密碼相同後更新。
          成功 → 重導向 /profile。
          失敗 → 顯示錯誤訊息（如兩次密碼不符）。
    """
    pass
