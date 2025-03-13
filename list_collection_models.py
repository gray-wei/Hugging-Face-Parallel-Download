#!/usr/bin/env python3
# List all models in the collection, but not download them

import os
import requests
from bs4 import BeautifulSoup
import json
import argparse
from urllib.parse import urlparse

def get_collection_models(collection_url):
    """Get all model/dataset information from the collection"""
    print(f"Getting collection information: {collection_url}")
    
    # Check if the URL is valid
    parsed_url = urlparse(collection_url)
    if not parsed_url.netloc or not parsed_url.path:
        raise ValueError("Invalid collection URL")
    
    # Ensure the correct user agent to avoid being rejected
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(collection_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to access the collection page, status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the script tag containing model information
    scripts = soup.find_all('script')
    collection_data = None
    
    for script in scripts:
        if script.string and 'window.initialData=' in script.string:
            data_str = script.string.split('window.initialData=')[1].split(';</script>')[0]
            try:
                data = json.loads(data_str)
                if 'collection' in data and 'models' in data['collection']:
                    collection_data = data['collection']
                    break
            except json.JSONDecodeError:
                continue
    
    if not collection_data:
        # Try another method: scrape model cards
        models = []
        model_cards = soup.select('article a[href^="/"]') or soup.select('a[href^="/"]')
        for card in model_cards:
            href = card.get('href', '')
            if href.startswith('/') and href.count('/') >= 1 and not href.startswith('/?'):
                model_id = href.lstrip('/')
                if model_id and '/' in model_id:  # Ensure the format is username/modelname
                    if not any(keyword in href for keyword in ['/discussions', '/settings', '/community']):
                        models.append(model_id)
        return list(set(models))  # Remove duplicates
    
    models = []
    for model in collection_data.get('models', []):
        if 'id' in model:
            models.append(model['id'])
    
    return models

def main():
    parser = argparse.ArgumentParser(description='List all models in the collection')
    parser.add_argument('--collection_url', type=str, 
                        default='https://huggingface.co/collections/facebook/sparsh-67167ce57566196a4526c328',
                        help='Hugging Face collection URL')
    parser.add_argument('--output_file', type=str, default=None,
                        help='Save the model list to a file (optional)')
    
    args = parser.parse_args()
    
    # Get the models from the collection
    model_ids = get_collection_models(args.collection_url)
    print(f"Found {len(model_ids)} models/datasets in the collection")
    
    # Print the model list
    for i, model_id in enumerate(model_ids, 1):
        print(f"{i}. {model_id}")
    
    # If the output file is specified, save the list to a file
    if args.output_file:
        with open(args.output_file, 'w') as f:
            for model_id in model_ids:
                f.write(f"{model_id}\n")
        print(f"Model list has been saved to {args.output_file}")

if __name__ == "__main__":
    main() 