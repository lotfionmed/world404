from app import app, db, User, Follow, Post
from werkzeug.security import generate_password_hash

def create_test_users():
    # Clear existing users
    db.session.query(User).delete()
    db.session.query(Follow).delete()
    db.session.query(Post).delete()
    
    # Create test users
    users = [
        User(
            username='alice', 
            email='alice@example.com', 
            password=generate_password_hash('password123'),
            bio='Photographe passionnée'
        ),
        User(
            username='bob', 
            email='bob@example.com', 
            password=generate_password_hash('password456'),
            bio='Amoureux des voyages'
        ),
        User(
            username='charlie', 
            email='charlie@example.com', 
            password=generate_password_hash('password789'),
            bio='Artiste créatif'
        )
    ]
    
    # Add users to the database
    db.session.add_all(users)
    db.session.commit()
    
    # Create some follow relationships
    follow1 = Follow(follower_id=users[0].id, followed_id=users[1].id)
    follow2 = Follow(follower_id=users[1].id, followed_id=users[0].id)
    db.session.add_all([follow1, follow2])
    
    # Create some posts
    posts = [
        Post(
            image_path='uploads/default_profile.png', 
            caption='Ma première photo!', 
            user_id=users[0].id
        ),
        Post(
            image_path='uploads/default_profile.png', 
            caption='Voyage en montagne', 
            user_id=users[1].id
        )
    ]
    db.session.add_all(posts)
    
    db.session.commit()
    print("Test data created successfully!")

def test_user_search():
    with app.test_client() as client:
        # Login first
        response = client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Search for users
        response = client.get('/search_users?query=bob')
        assert b'bob' in response.data, "User search failed"
        print("User search test passed!")

def test_follow_unfollow():
    with app.test_client() as client:
        # Login as Alice
        client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Get Bob's user ID
        bob = User.query.filter_by(username='bob').first()
        
        # Test follow
        response = client.post(f'/follow/{bob.id}', follow_redirects=True)
        assert b'Vous suivez maintenant cet utilisateur' in response.data
        
        # Test unfollow
        response = client.post(f'/unfollow/{bob.id}', follow_redirects=True)
        assert b'Vous ne suivez plus cet utilisateur' in response.data
        
        print("Follow/Unfollow test passed!")

def test_profile_photo_upload():
    with app.test_client() as client:
        # Login as Alice
        client.post('/login', data={
            'email': 'alice@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Get Alice's user ID
        alice = User.query.filter_by(username='alice').first()
        
        # Simulate photo upload
        with open('static/uploads/default_profile.png', 'rb') as photo:
            response = client.post(f'/profile/{alice.id}', data={
                'profile_photo': (photo, 'test_photo.png')
            }, follow_redirects=True)
        
        assert b'Photo de profil mise à jour' in response.data
        print("Profile photo upload test passed!")

def run_tests():
    with app.app_context():
        create_test_users()
        test_user_search()
        test_follow_unfollow()
        test_profile_photo_upload()
        print("All tests completed successfully!")

if __name__ == '__main__':
    run_tests()
