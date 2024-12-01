from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '5e7eb9a6c28b4b3f8f0c1d2e4a6b8c0d'  # Nouvelle clé secrète sécurisée
app.config['WTF_CSRF_SECRET_KEY'] = '8f0c1d2e4a6b8c0d5e7eb9a6c28b4b3f'  # Clé pour la protection CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photogram.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèles de base de données
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    profile_photo = db.Column(db.String(255), default='default_profile.png')
    bio = db.Column(db.String(500))
    
    # Add follow relationships
    followers = db.relationship(
        'Follow', 
        foreign_keys='Follow.followed_id', 
        backref='followed', 
        lazy='dynamic'
    )
    following = db.relationship(
        'Follow', 
        foreign_keys='Follow.follower_id', 
        backref='follower', 
        lazy='dynamic'
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S\'inscrire')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ajout de fonctions de pièges
def get_scary_message():
    scary_messages = [
        "👻 Attention, un fantôme se cache derrière toi !",
        "🕷️ Un énorme araignée vient de tomber sur ton écran !",
        "🔪 Quelqu'un te regarde... 👀",
        "💀 Tu es sûr de vouloir continuer ?",
        "🚨 ALERTE ROUGE ! Opération piège en cours !"
    ]
    return random.choice(scary_messages)

@app.route('/scary_trap', methods=['GET'])
def scary_trap():
    trap_type = random.choice(['message', 'sound', 'visual'])
    
    if trap_type == 'message':
        return jsonify({
            'type': 'message',
            'content': get_scary_message()
        })
    elif trap_type == 'sound':
        return jsonify({
            'type': 'sound',
            'content': 'scream.mp3'  # Vous devrez ajouter ce fichier audio
        })
    else:
        return jsonify({
            'type': 'visual',
            'content': 'Écran devient temporairement rouge ou noir'
        })

@app.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)

        if file:
            # Créer le dossier uploads s'il n'existe pas
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_post = Post(
                image_path=f"uploads/{filename}",
                caption=request.form.get('caption', ''),
                user_id=current_user.id
            )
            db.session.add(new_post)
            db.session.commit()
            
            flash('Photo publiée avec succès!')
            return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session['show_creepy_modal'] = True  # Ajouter l'indicateur
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        flash('Email ou mot de passe incorrect', 'error')
    elif request.method == 'POST':
        print('Form errors:', form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erreur dans {getattr(form, field).label.text}: {error}', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Cet email est déjà utilisé', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(username=form.username.data).first():
            flash('Ce nom d\'utilisateur est déjà utilisé', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Votre compte a été créé avec succès!', 'success')
        return redirect(url_for('login'))
    elif request.method == 'POST':
        # More detailed error logging
        print('Form errors:', form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erreur dans {getattr(form, field).label.text}: {error}', 'error')
                print(f"Erreur dans {getattr(form, field).label.text}: {error}")
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    session['show_creepy_modal'] = True  # Ajouter l'indicateur
    logout_user()
    return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'status': 'unlike', 'likes': len(post.likes)})
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'status': 'like', 'likes': len(post.likes)})

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': {
                    'username': comment.author.username
                },
                'timestamp': comment.timestamp.strftime('%d/%m/%Y %H:%M')
            }
        })
    return jsonify({'status': 'error', 'message': 'Commentaire vide'})

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id == current_user.id:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Non autorisé'})

