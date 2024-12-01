from app import app, db, Message

def migrate():
    with app.app_context():
        # Créer la table des messages
        db.create_all()
        print("Migration terminée avec succès !")

if __name__ == '__main__':
    migrate()
