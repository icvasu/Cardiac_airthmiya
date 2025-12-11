from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import requests
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import os
from datetime import datetime
import telepot

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


import pickle
knn=pickle.load(open("model/model.pkl","rb"))


# Initialize Telegram Bot
bot = telepot.Bot("8547799339:AAFGrrVDxrUuXzXc_MEvt_ZANIXUUj4qrDs")
CHANNEL_ID = "1432292618"

# Initialize KNN model (you'll need to train this with your actual data)
# knn = KNeighborsClassifier(n_neighbors=3)

# Database initialization
def init_db():
    conn = sqlite3.connect('cardiac.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Detections table
    c.execute('''CREATE TABLE IF NOT EXISTS detections
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT,
                  age INTEGER,
                  gender TEXT,
                  height REAL,
                  weight REAL,
                  ecg REAL,
                  heart_rate REAL,
                  temperature REAL,
                  history TEXT,
                  prediction_result INTEGER,
                  risk_level TEXT,
                  deviation_percentage REAL,
                  condition TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('cardiac.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_thingspeak_data():
    # try:
    data = requests.get("https://api.thingspeak.com/channels/3189855/feeds.json?api_key=0ZLWWYV0VWY8CZP6&results=2")
    if data.status_code == 200:
        feeds = data.json()['feeds']
        if feeds:
            latest = feeds[-1]
            return {
                'heart_rate': latest.get('field1'),
                'temperature':latest.get('field3'),
                'ecg': latest.get('field2')
            }
    # except Exception as e:
    #     print(f"Error fetching ThingSpeak data: {e}")
    return {'heart_rate': '', 'temperature': '', 'ecg': ''}

def send_telegram_alert(name, age, gender, ecg, heart_rate, temperature, risk_level, deviation_percentage, history, condition, result):
    """Send formatted Telegram message based on risk level"""
    
    # Emoji mapping based on risk level
    risk_emojis = {
        'LOW': '🟢',
        'MODERATE': '🟡', 
        'HIGH': '🔴',
        'No Risk': '✅',
        'Unknown': '⚪'
    }
    
    # Ensure risk_level is a string, not a list
    if isinstance(risk_level, list):
        risk_level_str = risk_level[0] if risk_level else 'Unknown'
    else:
        risk_level_str = str(risk_level)
    
    emoji = risk_emojis.get(risk_level_str, '⚪')
    
    # Create formatted message
    if result == 1:  # Normal case
        message = f"""
🚨 *CARDIAC HEALTH REPORT* 🚨

*Patient Information:*
👤 *Name:* {name}
🎂 *Age:* {age}
⚧ *Gender:* {'Female' if gender == '1' else 'Male'}
📋 *History:* {history}

*Vital Signs:*
❤️ *Heart Rate:* {heart_rate} bpm
🌡️ *Temperature:* {temperature}°C
📊 *ECG Value:* {ecg}

*Assessment Results:*
{emoji} *Risk Level:* {risk_level_str}
📈 *Deviation Percentage:* {deviation_percentage}%
💡 *Condition:* {condition}

🎉 *Status:* Patient is Healthy! No immediate risks detected.
"""
    else:  # Abnormal case
        message = f"""
🚨 *CARDIAC HEALTH ALERT* 🚨

*Patient Information:*
👤 *Name:* {name}
🎂 *Age:* {age}
⚧ *Gender:* {'Female' if gender == '1' else 'Male'}
📋 *History:* {history}

*Vital Signs:*
❤️ *Heart Rate:* {heart_rate} bpm
🌡️ *Temperature:* {temperature}°C
📊 *ECG Value:* {ecg}

*Assessment Results:*
{emoji} *Risk Level:* {risk_level_str}
📈 *Deviation Percentage:* {deviation_percentage}%
💡 *Condition:* {condition}

⚠️ *Alert:* Requires medical attention!
"""
    
    try:
        bot.sendMessage(CHANNEL_ID, message, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                           (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    detections = conn.execute('''
        SELECT * FROM detections 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', detections=detections)

@app.route('/delete_detection/<int:detection_id>')
def delete_detection(detection_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM detections WHERE id = ? AND user_id = ?', 
                (detection_id, session['user_id']))
    conn.commit()
    conn.close()
    
    flash('Detection deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/input_form')
def input_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    thingspeak_data = get_thingspeak_data()
    print(thingspeak_data)
    return render_template('input_form.html', 
                         ecg=thingspeak_data['ecg'],
                         hb=thingspeak_data['heart_rate'],
                         temp=thingspeak_data['temperature'])

@app.route('/predict', methods=['POST'])
def predictPage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get form data
    name = request.form['name']
    age = int(request.form['age'])
    gender = request.form['Gender']
    height = float(request.form['height'])
    weight = float(request.form['Weight'])
    ecg = float(request.form['ECG'])
    heart_rate = float(request.form['Heart_Rate'])
    temperature = float(request.form['Temperature'])
    his = int(request.form['his'])
    
    history = "Cardiac Arrest Happened" if his == 1 else "No Previous Cardiac Arrest Happened"
    
    # Your prediction logic
    data = np.array([[age, 1 if gender == '1' else 0, height, weight, ecg, heart_rate, temperature]])
    
    # Mock prediction (replace with your actual KNN model)
    # my_prediction = [2]  # Example prediction
    my_prediction = knn.predict(data)
    
    result = my_prediction[0]
    print(f"\n\n\n\n\n{data} \n\n\n\n\n")
    print(f"\n\n\n\n\n{result} \n\n\n\n\n")
    avg = 367.2
    cent = abs(float(ecg) - avg) / avg * 100
    cent = f"{cent:.2f}"
    
    def classify_risk(result):
        if result in [5, 6, 7, 8, 9, 10]:
            return ["LOW", "Regular Checkups: Continue periodic monitoring of heart health to catch early warning signs if the condition progresses.",
                    "Avoid Excessive Stimulants: Limit caffeine, energy drinks, or other stimulants that might stress the heart.",
                    "Regular Exercise: Incorporate moderate physical activity, such as brisk walking or swimming, for at least 30 minutes a day, five times a week.",
                    "Balanced Diet: Focus on a heart-healthy diet rich in fruits, vegetables, whole grains, and lean proteins."]
        elif result in [2, 3, 4, 14]:
            return ["High", "Monitor Symptoms Closely: Be alert to signs like shortness of breath, dizziness, or palpitations and report them to a healthcare provider promptly.",
                    "Follow Medication Plans: Adhere strictly to prescribed medications or treatments to stabilize arrhythmia.",
                    "Stress Management: Practice relaxation techniques like yoga or mindfulness to reduce stress, which can exacerbate arrhythmias.",
                    "Quit Smoking: Eliminate tobacco use to reduce heart strain and improve cardiovascular health."]
        elif result in [15, 16]:
            return ["Moderate", "Immediate Medical Attention: Seek urgent medical care for severe symptoms or complications to prevent emergencies like cardiac arrest.",
                    "Restrict Strenuous Activities: Avoid activities that may overexert the heart, as advised by your doctor.",
                    "Low-Sodium Diet: Adopt a diet that minimizes salt intake to manage blood pressure and reduce heart stress.",
                    "Weight Management: Maintain a healthy weight through a supervised diet and light, safe exercise as recommended by healthcare professionals."]
        elif result == 1:
            return ['Normal']
    
    risk = classify_risk(result)
    risk_level = risk[0]  # Extract the risk level string from the list
    
    # Map result to condition
    result_map = {
        1: 'Normal',
        2: 'Ischemic changes (Coronary Artery)',
        3: 'Old Anterior Myocardial Infarction',
        4: 'Old Inferior Myocardial Infarction',
        5: 'Sinus tachycardia',
        6: 'Ventricular Premature Contraction (PVC)',
        7: 'Supraventricular Premature Contraction',
        8: 'Left bundle branch block',
        9: 'Right bundle branch block',
        10: 'Left ventricle hypertrophy',
        14: 'Atrial Fibrillation or Flutter',
        15: 'Others1',
        16: 'Others2'
    }
    
    res = result_map.get(result, 'Normal')
    
    # Save to database
    conn = get_db_connection()
    conn.execute('''INSERT INTO detections 
                    (user_id, name, age, gender, height, weight, ecg, heart_rate, temperature, history, prediction_result, risk_level, deviation_percentage, condition)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (session['user_id'], name, age, gender, height, weight, ecg, heart_rate, temperature, history, int(result), risk_level, cent, res))
    conn.commit()
    conn.close()
    
    # Send Telegram alert - pass risk_level (string) instead of risk (list)
    telegram_sent = send_telegram_alert(
        name=name,
        age=age,
        gender=gender,
        ecg=ecg,
        heart_rate=heart_rate,
        temperature=temperature,
        risk_level=risk_level if result != 1 else "No Risk",
        deviation_percentage=cent,
        history=history,
        condition=res,
        result=result
    )
    
    if telegram_sent:
        flash('Assessment completed and alert sent successfully!', 'success')
    else:
        flash('Assessment completed but failed to send Telegram alert.', 'warning')
    
    return render_template('result.html', 
                         name=name, age=age, gender=gender, ecg=ecg, 
                         heart_rate=heart_rate, temperature=temperature,
                         history=history, result=res, risk=risk, 
                         deviation_percentage=cent,
                         telegram_sent=telegram_sent,
                         clsno=my_prediction[0])

if __name__ == '__main__':
    app.run(debug=True)