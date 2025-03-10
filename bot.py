import os
import time
import random
from datetime import datetime, timedelta
from typing import Set, Optional
import pytz
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired,
    ClientError, ClientConnectionError, BadPassword
)

class InstagramBot:
    """Instagram automation client for story viewing, feed engagement, and follow/unfollow."""
    
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [3, 7]  # Human-like interaction delays
        self._init_trackers()
        
        # Load credentials and target account from environment variables
        self.credentials = {
            'username': os.getenv("INSTAGRAM_USERNAME"),
            'password': os.getenv("INSTAGRAM_PASSWORD")
        }
        self.target_account = os.getenv("TARGET_ACCOUNT")
        
        if not self.credentials['username'] or not self.credentials['password']:
            raise ValueError("Instagram credentials not found in environment variables.")
        if not self.target_account:
            raise ValueError("Target account not found in environment variables.")
        
        self.limits = {
            'likes': 100,
            'comments': 40,
            'story_views': 200,
            'follows': 10  # Daily follow/unfollow limit
        }
        self.timezone = pytz.timezone('Asia/Kolkata')
        
    def _init_trackers(self) -> None:
        """Initialize interaction trackers to prevent duplicates"""
        self.viewed_stories: Set[str] = set()
        self.liked_posts: Set[str] = set()
        self.commented_posts: Set[str] = set()
        self.followed_accounts: Set[str] = set()
        
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
    def follow_target_account(self) -> Optional[bool]:
        """Follow the target account if not already followed"""
        if self.target_account in self.followed_accounts:
            print(f"Already following {self.target_account}")
            return False
        
        try:
            user_id = self.cl.user_id_from_username(self.target_account)
            self.cl.user_follow(user_id)
            self.followed_accounts.add(self.target_account)
            print(f"Followed {self.target_account}")
            return True
        except Exception as e:
            print(f"Error following {self.target_account}: {e}")
            return None
    
    @safe_action
    def unfollow_target_account(self) -> Optional[bool]:
        """Unfollow the target account if followed"""
        if self.target_account not in self.followed_accounts:
            print(f"Not following {self.target_account}")
            return False
        
        try:
            user_id = self.cl.user_id_from_username(self.target_account)
            self.cl.user_unfollow(user_id)
            self.followed_accounts.remove(self.target_account)
            print(f"Unfollowed {self.target_account}")
            return True
        except Exception as e:
            print(f"Error unfollowing {self.target_account}: {e}")
            return None
    
    def execute_cycle(self) -> None:
        """Execute complete engagement cycle"""
        print("\n--- Starting engagement cycle ---")
        print(f"Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        self.handle_stories()
        self.engage_feed()
        
        # Follow/unfollow logic
        if self.follow_target_account():
            time.sleep(random.randint(600, 1200))  # Wait 10-20 minutes before unfollowing
            self.unfollow_target_account()
        
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