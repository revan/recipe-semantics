#!/bin/python3
import requests
import json
import time
import sys

from secrets import BIGOVEN_API_KEY

recipes = []

def save():
    with open('bigoven.json', 'w', encoding='utf8') as json_file:
        data = json.dumps(recipes, ensure_ascii=False, indent=4)
        json_file.write(data)
    print('Saved. Now have %d recipes.' % len(recipes))

search_url = 'http://api.bigoven.com/recipes'
recipe_url = 'http://api.bigoven.com/recipe/'
headers = {'Accept': 'application/json'}

api_key = BIGOVEN_API_KEY
search_params = {
    'api_key': api_key,
    'pg': 1,
    'rpp': 200
}
recipe_params = {
    'api_key': api_key
}

while search_params['pg'] < 1000:
    try:
        print('Searching.')
        search = requests.get(search_url, params=search_params, headers=headers)

        if search.status_code == 400 or search.status_code == 409 or search.status_code == 500:
            print('Actual error. Waiting a minute.')
            time.sleep(60)
            continue
        search = search.json()

        for recipe in search['Results']:
            if 'RecipeID' in recipe:
                recipe_id = str(recipe['RecipeID'])
                print('Getting ' + recipe_id)

                fetch = requests.get(recipe_url + recipe_id, params=recipe_params, headers=headers)

                if fetch.status_code == 400 or fetch.status_code == 409 or fetch.status_code == 500:
                    print('Actual error on recipe. Waiting a minute.')
                    time.sleep(60)
                    continue

                fetch = fetch.json()

                if 'Instructions' in fetch:

                    to_add = {
                        'title': fetch['Title'],
                        'category': fetch['Category'],
                        'ingredients': [{'name': ing['Name'], 'quantity': ing['MetricDisplayQuantity'], 'unit': ing['MetricUnit']} for ing in fetch['Ingredients'] if ing['MetricDisplayQuantity'] or ing['MetricUnit']],
                        'instructions': [line for line in fetch['Instructions'].split('\r\n') if line != '']
                    }

                    recipes.append(to_add)
                    save()
                else:
                    print('No instructions!')

                time.sleep(40)

        time.sleep(10)
        search_params['pg'] += 1

    except Exception:
        print('Too fast? Waiting a minute.')
        print(sys.exc_info()[0])
        time.sleep(61)
