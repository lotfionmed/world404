from app import app, db, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Supprimer toutes les tables existantes
        db.drop_all()
        
        # Créer les tables
        db.create_all()
        
        # Créer des utilisateurs de test
        test_users = [
            User(
                username='john_doe', 
                email='john@example.com', 
                password=generate_password_hash('password123'),
                profile_photo='default_profile.png',
                bio='Passionné de photographie'
            ),
            User(
                username='jane_smith', 
                email='jane@example.com', 
                password=generate_password_hash('password456'),
                profile_photo='default_profile.png',
                bio='Voyageuse et artiste'
            ),
            User(
                username='alice_wonder', 
                email='alice@example.com', 
                password=generate_password_hash('password789'),
                profile_photo='default_profile.png',
                bio='Développeuse et créative'
            )
        ]
        
        # Ajouter les utilisateurs à la session
        for user in test_users:
            db.session.add(user)
        
        # Valider et sauvegarder les changements
        db.session.commit()
        
        print('Base de données initialisée avec succès !')

if __name__ == '__main__':
    init_db()
