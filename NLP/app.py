from flask import Flask, render_template, request, session
from analyze_idea import analyze_key_phrases, analyze_game_idea, analyze_project_cost
from task_utils import analyze_animation_suggestions, generate_character_images, suggest_gameplay_code
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

# Azure configuration
text_analytics_endpoint = "https://projectgame.cognitiveservices.azure.com/"
text_analytics_key = "2KzapW8uHvXU36izit7Gqf299IOmrOfeBnNFCPnI3uczFZsiQDVJJQQJ99AKACYeBjFXJ3w3AAAaACOGPojV"
openai_endpoint = "https://botgame.openai.azure.com"
openai_key = "EyoMKPi0cdmUAujXRhLdlPew6vrPnHr9Zyj0EswXpopsuerw3MQ7JQQJ99ALACYeBjFXJ3w3AAABACOGfOMX"

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Essential for session handling


app = Flask(__name__)
app.secret_key = "your_secret_key"

# إعدادات البريد الإلكتروني
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # يمكن تغييره بناءً على مزود الخدمة
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # بريد المرسل
app.config['MAIL_PASSWORD'] = 'your_email_password'   # كلمة مرور المرسل

mail = Mail(app)

# بيانات المستخدمين المخزنة بشكل تجريبي (يمكن استبدالها بقاعدة بيانات)
users = {
    "user@example.com": "Password@123"  # بريد إلكتروني وكلمة مرور صحيحة
}

# Home page for analyzing game ideas
@app.route('/', methods=['GET', 'POST'])
def home():
    key_phrases_result = None
    ai_analysis_result = None

    if request.method == 'POST':
        game_idea = request.form['idea']
        session['game_idea'] = game_idea  # Store the game idea in the session
        key_phrases_result = analyze_key_phrases(game_idea, text_analytics_endpoint, text_analytics_key)
        ai_analysis_result = analyze_game_idea(game_idea, openai_endpoint, openai_key)

    return render_template('home.html', key_phrases=key_phrases_result, ai_analysis=ai_analysis_result)

# Project cost analysis page
@app.route('/cost', methods=['GET', 'POST'])
def cost():
    cost_analysis_result = None
    if request.method == 'POST':
        project_details = request.form['project_details']
        cost_analysis_result = analyze_project_cost(project_details, openai_endpoint, openai_key)

    return render_template('cost.html', cost_analysis=cost_analysis_result)

# Tasks analysis page
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    animation_suggestions = None
    character_images = None
    gameplay_code = None

    # Retrieve the game idea from the session
    game_details = session.get('game_idea', "Default game idea")

    if request.method == 'POST':
        task_details = request.form['task_details']
        animation_suggestions = analyze_animation_suggestions(task_details)
        gameplay_code = suggest_gameplay_code(task_details)

    # Generate character images using the game idea
    if game_details:
        character_images = generate_character_images(game_details)

    return render_template(
        'tasks.html',
        animation_suggestions=animation_suggestions,
        character_images=character_images,
        gameplay_code=gameplay_code
    )




# Feedback page route
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Handle the feedback logic (e.g., save to database, send email, etc.)
        print(f"Feedback received from {name} ({email}): {message}")

        # Redirect to a thank you page or display a success message
        return redirect(url_for('thank_you'))

    return render_template('feedback.html')

# Thank you page route
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')


# AIGP page route
@app.route('/aigp', methods=['GET'])
def aigp():
    return render_template('aigp.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists and the password matches
        if email in users and users[email] == password:
            session['user'] = email  # Save the user session
            flash("Login successful!", "success")

            # Send a confirmation email
            try:
                msg = Message("Login Successful", sender="your_email@gmail.com", recipients=[email])
                msg.body = f"Hello {email},\n\nYou have successfully logged into AIGP. Welcome!"
                mail.send(msg)
                flash("A confirmation email has been sent.", "info")
            except Exception as e:
                flash(f"An error occurred while sending the email: {e}", "danger")

            # Redirect to the profile page after login
            return redirect(url_for('profile'))

        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile')
def profile():
    if 'user' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))
    
    user_email = session.get('user')  # الحصول على بريد المستخدم من الجلسة
    return render_template('profile.html', user_email=user_email)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# صفحة تسجيل الحساب
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in users:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for('signup'))
        else:
            users[email] = password
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for('login'))
         
    print("Current working directory:", os.getcwd())
    print("Templates directory contents:", os.listdir("templates"))
    print("Looking for template in:", os.path.join(os.getcwd(), "templates/signup.html"))

    return render_template('signup.html')


# صفحة محمية تتطلب تسجيل الدخول
@app.route('/protected')
def protected():
    if 'user' not in session:
        flash("You must be logged in to access this page.", "warning")
        return redirect(url_for('login'))
    return f"Welcome, {session['user']}! <a href='/logout'>Logout</a>"



if __name__ == '__main__':
    app.run(debug=True, port=8080)

#تعديل