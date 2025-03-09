import time
import random
from datetime import datetime, timedelta
from typing import Set, Dict
import pytz
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired,
    ClientError, ClientConnectionError, BadPassword
)

class InstagramBot:
    """Instagram automation client for story viewing, feed engagement, and messaging new followers"""
    
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [3, 7]  # Human-like interaction delays
        self._init_trackers()
        
        # Configuration
        self.credentials = {
            'username': "xkira2026",
            'password': "9562449137"
        }
        self.limits = {
            'likes': 100,
            'comments': 40,
            'dms': 20,
            'story_views': 200
        }
        self.timezone = pytz.timezone('Asia/Kolkata')
        self.messaged_users_file = "messaged_users.txt"
        self.messaged_users = self._load_messaged_users()
        
    def _init_trackers(self) -> None:
        """Initialize interaction trackers to prevent duplicates"""
        self.viewed_stories: Set[str] = set()
        self.liked_posts: Set[str] = set()
        self.commented_posts: Set[str] = set()
        
    def _load_messaged_users(self) -> Set[int]:
        """Load messaged users from a file to avoid duplicates"""
        try:
            with open(self.messaged_users_file, "r") as file:
                return {int(line.strip()) for line in file if line.strip()}
        except FileNotFoundError:
            return set()
        
    def _save_messaged_user(self, user_id: int) -> None:
        """Save a messaged user to the file"""
        with open(self.messaged_users_file, "a") as file:
            file.write(f"{user_id}\n")
        
    @staticmethod
    def safe_action(func):
        """Decorator for error handling and rate limiting"""
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                time.sleep(random.uniform(1.2, 3.8))
                return result
            except (ClientError, ClientConnectionError) as e:
                print(f"Network error: {e}")
                self._handle_retry()
            except ChallengeRequired:
                print("Manual verification required")
                exit(1)
            except LoginRequired:
                print("Re-authenticating...")
                self.authenticate()
            return None
        return wrapper
    
    def _handle_retry(self) -> None:
        """Handle retry logic for temporary errors"""
        delay = random.randint(600, 1200)
        print(f"Temporary issue detected. Retrying in {delay//60} minutes")
        time.sleep(delay)
    
    def authenticate(self) -> None:
        """Handle secure authentication with credentials"""
        try:
            print("Initiating secure authentication...")
            self.cl.login(**self.credentials)
            print("Authentication successful")
        except ChallengeRequired:
            print("Account verification required - check your Instagram app")
            exit(1)
        except BadPassword:
            print("Invalid credentials or suspicious login detected")
            exit(1)
            
    def _within_limit(self, action: str, count: int) -> bool:
        """Check if action count is within daily limits"""
        return count < self.limits.get(action, 0)
    
    @safe_action
    def handle_stories(self) -> None:
        """Process stories from followed accounts with duplicate prevention"""
        following = self.cl.user_following(self.cl.user_id)
        story_count = 0
        
        for user in following.values():
            if story_count >= self.limits['story_views']:
                break
                
            try:
                stories = self.cl.user_stories(user.pk)
                for story in stories:
                    if story.id in self.viewed_stories:
                        continue
                        
                    self.cl.story_seen([story.pk])
                    self.viewed_stories.add(story.id)
                    
                    if random.random() < 0.7:
                        self.cl.story_like(story.id)
                    
                    story_count += 1
                    print(f"Processed story by {user.username}")
                    
                    if not self._within_limit('story_views', story_count):
                        break
                        
            except Exception as e:
                print(f"Error processing stories for {user.username}: {e}")
                
    @safe_action
    def engage_feed(self) -> None:
        """Interact with feed posts while avoiding duplicates"""
        feed = self.cl.user_medias(self.cl.user_id, amount=self.limits['likes'])
        like_count = 0
        comment_count = 0
        
        for post in feed:
            if post.id in self.liked_posts:
                continue
                
            if self._within_limit('likes', like_count):
                self.cl.media_like(post.id)
                self.liked_posts.add(post.id)
                like_count += 1
                print(f"Liked post by {post.user.username}")
                
            if (self._within_limit('comments', comment_count) 
                and post.id not in self.commented_posts
                and random.random() < 0.3):
                
                comments = ["Great content!", "Well done!", "Awesome post!"]
                self.cl.media_comment(post.id, random.choice(comments))
                self.commented_posts.add(post.id)
                comment_count += 1
                print(f"Commented on post by {post.user.username}")
                
    @safe_action
    def dm_new_followers(self) -> None:
        """Send welcome messages to new followers, avoiding duplicates"""
        current_followers = self.cl.user_followers(self.cl.user_id)
        dm_count = 0
        
        for user_id, user in current_followers.items():
            if dm_count >= self.limits['dms'] or user_id in self.messaged_users:
                continue
                
            message = f"Hi {user.username}, thanks for connecting!"
            self.cl.direct_send(message, user_ids=[user_id])
            self.messaged_users.add(user_id)
            self._save_messaged_user(user_id)
            dm_count += 1
            print(f"Sent welcome message to {user.username}")
            
    def execute_cycle(self) -> None:
        """Execute complete engagement cycle"""
        print("\n--- Starting engagement cycle ---")
        print(f"Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        self.handle_stories()
        self.engage_feed()
        self.dm_new_followers()
        print("--- Cycle completed successfully ---\n")
        
    def run(self) -> None:
        """Main execution loop"""
        self.authenticate()
        
        while True:
            self.execute_cycle()
            delay = 1800  # 30 minutes
            next_run = datetime.now(self.timezone) + timedelta(seconds=delay)
            print(f"Next cycle at {next_run.strftime('%H:%M:%S')}")
            time.sleep(delay)

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()