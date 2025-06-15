# -*- coding: utf-8 -*-
"""
Flask 線上訂餐系統主程式
- 前台點餐、購物車、桌號/外帶選擇
- 員工後台訂單管理、結帳、訂單自動移除
- 帳單分群、分類下載（Excel）
- 訂單與帳單資料庫模型
- requirements.txt 請勿刪除 pandas、openpyxl
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
import json

# Flask 應用初始化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = 'your_secret_key_123456'  # 請改成你自己的安全字串
# SQLAlchemy 資料庫初始化
db = SQLAlchemy(app)

# 資料庫模型：菜單品項
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=True)  # 新增分類欄位

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price, "category": self.category}

# 新增：細項資料表
class ItemOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    option = db.Column(db.String(100), nullable=False)

# 資料庫模型：員工
class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 資料庫模型：訂單
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(10), nullable=False)
    items = db.Column(db.Text, nullable=False)  # 儲存 JSON 字串

# 資料庫模型：帳單
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(10), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    staff_code = db.Column(db.String(100), nullable=False)
    checkout_time = db.Column(db.String(32), nullable=False)

# 新增：分類資料表
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)

# 資料庫模型：老闆
class Boss(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 取得菜單品項 API（支援 POST 新增菜品）
@app.route('/api/items', methods=['GET', 'POST'])
def get_or_add_items():
    if request.method == 'GET':
        items = Item.query.all()
        # 嘗試回傳 category 欄位（若有）
        result = []
        for item in items:
            d = item.to_dict()
            if hasattr(item, 'category'):
                d['category'] = getattr(item, 'category', None)
            result.append(d)
        return jsonify(result)
    # POST 新增菜品
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    options = data.get('options', [])
    category = data.get('category', None)
    if not name or price is None:
        return jsonify({'success': False, 'msg': '缺少名稱或價格'}), 400
    # 檢查是否重複
    if Item.query.filter_by(name=name).first():
        return jsonify({'success': False, 'msg': '菜品已存在'}), 400
    # 嘗試支援 category 欄位
    try:
        item = Item(name=name, price=price)
        if hasattr(item, 'category'):
            setattr(item, 'category', category)
        db.session.add(item)
        db.session.commit()
        # 新增：細項寫入 ItemOption
        for opt in options:
            db.session.add(ItemOption(item_id=item.id, option=opt))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': str(e)})
    return jsonify({'success': True})

# 新增：取得所有餐點細項 API
@app.route('/api/item_options')
def get_item_options():
    items = Item.query.all()
    options = ItemOption.query.all()
    item_map = {item.id: item.name for item in items}
    result = {}
    for opt in options:
        name = item_map.get(opt.item_id)
        if not name:
            continue
        result.setdefault(name, []).append(opt.option)
    return jsonify(result)

# 新增：取得/新增分類 API
@app.route('/api/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        cats = Category.query.order_by(Category.id.asc()).all()
        return jsonify([c.name for c in cats])
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'msg': '分類名稱不得為空'}), 400
    if Category.query.filter_by(name=name).first():
        return jsonify({'success': False, 'msg': '分類已存在'}), 400
    db.session.add(Category(name=name))
    db.session.commit()
    return jsonify({'success': True})

# 購物車頁面
@app.route('/shop-cart')
def shop_cart():
    return render_template('shop-cart.html')

# 員工登入頁面
@app.route('/staff')
def staff():
    return render_template('staff.html')

# 員工登入驗證
@app.route('/staff-login', methods=['POST'])
def staff_login():
    username = request.form.get('username')
    password = request.form.get('password')
    # 先檢查是否為老闆帳號
    boss = Boss.query.filter_by(username=username).first()
    if boss:
        if boss.password == password:
            session['boss_code'] = username
            staffs = Staff.query.all()
            return render_template('Boss.html', staffs=staffs)
        else:
            flash('密碼錯誤')
            return redirect(url_for('staff'))
    # 不是老闆才查員工
    staff = Staff.query.filter_by(username=username, password=password).first()
    if staff:
        session['staff_code'] = staff.username
        return redirect(url_for('personnel'))
    else:
        flash('帳號或密碼錯誤')
        return redirect(url_for('staff'))

# 前台送出訂單 API
@app.route('/api/order', methods=['POST'])
def api_order():
    data = request.get_json()
    table_number = data.get('tableNumber')
    items = data.get('items')
    if not table_number or not items:
        return jsonify({'success': False, 'msg': '缺少桌號或餐點'}), 400
    order = Order(table_number=table_number, items=json.dumps(items, ensure_ascii=False))
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True})

# 員工後台訂單管理頁面
@app.route('/personnel')
def personnel():
    orders = Order.query.order_by(Order.id.asc()).all()
    order_list = []
    for o in orders:
        try:
            items = json.loads(o.items)
        except Exception as e:
            print('訂單解析錯誤:', o.items, e)
            items = []
        # 檢查該訂單所有品項是否都已存在於 Bill（同桌號、同品項、同價格）
        all_billed = True
        for item in items:
            bill = Bill.query.filter_by(
                table_number=o.table_number,
                item_name=item.get('name'),
                item_price=float(item.get('price', 0))
            ).first()
            if not bill:
                all_billed = False
                break
        if all_billed:
            try:
                db.session.delete(o)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print('訂單刪除失敗:', o.id, e)
            continue
        order_list.append({
            'id': o.id,
            'table_number': o.table_number if o.table_number else '外帶',
            'items': items
        })
    staff_code = session.get('staff_code', 'A001')
    return render_template('personnel.html', orders=order_list, staff_code=staff_code)

# 老闆註冊員工頁面
@app.route('/Boss-register')
def boss_register_page():
    return render_template('Boss-register.html')

# 老闆註冊員工 API
@app.route('/boss-register', methods=['POST'])
def boss_register():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        flash('請輸入帳號與密碼')
        return redirect(url_for('boss_register_page'))
    # 檢查是否重複
    if Staff.query.filter_by(username=username).first():
        flash('帳號已存在')
        return redirect(url_for('boss_register_page'))
    staff = Staff(username=username, password=password)
    db.session.add(staff)
    db.session.commit()
    flash('註冊成功！')
    # 註冊完直接導回 Boss.html 並顯示員工名單
    staffs = Staff.query.all()
    return render_template('Boss.html', staffs=staffs)

# 註冊成功後回老闆頁面
@app.route('/staff-login-success')
def staff_login_success():
    staffs = Staff.query.all()
    return render_template('Boss.html', staffs=staffs)

# 老闆刪除員工 API
@app.route('/api/staff/<username>', methods=['DELETE'])
def delete_staff(username):
    staff = Staff.query.filter_by(username=username).first()
    if not staff:
        return jsonify({'success': False, 'msg': '找不到員工'})
    if username == 'Tsung':
        return jsonify({'success': False, 'msg': '老闆帳號不能被註銷'})
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'success': True})

# 員工結帳 API，將訂單明細寫入帳單
@app.route('/api/bill', methods=['POST'])
def add_bill():
    data = request.get_json()
    table_number = data.get('table_number')
    items = data.get('items')
    staff_code = data.get('staff_code')
    checkout_time = data.get('checkout_time')
    if not table_number or not items or not staff_code or not checkout_time:
        return jsonify({'success': False, 'msg': '資料不完整'}), 400
    for item in items:
        bill = Bill(
            table_number=table_number,
            item_name=item.get('name'),
            item_price=float(item.get('price', 0)),
            staff_code=staff_code,
            checkout_time=checkout_time
        )
        db.session.add(bill)
    db.session.commit()
    # 新增：刪除已結帳的訂單
    order = Order.query.filter_by(table_number=table_number, items=json.dumps(items, ensure_ascii=False)).first()
    if order:
        db.session.delete(order)
        db.session.commit()
    return jsonify({'success': True})

# 帳單紀錄頁面
@app.route('/bills')
def bills():
    bills = Bill.query.order_by(Bill.id.asc()).all()
    return render_template('bills.html', bills=bills)

# 帳單 Excel 下載 API
@app.route('/bills/download')
def download_bills():
    import pandas as pd
    from io import BytesIO
    from flask import send_file, request
    month = request.args.get('month')
    query = Bill.query.order_by(Bill.id.asc())
    if month:
        query = query.filter(Bill.checkout_time.startswith(month))
    bills = query.all()
    # 產生分群編號
    group_map = {}
    group_counter = 0
    rows = []
    for b in bills:
        group_key = f"{b.table_number.replace('結帳', '').strip()}-{b.checkout_time}"
        if group_key not in group_map:
            group_counter += 1
            group_map[group_key] = f"A{group_counter:03d}"
        rows.append([
            group_map[group_key],
            b.table_number.replace('結帳', '').strip() if b.table_number.replace('結帳', '').strip() else '外帶',
            b.item_name,
            b.item_price,
            b.staff_code,
            b.checkout_time
        ])
    df = pd.DataFrame(rows, columns=['編號', '桌號', '品項', '價格', '店員代碼', '結帳時間'])
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    if month:
        filename = f'{month.replace("-", "年")}月帳單.xlsx'
    else:
        filename = '全部帳單.xlsx'
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# 老闆後台頁面
@app.route('/Boss')
def boss_page():
    staffs = Staff.query.all()
    return render_template('Boss.html', staffs=staffs)

# 刪除餐品 API
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'success': False, 'msg': '找不到餐品'})
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

# 新增：刪除分類及其商品 API
@app.route('/api/categories/<cat_name>', methods=['DELETE'])
def delete_category(cat_name):
    # 刪除分類下所有商品（不論該分類是否在 Category 表，並處理全形/半形/空白）
    def norm(s):
        return (s or '').replace(' ', '').replace('\u3000', '').replace('類','').strip()
    # 找出所有分類名稱相等的商品（比對時去掉「類」字）
    items = Item.query.all()
    for item in items:
        if norm(item.category) == norm(cat_name):
            ItemOption.query.filter_by(item_id=item.id).delete()
            db.session.delete(item)
    # 刪除分類（如果有，並比對全形半形）
    cats = Category.query.all()
    for cat in cats:
        if norm(cat.name) == norm(cat_name):
            db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})

# 刪除訂單 API
@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'msg': '訂單不存在'}), 404
    try:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': str(e)}), 500

# 老闆更改密碼 API（獨立 Boss 表）
@app.route('/boss/change-password', methods=['POST'])
def boss_change_password():
    if 'boss_code' not in session:
        return jsonify({'success': False, 'message': '未授權，請重新登入'}), 401
    data = request.get_json()
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 4:
        return jsonify({'success': False, 'message': '新密碼長度需至少4碼'}), 400
    boss = Boss.query.filter_by(username=session['boss_code']).first()
    if not boss:
        return jsonify({'success': False, 'message': '找不到老闆帳號'}), 404
    boss.password = new_password
    db.session.commit()
    return jsonify({'success': True})

# 主程式入口
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 預設建立老闆帳號 Tsung/123456
        if not Boss.query.filter_by(username='Tsung').first():
            db.session.add(Boss(username='Tsung', password='123456'))
            db.session.commit()
        if Item.query.count() == 0:
            items = [
                Item(name='牛肉麵', price=120),
                Item(name='雞排飯', price=100),
                Item(name='陽春麵', price=80),
                Item(name='滷肉飯', price=60),
                Item(name='排骨便當', price=110),
                Item(name='燒臘飯', price=130),
                Item(name='咖哩飯', price=90),
                Item(name='水餃(10顆)', price=70),
                Item(name='鍋貼(10顆)', price=75),
                Item(name='雞腿飯', price=125),
                Item(name='紅燒牛腩麵', price=140),
                Item(name='三杯雞飯', price=120),
                Item(name='麻婆豆腐飯', price=95),
                Item(name='蔥爆豬肉飯', price=110),
                Item(name='炸醬麵', price=85),
                Item(name='酸辣湯麵', price=90),
                Item(name='青菜蛋花湯', price=40),
                Item(name='紫菜蛋花湯', price=35),
                Item(name='玉米濃湯', price=45),
                Item(name='酸辣湯', price=50)
            ]
            db.session.add_all(items)
            db.session.commit()
    app.run(debug=True)