@app.route('/get_comments/<int:post_id>')
def get_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = []
    for comment in post.comments:
        comments.append({
            'content': comment.content,
            'username': comment.author.username,
            'timestamp': comment.timestamp.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(comments)

@app.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('query', '')
    if not query:
        return render_template('search_results.html', users=[])
    
    # Recherche par nom d'utilisateur ou email (insensible à la casse)
    users = User.query.filter(
        db.or_(
            User.username.ilike(f'%{query}%'), 
            User.email.ilike(f'%{query}%')
        )
    ).all()
    
    return render_template('search_results.html', users=users, query=query)

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow == current_user:
        flash('Vous ne pouvez pas vous suivre vous-même')
        return redirect(url_for('profile', user_id=user_id))
    
    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first()
    
    if existing_follow:
        flash('Vous suivez déjà cet utilisateur')
    else:
        new_follow = Follow(follower_id=current_user.id, followed_id=user_id)
        db.session.add(new_follow)
        db.session.commit()
        flash('Vous suivez maintenant cet utilisateur')
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow_user(user_id):
    follow = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first()
    
    if follow:
        db.session.delete(follow)
        db.session.commit()
        flash('Vous ne suivez plus cet utilisateur')
    else:
        flash('Vous ne suiviez pas cet utilisateur')
    
    return redirect(url_for('profile', user_id=user_id))

@app.route('/profile', defaults={'user_id': None}, methods=['GET', 'POST'])
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    # Si aucun user_id n'est fourni, utiliser l'utilisateur actuel
    if user_id is None:
        user_id = current_user.id
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST' and request.files.get('profile_photo'):
        file = request.files['profile_photo']
        if file and file.filename != '':
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if not file.filename.lower().split('.')[-1] in allowed_extensions:
                flash('Type de fichier non autorisé. Utilisez PNG, JPG, JPEG ou GIF.')
                return redirect(url_for('profile', user_id=user_id))
            
            # Validate file size (max 5MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > 5 * 1024 * 1024:  # 5MB
                flash('La taille du fichier ne doit pas dépasser 5 Mo.')
                return redirect(url_for('profile', user_id=user_id))
            
            # Generate unique filename
            filename = f"profile_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.split('.')[-1]}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                
                # Update user's profile photo
                user.profile_photo = f"uploads/{filename}"
                db.session.commit()
                flash('Photo de profil mise à jour avec succès')
            except Exception as e:
                flash(f'Erreur lors du téléchargement : {str(e)}')
                db.session.rollback()
    
    is_following = Follow.query.filter_by(
        follower_id=current_user.id, 
        followed_id=user_id
    ).first() is not None
    
    user_posts = Post.query.filter_by(user_id=user_id).order_by(Post.timestamp.desc()).all()
    
    return render_template(
        'profile.html', 
        user=user, 
        posts=user_posts, 
        is_following=is_following
    )

@app.route('/messages')
@login_required
def messages():
    # Récupérer la liste des conversations
    sent_messages = db.session.query(Message.receiver_id, User.username, 
        db.func.max(Message.timestamp).label('last_message_time')) \
        .join(User, Message.receiver_id == User.id) \
        .filter(Message.sender_id == current_user.id) \
        .group_by(Message.receiver_id, User.username)

    received_messages = db.session.query(Message.sender_id, User.username, 
        db.func.max(Message.timestamp).label('last_message_time')) \
        .join(User, Message.sender_id == User.id) \
        .filter(Message.receiver_id == current_user.id) \
        .group_by(Message.sender_id, User.username)

    # Combiner et trier les conversations
    conversations = {}
    for receiver_id, username, timestamp in sent_messages:
        conversations[receiver_id] = {'username': username, 'timestamp': timestamp}
    
    for sender_id, username, timestamp in received_messages:
        if sender_id in conversations:
            if timestamp > conversations[sender_id]['timestamp']:
                conversations[sender_id]['timestamp'] = timestamp
        else:
            conversations[sender_id] = {'username': username, 'timestamp': timestamp}

    conversations = [
        {'user_id': user_id, 'username': data['username'], 'timestamp': data['timestamp']}
        for user_id, data in conversations.items()
    ]
    conversations.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('messages.html', conversations=conversations)

@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        content = request.form.get('content').strip()
        if content:
            # Vérifier s'il n'y a pas de message identique récemment envoyé
            recent_message = Message.query.filter_by(
                sender_id=current_user.id,
                receiver_id=user_id,
                content=content
            ).order_by(Message.timestamp.desc()).first()

            if not recent_message or (datetime.utcnow() - recent_message.timestamp).total_seconds() > 5:
                message = Message(
                    sender_id=current_user.id,
                    receiver_id=user_id,
                    content=content
                )
                db.session.add(message)
                db.session.commit()
            
            return redirect(url_for('chat', user_id=user_id))

    # Marquer les messages comme lus
    unread_messages = Message.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user.id,
        is_read=False
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    db.session.commit()

    # Récupérer tous les messages entre les deux utilisateurs
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    return render_template('chat.html', messages=messages, other_user=other_user)

@app.route('/api/messages/<int:user_id>/unread')
@login_required
def get_unread_messages(user_id):
    messages = Message.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user.id,
        is_read=False
    ).order_by(Message.timestamp.asc()).all()
    
    # Marquer les messages comme lus
    for message in messages:
        message.is_read = True
    db.session.commit()
    
    return jsonify([{
        'id': message.id,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%H:%M')
    } for message in messages])

@app.route('/clear_modal_flag', methods=['POST'])
def clear_modal_flag():
    session.pop('show_creepy_modal', None)
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
