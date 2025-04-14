from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import os
import math  # 添加 math 模組
import json
import sys
import threading
import webbrowser
import socket
from werkzeug.utils import secure_filename  # 添加這行
import re
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 啟用跨域支持

# 檢查端口是否可用
def is_port_available(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except:
        return False

# 找到可用的端口
def find_available_port(start_port=5001):
    port = start_port
    while not is_port_available(port):
        port += 1
    return port

# 獲取應用程序的根目錄
if getattr(sys, 'frozen', False):
    # 如果是打包後的應用
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是開發環境
    application_path = os.path.dirname(os.path.abspath(__file__))

# 配置文件路徑
CONFIG_PATH = os.path.join(application_path, 'config.json')

# 默認配置
DEFAULT_CONFIG = {
    "excel_path": "",
    "last_modified": None,
    "port": 5001
}

def load_config():
    """加載配置文件"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 如果配置文件不存在，創建默認配置
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"加載配置文件錯誤: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config):
    """保存配置文件"""
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        # 嘗試保存配置
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
            
        # 確保文件已經被正確寫入
        if os.path.exists(CONFIG_PATH):
            return True
        return False
    except Exception as e:
        print(f"保存配置文件錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

# 緩存數據
excel_data = None
excel_data_u = None  # 新增：用於存儲 U 欄數據
last_modified_time = None

def calculate_stamp_duty(price):
    try:
        price = float(str(price).replace(',', ''))
        if price <= 4000000:
            return math.ceil(100)
        elif price <= 4323780:
            return math.ceil(100 + (price - 4000000) * 0.2)
        elif price <= 4500000:
            return math.ceil(price * 0.015)
        elif price <= 4935480:
            return math.ceil(67500 + (price - 4500000) * 0.1)
        elif price <= 6000000:
            return math.ceil(price * 0.0225)
        elif price <= 6642860:
            return math.ceil(135000 + (price - 6000000) * 0.1)
        elif price <= 9000000:
            return math.ceil(price * 0.03)
        elif price <= 10080000:
            return math.ceil(270000 + (price - 9000000) * 0.1)
        elif price <= 20000000:
            return math.ceil(price * 0.0375)
        elif price <= 21739120:
            return math.ceil(750000 + (price - 20000000) * 0.1)
        else:
            return math.ceil(price * 0.0425)
    except (ValueError, TypeError):
        return 0

def format_currency(value):
    try:
        # 將字符串轉換為浮點數
        if isinstance(value, str):
            value = float(value.replace(',', ''))
        # 格式化為帶千位分隔符和兩位小數的字符串
        return f"{value:,.2f}"
    except (ValueError, TypeError):
        return value

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'GET':
        config = load_config()
        excel_exists = False
        if config.get('excel_path'):
            excel_exists = os.path.exists(config['excel_path'])
        
        return jsonify({
            'success': True,
            'config': config,
            'excel_exists': excel_exists
        })
    
    elif request.method == 'POST':
        try:
            print("Received POST request to /api/config")  # 添加調試信息
            data = request.get_json()
            print("Request data:", data)  # 添加調試信息
            
            if not data:
                print("No JSON data received")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': '沒有接收到數據'
                })
            
            new_path = data.get('excel_path')
            print("Received path:", new_path)  # 添加調試信息
            
            if not new_path:
                print("Empty path received")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': 'Excel 文件路徑不能為空'
                })
            
            # 如果路徑是相對路徑，轉換為絕對路徑
            if not os.path.isabs(new_path):
                new_path = os.path.abspath(new_path)
                print("Converted to absolute path:", new_path)  # 添加調試信息
            
            # 驗證文件是否存在且為 Excel 文件
            if not os.path.exists(new_path):
                print(f"File does not exist: {new_path}")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': '文件不存在'
                })
                
            if not new_path.lower().endswith(('.xlsx', '.xls')):
                print(f"Invalid file extension: {new_path}")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': '請選擇有效的 Excel 文件'
                })
            
            # 嘗試讀取 Excel 文件
            try:
                print(f"Attempting to read Excel file: {new_path}")  # 添加調試信息
                pd.read_excel(new_path)
                print("Successfully read Excel file")  # 添加調試信息
            except Exception as e:
                print(f"Failed to read Excel file: {str(e)}")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': f'無法讀取 Excel 文件: {str(e)}'
                })
            
            # 保存新配置
            config = load_config()
            config['excel_path'] = new_path
            if save_config(config):
                print("Configuration saved successfully")  # 添加調試信息
                # 重新加載 Excel 數據
                success, message = load_excel_data()
                print(f"Reload data result: success={success}, message={message}")  # 添加調試信息
                return jsonify({
                    'success': True,
                    'message': 'Excel 文件路徑已更新'
                })
            else:
                print("Failed to save configuration")  # 添加調試信息
                return jsonify({
                    'success': False,
                    'message': '保存配置失敗'
                })
                
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # 添加調試信息
            import traceback
            print(traceback.format_exc())  # 添加完整的錯誤追踪
            return jsonify({
                'success': False,
                'message': f'更新配置失敗: {str(e)}'
            })

def load_excel_data():
    global excel_data, excel_data_u, last_modified_time
    
    # 從配置文件獲取 Excel 路徑
    config = load_config()
    excel_path = config.get('excel_path')
    
    if not excel_path:
        # 如果沒有設置 Excel 路徑，返回空數據但不報錯
        excel_data = {}
        excel_data_u = {}
        return True, "未設置 Excel 文件路徑"
    
    if not os.path.exists(excel_path):
        # 如果文件不存在，返回空數據但不報錯
        excel_data = {}
        excel_data_u = {}
        return True, "Excel 文件不存在"
    
    # 檢查文件最後修改時間
    current_modified_time = os.path.getmtime(excel_path)
    
    # 如果數據已經加載且文件未修改，直接返回緩存的數據
    if excel_data is not None and last_modified_time == current_modified_time:
        return True, "使用緩存數據"
    
    try:
        # 讀取 Excel 文件
        df = pd.read_excel(excel_path)
        
        # 檢查是否存在所需的列
        if 'Ref' not in df.columns or 'Tel' not in df.columns:
            # 嘗試查找可能的列名
            possible_ref_cols = [col for col in df.columns if 'ref' in str(col).lower()]
            possible_tel_cols = [col for col in df.columns if 'tel' in str(col).lower()]
            
            # 使用找到的第一個匹配列名
            ref_col = possible_ref_cols[0] if possible_ref_cols else 'Ref'
            tel_col = possible_tel_cols[0] if possible_tel_cols else 'Tel'
        else:
            ref_col = 'Ref'
            tel_col = 'Tel'
        
        # 處理電話號碼數據
        excel_data = {}
        for _, row in df.iterrows():
            ref_str = str(row[ref_col]).strip()
            if ref_str.endswith('.0'):
                ref_str = ref_str[:-2]
            
            tel_str = str(row[tel_col]).strip() if pd.notna(row[tel_col]) else ''
            
            if ref_str and tel_str:
                excel_data[ref_str] = tel_str
        
        # 處理 U 欄數據和其他欄位
        excel_data_u = {}
        for _, row in df.iterrows():
            ref_str = str(row[ref_col]).strip()
            if ref_str.endswith('.0'):
                ref_str = ref_str[:-2]
            
            # 檢查 Nature 欄位（第4列，索引3）
            nature = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
            
            # 獲取所有需要的欄位
            u_value = str(row.iloc[20]).strip() if pd.notna(row.iloc[20]) else ''
            phone = str(row[tel_col]).strip() if pd.notna(row[tel_col]) else ''
            property_info = str(row['Matter/Property']).strip() if pd.notna(row['Matter/Property']) else ''
            client_name = str(row['Client']).strip() if pd.notna(row['Client']) else ''
            
            # 讀取 J 欄（Further Deposit）的數據
            further_deposit = row.iloc[9] if pd.notna(row.iloc[9]) else 0
            try:
                # 嘗試轉換為浮點數
                further_deposit = float(str(further_deposit).replace(',', ''))
            except (ValueError, TypeError):
                further_deposit = 0
            
            # 檢查是否為 P 買入文件
            is_buyer = nature.upper().startswith('P')
            
            if ref_str:
                excel_data_u[ref_str] = {
                    'u_value': u_value,
                    'phone': phone,
                    'property_info': property_info,
                    'client_name': client_name,
                    'further_deposit': further_deposit if is_buyer else 0,  # 只有在 P 買入文件時才設置加訂
                    'is_buyer': is_buyer
                }
        
        last_modified_time = current_modified_time
        return True, "數據已更新"
    except Exception as e:
        # 如果讀取失敗，返回空數據但不中斷服務
        excel_data = {}
        excel_data_u = {}
        return True, f"讀取 Excel 失敗: {str(e)}"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/styles.css')
def serve_css():
    return send_from_directory('.', 'styles.css')

@app.route('/api/search/<ref>')
def search(ref):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    phone = excel_data.get(ref)
    return jsonify({
        'found': phone is not None,
        'phone': phone if phone else None,
        'message': '找到電話號碼' if phone else '找不到對應的電話號碼'
    })

@app.route('/api/search_u/<ref>')
def search_u(ref):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    # 檢查是否為電話號碼搜尋
    is_phone_search = len(ref) > 6 or not ref.isdigit()
    
    if is_phone_search:
        # 電話號碼搜尋
        results = []
        search_number = ref.replace(' ', '')
        
        for ref_num, data in excel_data_u.items():
            if 'phone' in data and data['phone']:
                phone_clean = str(data['phone']).replace(' ', '')
                if search_number in phone_clean:
                    results.append({
                        'ref_number': ref_num,
                        'value': data['u_value'],
                        'phone': data['phone']
                    })
        
        return jsonify({
            'found': len(results) > 0,
            'is_phone_search': True,
            'results': results,
            'message': f'找到 {len(results)} 個相關記錄' if results else '找不到相關記錄'
        })
    else:
        # 檔案編號搜尋邏輯
        # 清理檔案編號格式
        ref = ref.strip()
        if ref.endswith('.0'):
            ref = ref[:-2]
        
        data = excel_data_u.get(ref)
        if data:
            # 從 U 欄數據中提取完整的檔案編號
            u_value = data['u_value']
            ref_match = u_value.split('\n')[0] if u_value else ''  # 獲取第一行
            
            # 檢查檔案編號是否以 P 結尾來判斷是否為買家
            is_buyer = ref_match.strip().endswith('P')
            
            return jsonify({
                'found': True,
                'value': data['u_value'],
                'phone': data['phone'],
                'is_buyer': is_buyer,
                'ref_number': ref,
                'property_info': data.get('property_info', ''),
                'client_name': data.get('client_name', ''),
                'further_deposit': data.get('further_deposit', 0)
            })
        return jsonify({
            'found': False,
            'message': '找不到對應的數據'
        })

@app.route('/api/refresh')
def refresh():
    success, message = load_excel_data()
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/update_amounts', methods=['POST'])
def update_amounts():
    try:
        data = request.get_json()
        purchase_price = float(str(data['purchase_price']).replace(',', '') or 0)
        further_deposit = float(str(data['further_deposit']).replace(',', '') or 0)
        deed_fee = float(data.get('deed_fee', 0) or 0)
        lawyer_fee = float(data.get('lawyer_fee', 5000) or 5000)  # 使用前端傳入的值，默認為 5000
        
        stamp_duty = calculate_stamp_duty(purchase_price)
        total_amount = further_deposit + stamp_duty + lawyer_fee + deed_fee

        formatted_notice = f"""買家所需文件:
1.⁠ ⁠身分證
2.⁠ ⁠臨時買賣合約正本(如有)
3.⁠ ⁠支票以付訂金、印花稅及律師費上期，詳細金額會面時會確認（如沒支票可以選用銀行轉帳）

請準備支票/本票一張:
金額:HK${format_currency(total_amount)}
以支付以下事項:
印花稅:HK${format_currency(stamp_duty)}
加訂:HK${format_currency(further_deposit)}
契費:HK${format_currency(deed_fee)}
律師費定金:HK${format_currency(lawyer_fee)}

抬頭:
鄺 來 興 律 師 行
KEVIN L. H. KWONG & CO. SOLICITORS"""

        return jsonify({
            'success': True,
            'formatted_notice': formatted_notice,
            'total_amount': format_currency(total_amount)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/search_by_client/<client_name>')
def search_by_client(client_name):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    client_name = client_name.lower()
    exact_matches = []
    fuzzy_matches = []
    
    for ref_num, data in excel_data_u.items():
        if data and 'client_name' in data:
            current_client = str(data['client_name']).lower()
            
            if client_name in current_client:
                exact_matches.append({
                    'ref_number': ref_num,
                    'value': data['u_value'],
                    'phone': data['phone']
                })
            elif not exact_matches:
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, client_name, current_client).ratio()
                if similarity >= 0.6:
                    fuzzy_matches.append({
                        'ref_number': ref_num,
                        'value': data['u_value'],
                        'phone': data['phone'],
                        'similarity': int(similarity * 100)
                    })
    
    if exact_matches:
        return jsonify({
            'found': True,
            'exact_matches': exact_matches,
            'message': f'找到 {len(exact_matches)} 個完全匹配的記錄'
        })
    
    if fuzzy_matches:
        fuzzy_matches.sort(key=lambda x: x['similarity'], reverse=True)
        return jsonify({
            'found': True,
            'fuzzy_matches': fuzzy_matches,
            'message': f'找到 {len(fuzzy_matches)} 個相似的記錄'
        })
    
    return jsonify({
        'found': False,
        'message': '找不到相關記錄'
    })

@app.route('/api/search_by_property/<property_info>')
def search_by_property(property_info):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    property_info = property_info.lower()
    exact_matches = []
    fuzzy_matches = []
    
    for ref_num, data in excel_data_u.items():
        if data and 'property_info' in data:
            current_property = str(data['property_info']).lower()
            
            if property_info in current_property:
                exact_matches.append({
                    'ref_number': ref_num,
                    'value': data['u_value'],
                    'phone': data['phone']
                })
            elif not exact_matches:
                from difflib import SequenceMatcher
                similarity = SequenceMatcher(None, property_info, current_property).ratio()
                if similarity >= 0.6:
                    fuzzy_matches.append({
                        'ref_number': ref_num,
                        'value': data['u_value'],
                        'phone': data['phone'],
                        'similarity': int(similarity * 100)
                    })
    
    if exact_matches:
        return jsonify({
            'found': True,
            'exact_matches': exact_matches,
            'message': f'找到 {len(exact_matches)} 個完全匹配的記錄'
        })
    
    if fuzzy_matches:
        fuzzy_matches.sort(key=lambda x: x['similarity'], reverse=True)
        return jsonify({
            'found': True,
            'fuzzy_matches': fuzzy_matches,
            'message': f'找到 {len(fuzzy_matches)} 個相似的記錄'
        })
    
    return jsonify({
        'found': False,
        'message': '找不到相關記錄'
    })

@app.route('/api/search_phone/<phone>')
def search_phone(phone):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    results = []
    search_number = phone.replace(' ', '')
    
    for ref_num, data in excel_data_u.items():
        if 'phone' in data and data['phone']:
            phone_clean = str(data['phone']).replace(' ', '')
            if search_number in phone_clean:
                results.append({
                    'ref_number': ref_num,
                    'value': data['u_value'],
                    'phone': data['phone']
                })
    
    return jsonify({
        'success': True,
        'results': results,
        'message': f'找到 {len(results)} 個相關記錄' if results else '找不到相關記錄'
    })

@app.route('/api/search_client/<client>')
def search_client(client):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    results = []
    search_term = client.lower()
    
    for ref_num, data in excel_data_u.items():
        if 'client_name' in data and data['client_name']:
            if search_term in data['client_name'].lower():
                results.append({
                    'ref_number': ref_num,
                    'value': data['u_value'],
                    'phone': data['phone']
                })
    
    return jsonify({
        'success': True,
        'results': results,
        'message': f'找到 {len(results)} 個相關記錄' if results else '找不到相關記錄'
    })

@app.route('/api/search_property/<property>')
def search_property(property):
    success, message = load_excel_data()
    if not success:
        return jsonify({'error': message}), 500
    
    results = []
    search_term = property.lower()
    
    for ref_num, data in excel_data_u.items():
        if 'property_info' in data and data['property_info']:
            if search_term in data['property_info'].lower():
                results.append({
                    'ref_number': ref_num,
                    'value': data['u_value'],
                    'phone': data['phone']
                })
    
    return jsonify({
        'success': True,
        'results': results,
        'message': f'找到 {len(results)} 個相關記錄' if results else '找不到相關記錄'
    })

@app.route('/api/upload_excel', methods=['POST'])
def upload_excel():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '沒有收到文件'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '沒有選擇文件'
            })
        
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'message': '請選擇有效的 Excel 文件'
            })
        
        # 確保上傳目錄存在
        upload_dir = os.path.join(application_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 安全地保存文件名
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 嘗試讀取 Excel 文件
        try:
            pd.read_excel(file_path)
        except Exception as e:
            os.remove(file_path)  # 如果讀取失敗，刪除文件
            return jsonify({
                'success': False,
                'message': f'無法讀取 Excel 文件: {str(e)}'
            })
        
        # 更新配置
        config = load_config()
        config['excel_path'] = file_path
        if save_config(config):
            # 重新加載 Excel 數據
            success, message = load_excel_data()
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Excel 文件已上傳並配置'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'Excel 文件已上傳但配置失敗: {message}'
                })
        else:
            os.remove(file_path)  # 如果保存配置失敗，刪除文件
            return jsonify({
                'success': False,
                'message': '保存配置失敗'
            })
                
    except Exception as e:
        print(f"上傳文件錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'上傳文件失敗: {str(e)}'
        })

@app.route('/api/search_ref_u/<ref_number>')
def search_ref_u(ref_number):
    try:
        # 檢查是否有數據
        if not excel_data_u:
            return jsonify({
                'success': False,
                'message': '沒有可用的數據'
            })
        
        # 查找記錄
        if ref_number in excel_data_u:
            data = excel_data_u[ref_number]
            
            # 直接使用 U 欄資料，並添加提示訊息
            lines = data['u_value'] if data['u_value'] else ''
            lines = f"{lines}\n\n請細閱以上資料是否正確"
            
            # 從 U 欄文本中提取樓價
            price_match = re.search(r'樓價:([\d,]+\.?\d*)', lines)
            cleanPrice = 0
            if price_match:
                try:
                    cleanPrice = float(price_match.group(1).replace(',', ''))
                except ValueError:
                    cleanPrice = 0
            
            # 獲取電話號碼
            phoneNumber = data['phone']
            
            return jsonify({
                'success': True,
                'lines': lines,
                'phone': phoneNumber,
                'purchase_price': cleanPrice,
                'further_deposit': data['further_deposit'],
                'is_buyer': data['is_buyer']
            })
        else:
            return jsonify({
                'success': False,
                'message': '找不到相關記錄'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查詢失敗: {str(e)}'
        })

def start_browser(port):
    """啟動瀏覽器"""
    url = f'http://localhost:{port}'
    webbrowser.open(url)

def run_app():
    """運行應用程序"""
    try:
        # 加載配置
        config = load_config()
        
        # 獲取可用端口
        port = find_available_port(config.get('port', 5001))
        
        # 更新配置中的端口
        config['port'] = port
        save_config(config)
        
        # 啟動瀏覽器的線程
        threading.Timer(1.5, start_browser, args=[port]).start()
        
        # 運行 Flask 應用
        app.run(host='localhost', port=port, debug=False)
        
    except Exception as e:
        print(f"應用程序啟動錯誤: {str(e)}")
        import traceback
        print(traceback.format_exc())

# 初始化任務數據庫
def init_task_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_number TEXT NOT NULL,
            task_content TEXT NOT NULL,
            due_date TEXT,
            due_time TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 在應用啟動時初始化數據庫
init_task_db()

# 添加任務相關的API端點
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        
        # 獲取所有任務
        c.execute('SELECT * FROM tasks ORDER BY due_date, due_time')
        tasks = c.fetchall()
        
        # 格式化任務數據
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'id': task[0],
                'file_number': task[1],
                'task_content': task[2],
                'due_date': task[3],
                'due_time': task[4],
                'created_at': task[5],
                'updated_at': task[6]
            })
        
        conn.close()
        return jsonify({'success': True, 'tasks': formatted_tasks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.json
        file_number = data.get('file_number')
        task_content = data.get('task_content')
        due_date = data.get('due_date')
        due_time = data.get('due_time')
        
        if not file_number or not task_content:
            return jsonify({'success': False, 'error': '檔案編號和任務內容不能為空'})
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO tasks (file_number, task_content, due_date, due_time, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (file_number, task_content, due_date, due_time, current_time, current_time))
        
        conn.commit()
        task_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'task': {
                'id': task_id,
                'file_number': file_number,
                'task_content': task_content,
                'due_date': due_date,
                'due_time': due_time,
                'created_at': current_time,
                'updated_at': current_time
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.json
        file_number = data.get('file_number')
        task_content = data.get('task_content')
        due_date = data.get('due_date')
        due_time = data.get('due_time')
        
        if not file_number or not task_content:
            return jsonify({'success': False, 'error': '檔案編號和任務內容不能為空'})
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute('''
            UPDATE tasks 
            SET file_number = ?, 
                task_content = ?, 
                due_date = ?, 
                due_time = ?, 
                updated_at = ?
            WHERE id = ?
        ''', (file_number, task_content, due_date, due_time, current_time, task_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'task': {
                'id': task_id,
                'file_number': file_number,
                'task_content': task_content,
                'due_date': due_date,
                'due_time': due_time,
                'updated_at': current_time
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    run_app() 