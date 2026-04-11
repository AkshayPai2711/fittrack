import random

def generate_dish(foods, meal_type):

    # Simple templates
    breakfast_templates = [
        "{} with {} and {}",
        "{} bowl with {} and {}",
        "{} smoothie with {} and {}"
    ]

    lunch_templates = [
        "{} with {} and {}",
        "{} salad with {} and {}",
        "{} stir-fry with {} and {}"
    ]

    dinner_templates = [
        "{} with roasted {} and {}",
        "{} bowl with {} and {}",
        "{} plate with {} and {}"
    ]

    snack_templates = [
        "{} with {}",
        "{} snack with {}",
        "{} and {}"
    ]

    if meal_type == "Breakfast":
        template = random.choice(breakfast_templates)

    elif meal_type == "Lunch":
        template = random.choice(lunch_templates)

    elif meal_type == "Dinner":
        template = random.choice(dinner_templates)

    else:
        template = random.choice(snack_templates)

    try:
        return template.format(*foods)
    except:
        return " + ".join(foods)