#!/usr/bin/env python3
"""
Add GitHub repository topics using GitHub API

Usage:
    python add_github_topics.py
    
Requirements:
    pip install requests
    
Environment:
    GITHUB_TOKEN - Personal access token with 'repo' scope
"""

import os
import requests
import sys

# Configuration
OWNER = "VadimToptunov"
REPO = "mobile_test_recorder"

TOPICS = [
    "mobile-testing",
    "test-automation",
    "appium",
    "pytest",
    "bdd",
    "self-healing-tests",
    "android-testing",
    "ios-testing",
    "kotlin",
    "swift",
    "python",
    "machine-learning",
    "page-object-model",
    "ci-cd",
    "github-actions",
    "gitlab-ci",
    "test-framework",
    "quality-assurance",
    "mobile-development",
    "fintech",
]


def add_topics(owner: str, repo: str, topics: list, token: str):
    """Add topics to GitHub repository"""
    
    url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    data = {"names": topics}
    
    print(f"Adding {len(topics)} topics to {owner}/{repo}...")
    print(f"Topics: {', '.join(topics)}")
    
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Topics added successfully!")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    # Get token from environment
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("\nGet your token here: https://github.com/settings/tokens")
        print("Required scope: 'repo'")
        print("\nUsage:")
        print("  export GITHUB_TOKEN=your_token_here")
        print("  python add_github_topics.py")
        sys.exit(1)
    
    success = add_topics(OWNER, REPO, TOPICS, token)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

