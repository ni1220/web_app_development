import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 初始化擴充套件（先不綁定 app）
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '請先登入才能使用此功能。'


def create_app():
    """Flask App 工廠函式 (App Factory Pattern)"""
    app = Flask(__name__, instance_relative_config=True)

    # --- 設定 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

    # 確保 instance 資料夾存在
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- 初始化擴充套件 ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- 使用者載入函式（Flask-Login 必要） ---
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- 註冊 Blueprint ---
    from app.routes.auth import bp as auth_bp
    from app.routes.recipe import bp as recipe_bp
    from app.routes.search import bp as search_bp
    from app.routes.favorite import bp as favorite_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # --- 首頁路由 ---
    from flask import render_template
    from app.models.recipe import Recipe

    @app.route('/')
    def index():
        """首頁：顯示最新食譜"""
        latest_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(8).all()
        return render_template('index.html', recipes=latest_recipes)

    # --- 錯誤頁面 ---
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    return app
