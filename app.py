from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 初始化資料庫（若尚未建立則自動建表）
    app.run(debug=True)
