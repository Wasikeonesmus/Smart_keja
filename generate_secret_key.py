#!/usr/bin/env python
"""
Generate a secure Django secret key for deployment
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*60)
    print("Django Secret Key (copy this for your deployment):")
    print("="*60)
    print(secret_key)
    print("="*60 + "\n")
    print("Add this to your environment variables as SECRET_KEY")

