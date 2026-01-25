from flask import Flask, render_template, request, session, redirect, url_for, flash
import google.generativeai as genai
from menu_data import food_database
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
import random

app = Flask(__name__)
app.secret_key = 'chia_khoa_bao_mat_cua_ban'

# --- 1. CẤU HÌNH ---
BASE_DIR = r"D:\nutrition_app"
if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)

db_path = os.path.join(BASE_DIR, "users.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

# --- 2. AI CONFIG (SỬA LỖI 500 TẠI ĐÂY) ---
# Key của bạn
GOOGLE_API_KEY = "AIzaSyCy2DPwd5M1GnJN8B7e4o5yoUi22TxMq2w"
genai.configure(api_key=GOOGLE_API_KEY)

# *** ĐÃ SỬA: Dùng 'gemini-pro' để chạy ổn định, không bị lỗi 404 ***
model = genai.GenerativeModel('gemini-pro')

# --- 3. DATABASE ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    height = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --- 4. DANH SÁCH MÓN ĂN NHẸ "CỨU ĐÓI" (KHI BỊ PHẠT) ---
LIGHT_MEALS = [
    {"name": "🥗 Salad dưa leo cà chua (Sốt chanh, không đường)", "calo": 50},
    {"name": "🥒 Rau củ luộc kho quẹt (Ăn nhiều rau)", "calo": 80},
    {"name": "🍲 Canh bí đao nấu tôm khô (Chỉ uống nước và ăn cái)", "calo": 70},
    {"name": "🥬 Bắp cải luộc + 1 quả trứng luộc", "calo": 90},
    {"name": "🥣 Súp rau củ thập cẩm (Không tinh bột)", "calo": 60},
    {"name": "🥗 Nộm su hào cà rốt (Không lạc/đậu phộng)", "calo": 75}
]

# --- 5. AI FUNCTIONS ---

def ask_ai_calories(dish_name):
    """Hỏi AI số calo (Dùng Regex lọc số để tránh lỗi)"""
    try:
        print(f"🍲 Đang hỏi AI: {dish_name}")
        prompt = f"Món ăn: '{dish_name}'. Hãy ước lượng Calo cho 1 suất ăn này. Chỉ trả lời duy nhất 1 con số nguyên (Ví dụ: 450). Không viết thêm chữ."
        
        response = model.generate_content(prompt)
        text = response.text
        print(f"🤖 AI trả lời: {text}") # In ra xem AI nói gì
        
        # Lọc lấy số từ câu trả lời
        numbers = re.findall(r'\d+', text)
        
        if numbers:
            return int(numbers[0])
        else:
            return 300 # Mặc định nếu AI không đưa ra số
            
    except Exception as e:
        print(f"❌ LỖI AI: {e}")
        return 500 # Trả về 500 nếu lỗi mạng/key

def ask_ai_feedback(start_w, final_w, goal, warnings):
    try:
        diff = final_w - start_w
        res = "giảm" if diff < 0 else "tăng"
        
        # Gửi danh sách vi phạm cho AI
        vi_pham = "; ".join(warnings) if warnings else "Không có vi phạm nào."
        
        prompt = f"""
        Đóng vai HLV dinh dưỡng nghiêm khắc.
        - Mục tiêu: {goal}. Kết quả: {res} {abs(diff)}kg.
        - Lịch sử vi phạm tuần qua: {vi_pham}.
        Hãy nhận xét ngắn gọn 3 câu, nhắc nhở nếu có vi phạm.
        """
        return model.generate_content(prompt).text
    except: return "Kết quả tốt! Cố gắng duy trì nhé."

def create_plan(weight, height, age, gender, goal):
    if gender == 'male': bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else: bmr = 10 * weight + 6.25 * height - 5 * age - 161
    tdee = bmr * 1.2
    
    if goal == 'lose': base = tdee - 500
    elif goal == 'gain': base = tdee + 400
    else: base = tdee
    base = max(1000, round(base))
    target_meal = round(base / 3)

    menu = {}
    db_menu = food_database.get(goal, {})
    def get_dish(t):
        items = db_menu.get(t, [])
        return random.choice(items) if items else {"name": "Món tùy chọn", "calo": 400}

    for i in range(1, 8):
        menu[str(i)] = {
            'breakfast': get_dish('breakfast'),
            'lunch': get_dish('lunch'),
            'dinner': get_dish('dinner'),
            'targets': [target_meal, target_meal, target_meal],
            'eaten': [0, 0, 0], 'is_custom': [False, False, False]
        }
    
    return {
        'profile': {'height': height, 'age': age, 'gender': gender, 'goal': goal},
        'start_weight': weight, 'final_weight': 0, 
        'base_target': base, 'daily_target': base,
        'current_day': 1, 'current_meal': 0, 'balance': 0,
        'warnings': [], 
        'menu_plan': menu, 'calorie_history': [0]*8, 'ai_feedback': ''
    }

# --- 6. ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    if User.query.filter_by(username=username).first():
        flash('Tên đã tồn tại!', 'error'); return redirect(url_for('index'))
    new_user = User(username=username, password=generate_password_hash(request.form['password'], method='pbkdf2:sha256'))
    db.session.add(new_user); db.session.commit(); login_user(new_user)
    session.pop('app_data', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        login_user(user); session.pop('app_data', None); return redirect(url_for('index'))
    flash('Sai thông tin!', 'error'); return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout(): logout_user(); session.pop('app_data', None); return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated: return render_template('index.html', user=None)
    if request.args.get('action') == 'reset': session.pop('app_data', None); return redirect(url_for('index'))
    
    app_data = session.get('app_data')

    if request.method == 'POST':
        # 1. SETUP
        if 'setup_full' in request.form:
            try:
                w = float(request.form['weight']); h = float(request.form['height']); a = int(request.form['age']); gen = request.form['gender']; goal = request.form['goal']
                current_user.height = h; current_user.age = a; current_user.gender = gen; db.session.commit()
                session['app_data'] = create_plan(w, h, a, gen, goal)
                return redirect(url_for('index'))
            except: pass
        elif 'setup_quick' in request.form:
            session['app_data'] = create_plan(float(request.form['weight']), current_user.height, current_user.age, current_user.gender, request.form['goal'])
            return redirect(url_for('index'))

        # 2. UPDATE MEAL (LOGIC KỶ LUẬT)
        elif 'update_meal' in request.form and app_data:
            day = str(app_data['current_day']); idx = app_data['current_meal']
            keys = {0: 'breakfast', 1: 'lunch', 2: 'dinner'}; key = keys[idx]
            plan = app_data['menu_plan'][day]
            
            c_name = request.form.get('custom_name')
            c_calo = request.form.get('custom_calo')
            actual = 0

            # Ưu tiên nhập số tay
            if c_calo and c_calo.strip():
                actual = float(c_calo)
                if not c_name: c_name = "Món tự nhập"
                plan[key]['name'], plan['is_custom'][idx] = c_name, True
            
            # Nếu dùng AI
            elif request.form['update_type'] == 'custom':
                actual = ask_ai_calories(c_name)
                # Nếu AI lỗi 500 -> Báo lỗi
                if actual == 500: flash(f"⚠️ Lỗi kết nối AI. Vui lòng kiểm tra mạng.", "danger")
                
                plan[key]['name'] = f"{c_name} (AI: {actual})"
                plan['is_custom'][idx] = True
            else:
                actual = plan['targets'][idx]

            # Cập nhật số đã ăn
            plan['eaten'][idx] = actual
            plan[key]['calo'] = actual

            # --- KIỂM TRA SAU BỮA TRƯA (IDX=1) ---
            if idx == 1:
                total_an = sum(plan['eaten'][:2]) # Tổng Sáng + Trưa
                daily_max = app_data['daily_target']
                
                # Nếu ăn quá 90% quota cả ngày
                if total_an > daily_max * 0.9:
                    msg = f"Ngày {day}: Ăn lố {total_an} kcal (Sáng+Trưa)"
                    if 'warnings' not in app_data: app_data['warnings'] = []
                    app_data['warnings'].append(msg)
                    
                    flash(f"🚨 CẢNH BÁO: Ăn quá nhiều! Bữa tối bị chuyển sang chế độ Ăn Nhẹ.", "danger")

                    # Phạt: Đổi bữa tối
                    light_dish = random.choice(LIGHT_MEALS)
                    plan['dinner'] = light_dish
                    plan['dinner']['name'] = "🚨 " + light_dish['name']
                    plan['targets'][2] = light_dish['calo']
                    plan['is_custom'][2] = True # Khóa lại

            app_data['current_meal'] += 1
            if app_data['current_meal'] > 2:
                app_data['calorie_history'][int(day)] = sum(plan['eaten'])
                app_data['current_day'] += 1; app_data['current_meal'] = 0
                flash(f"Hoàn thành Ngày {day}!", "success"); session['app_data'] = app_data; return redirect(url_for('index'))
            
            session['app_data'] = app_data
            return redirect(url_for('index', day_view=day))

        # 3. FINAL
        elif 'submit_final_weight' in request.form:
            app_data['final_weight'] = float(request.form['final_weight'])
            app_data['ai_feedback'] = ask_ai_feedback(
                app_data['start_weight'], app_data['final_weight'], 
                app_data['profile']['goal'], app_data.get('warnings', [])
            )
            session['app_data'] = app_data; return redirect(url_for('index'))
        
        elif 'restart_option' in request.form:
            session.pop('app_data', None); return redirect(url_for('index'))

    view_mode = 'dashboard'; menu_today = None; chart_data = []
    if app_data:
        chart_data = app_data['calorie_history'][1:]
        req_day = request.args.get('day_view')
        if req_day and int(req_day) <= app_data['current_day'] and int(req_day) <= 7:
             view_mode = 'detail'; menu_today = app_data['menu_plan'][str(req_day)]

    return render_template('index.html', user=current_user, app_data=app_data, view_mode=view_mode, menu_today=menu_today, chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
