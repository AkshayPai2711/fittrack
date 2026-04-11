import numpy as np
import random
from sklearn.cluster import KMeans
from .foods import foods
import random

import numpy as np
import random
from sklearn.cluster import KMeans
from .foods import foods
from .dish_generator import generate_dish


def recommend_meals(calories_per_meal, preference, meals, goal):

    # Filter foods by diet preference
    filtered = []

    for f in foods:

        if preference == "mixed":
            filtered.append(f)

        elif preference == "veg" and f["type"] in ["veg","vegan"]:
            filtered.append(f)

        elif preference == "vegan" and f["type"] == "vegan":
            filtered.append(f)

    # Nutrition vectors
    X = np.array([[f["cal"],f["protein"],f["carbs"],f["fat"]] for f in filtered])

    kmeans = KMeans(n_clusters=4, random_state=0).fit(X)

    labels = kmeans.labels_

    clusters = {}

    for i,label in enumerate(labels):

        clusters.setdefault(label, []).append(filtered[i])

    # Goal based sorting
    if goal == "cut":
        # prefer high protein foods
        ranked = sorted(filtered, key=lambda x: x["protein"], reverse=True)

    elif goal == "bulk":
        # prefer carb dense foods
        ranked = sorted(filtered, key=lambda x: x["carbs"], reverse=True)

    else:
        # balanced
        ranked = sorted(filtered, key=lambda x: x["protein"] + x["carbs"])

    meal_types = ["Breakfast","Lunch","Dinner","Snack 1","Snack 2"]

    meal_plan = []

    used = set()

    for i in range(meals):

        meal_foods = []

        for food in ranked:

            if food["name"] not in used:
                meal_foods.append(food["name"])
                used.add(food["name"])

            if len(meal_foods) == 3:
                break

        if len(meal_foods) < 3:
            meal_foods += random.sample(
                [f["name"] for f in filtered],
                3 - len(meal_foods)
            )

        dish = generate_dish(meal_foods, meal_types[i])

        meal_plan.append({
            "name": meal_types[i],
            "foods": meal_foods,
            "dish": dish
        })

    return meal_plan