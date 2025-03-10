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
    """Instagram automation client for story viewing and feed engagement."""
    
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [3, 7]  # Human-like interaction delays
        self._init_trackers()
        
        # Load credentials from environment variables
        self.credentials = {
            'username': os.getenv("INSTAGRAM_USERNAME"),
            'password': os.getenv("INSTAGRAM_PASSWORD")
        }
        if not self.credentials['username'] or not self.credentials['password']:
            raise ValueError("Instagram credentials not found in environment variables.")
        
        self.limits = {
            'likes': 100,
            'comments': 40,
            'story_views': 200
        }
        self.timezone = pytz.timezone('Asia/Kolkata')
        
    def _init_trackers(self) -> None:
        """Initialize interaction trackers to prevent duplicates"""
        self.viewed_stories: Set[str] = set()
        self.liked_posts: Set[str] = set()
        self.commented_posts: Set[str] = set()
        
    @staticmethod
    def safe_action(func):
        """Decorator for error handling and rate limiting"""
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
                time.sleep(random.uniform(1.2, 3.8))  # Simulate human-like delays
                return result
            except (ClientError, ClientConnectionError) as e:
                print(f"Network error: {e}")
                self._handle_retry()
            except ChallengeRequired:
                print("Manual verification required. Please check your Instagram app.")
                self._handle_challenge()
            except LoginRequired:
                print("Re-authenticating...")
                self.authenticate()
            except BadPassword:
                print("Invalid credentials or suspicious login detected. Exiting.")
                exit(1)
            except Exception as e:
                print(f"Unexpected error: {e}")
                self._handle_retry()
            return None
        return wrapper
    
    def _handle_retry(self, delay: Optional[int] = None) -> None:
        """Handle retry logic for temporary errors"""
        if delay is None:
            delay = random.randint(600, 1200)  # Default delay: 10-20 minutes
        print(f"Temporary issue detected. Retrying in {delay // 60} minutes.")
        time.sleep(delay)
    
    def _handle_challenge(self) -> None:
        """Handle Instagram's challenge requirement (e.g., manual verification)"""
        print("Please complete the challenge in the Instagram app.")
        time.sleep(300)  # Wait 5 minutes for the user to complete the challenge
        self.authenticate()
    
    def authenticate(self) -> None:
        """Handle secure authentication with credentials"""
        try:
            print("Initiating secure authentication...")
            self.cl.login(**self.credentials)
            print("Authentication successful.")
        except ChallengeRequired:
            print("Account verification required. Please check your Instagram app.")
            self._handle_challenge()
        except BadPassword:
            print("Invalid credentials or suspicious login detected. Exiting.")
            exit(1)
        except Exception as e:
            print(f"Authentication failed: {e}")
            self._handle_retry()
            
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
                    
                    if random.random() < 0.7:  # 70% chance to like the story
                        self.cl.story_like(story.id)
                    
                    story_count += 1
                    print(f"Processed story by {user.username}")
                    
                    if not self._within_limit('story_views', story_count):
                        break
                        
            except Exception as e:
                print(f"Error processing stories for {user.username}: {e}")
                self._handle_retry(delay=300)  # Retry after 5 minutes
                
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
                and random.random() < 0.3):  # 30% chance to comment
                
                comments = ["Great content!", "Well done!", "Awesome post!"]
                self.cl.media_comment(post.id, random.choice(comments))
                self.commented_posts.add(post.id)
                comment_count += 1
                print(f"Commented on post by {post.user.username}")
                
    def execute_cycle(self) -> None:
        """Execute complete engagement cycle"""
        print("\n--- Starting engagement cycle ---")
        print(f"Current time: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}")
        self.handle_stories()
        self.engage_feed()
        print("--- Cycle completed successfully ---\n")
        
    def run(self) -> None:
        """Main execution loop"""
        self.authenticate()
        
        while True:
            try:
                self.execute_cycle()
            except Exception as e:
                print(f"Error during engagement cycle: {e}")
                self._handle_retry()
            
            delay = 1800  # 30 minutes
            next_run = datetime.now(self.timezone) + timedelta(seconds=delay)
            print(f"Next cycle at {next_run.strftime('%H:%M:%S')}")
            time.sleep(delay)

if __name__ == "__main__":
    bot = InstagramBot()
    bot.run()