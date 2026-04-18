

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
import requests
import random
from django.http import JsonResponse
from django.conf import settings

import random
from django.shortcuts import render
from .ml.calorie_model import predict_calories

from django.shortcuts import render
from .ml.calorie_model import predict_calories
from .ml.meal_recommender import recommend_meals
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import JournalEntry
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from openai import OpenAI

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Profile, Post
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


from .models import Profile, Post
from django.contrib.auth.decorators import login_required
from .models import FriendRequest, Message
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from .models import FriendRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse

from .models import FriendRequest, Message

from .models import ContactMessage

from .models import ContactMessage

def home(request):

    if request.method == "POST":

        print("POST RECEIVED ✅")

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        print(name, email, message)

        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        return render(request, "users/home.html", {"success": True})

    return render(request, "users/home.html")
@login_required
def send_request(request, user_id):
    user = User.objects.get(id=user_id)

    if user != request.user:
        FriendRequest.objects.get_or_create(
            sender=request.user,
            receiver=user,
            accepted=False
        )

    return redirect("discover")


# 🔹 ACCEPT REQUEST
@login_required
def accept_request(request, req_id):
    req = FriendRequest.objects.get(id=req_id)

    if req.receiver == request.user:
        req.accepted = True
        req.save()

    return redirect("friends")


# 🔹 FRIEND LIST (ONLY ACCEPTED)
@login_required
def friends_list(request):

    friends = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    )

    return render(request, "users/friends.html", {"friends": friends})


# 🔹 DISCOVER USERS (WITH STATUS)
@login_required
def discover_users(request):

    users = User.objects.exclude(id=request.user.id)
    data = []

    for u in users:

        status = "none"
        req_id = None

        # sent request
        if FriendRequest.objects.filter(sender=request.user, receiver=u, accepted=False).exists():
            status = "sent"

        # received request
        elif FriendRequest.objects.filter(sender=u, receiver=request.user, accepted=False).exists():
            req = FriendRequest.objects.get(sender=u, receiver=request.user, accepted=False)
            status = "received"
            req_id = req.id

        # already friends
        elif FriendRequest.objects.filter(
            accepted=True
        ).filter(
            (models.Q(sender=request.user, receiver=u)) |
            (models.Q(sender=u, receiver=request.user))
        ).exists():
            status = "friends"

        mutual = len(get_mutual_friends(request.user, u))

        data.append({
            "user": u,
            "mutual": mutual,
            "status": status,
            "req_id": req_id
        })

    data = sorted(data, key=lambda x: x["mutual"], reverse=True)

    return render(request, "users/discover.html", {"users": data})


# 🔹 MUTUAL FRIENDS (FIXED)
def get_mutual_friends(user1, user2):

    user1_friends = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        models.Q(sender=user1) | models.Q(receiver=user1)
    )

    user2_friends = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        models.Q(sender=user2) | models.Q(receiver=user2)
    )

    set1 = set([f.sender if f.sender != user1 else f.receiver for f in user1_friends])
    set2 = set([f.sender if f.sender != user2 else f.receiver for f in user2_friends])

    return set1.intersection(set2)


# 🔹 CHAT SYSTEM (FIXED)
@login_required
def chat(request, user_id):

    other_user = User.objects.get(id=user_id)

    # allow only if friends
    is_friend = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        (models.Q(sender=request.user, receiver=other_user)) |
        (models.Q(sender=other_user, receiver=request.user))
    ).exists()

    if not is_friend:
        return redirect("discover")

    # 🔥 GET messages (AJAX)
    if request.GET.get("ajax"):

        messages = Message.objects.filter(
            sender__in=[request.user, other_user],
            receiver__in=[request.user, other_user]
        ).order_by("timestamp")

        data = []

        for m in messages:
            data.append({
                "text": m.text,
                "image": m.image.url if m.image else None,
                "me": m.sender == request.user
            })

        return JsonResponse({"messages": data})

    # 🔥 SEND message
    if request.method == "POST":

        Message.objects.create(
            sender=request.user,
            receiver=other_user,
            text=request.POST.get("text"),
            image=request.FILES.get("image")
        )

        return JsonResponse({"status": "ok"})

    return render(request, "users/chat.html", {"other_user": other_user})
@login_required
def chat_inbox(request):

    friends = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user)
    )

    users = []

    for f in friends:
        other = f.receiver if f.sender == request.user else f.sender
        users.append(other)

    return render(request, "users/chat_inbox.html", {"users": users})
@login_required
def user_profile(request, user_id):

    profile_user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=profile_user)
    posts = Post.objects.filter(user=profile_user).order_by("-id")

    # already friends?
    is_friend = FriendRequest.objects.filter(
        accepted=True
    ).filter(
        (models.Q(sender=request.user, receiver=profile_user)) |
        (models.Q(sender=profile_user, receiver=request.user))
    ).exists()

    # request sent by current user
    sent = FriendRequest.objects.filter(
        sender=request.user,
        receiver=profile_user,
        accepted=False
    ).exists()

    # request received from viewed user
    received_request = FriendRequest.objects.filter(
        sender=profile_user,
        receiver=request.user,
        accepted=False
    ).first()

    return render(request, "users/user_profile.html", {
        "profile_user": profile_user,
        "profile": profile,
        "posts": posts,
        "is_friend": is_friend,
        "sent": sent,
        "received": bool(received_request),
        "request_id": received_request.id if received_request else None,
    })
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    posts = Post.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "users/profile.html", {
        "profile": profile,
        "posts": posts
    })


@login_required
def edit_profile(request):

    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio")

        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES.get("profile_pic")

        profile.save()
        return redirect("profile")

    return render(request, "users/edit_profile.html", {"profile": profile})


@login_required
def create_post(request):

    if request.method == "POST":

        image = request.FILES.get("image")
        video = request.FILES.get("video")
        caption = request.POST.get("caption")

        Post.objects.create(
            user=request.user,
            image=image,
            video=video,
            caption=caption
        )

        return redirect("profile")

    return render(request, "users/create_post.html")

@csrf_exempt



def chatbot_api(request):

    if request.method == "POST":

        data = json.loads(request.body)
        user_msg = data.get("message", "").lower()

        reply = ""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "FitTrack AI"
                },
                json={
                    "model": "openchat/openchat-3.5",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a smart fitness coach. Give short, helpful, varied answers. Do not repeat same responses."
                        },
                        {
                            "role": "user",
                            "content": user_msg
                        }
                    ]
                }
            )

            result = response.json()

            if "choices" in result:
                reply = result["choices"][0]["message"]["content"]
            else:
                raise Exception("No AI response")

        except Exception:

            # 🔥 SMART FALLBACK SYSTEM (VARIED RESPONSES)

            if "chest" in user_msg:
                options = [
                    "🏋️ Chest Workout:\n- Push-ups (3x15)\n- Bench Press (4x10)\n- Chest Fly (3x12)",
                    "🔥 Chest Routine:\n- Incline Press (4x10)\n- Dips (3x12)\n- Cable Fly (3x15)",
                    "💪 Chest Builder:\n- Dumbbell Press (4x10)\n- Decline Push-ups (3x15)\n- Pec Deck (3x12)"
                ]
                reply = random.choice(options)

            elif "biceps" in user_msg:
                options = [
                    "💪 Biceps:\n- Barbell Curl (4x10)\n- Hammer Curl (3x12)",
                    "🔥 Arms Day:\n- Concentration Curl (3x10)\n- Preacher Curl (3x12)",
                    "💥 Biceps Blast:\n- EZ Bar Curl (4x10)\n- Cable Curl (3x15)"
                ]
                reply = random.choice(options)

            elif "legs" in user_msg:
                options = [
                    "🦵 Leg Day:\n- Squats (4x10)\n- Lunges (3x12)\n- Leg Press (3x12)",
                    "🔥 Lower Body:\n- Deadlifts (4x8)\n- Hamstring Curl (3x12)",
                    "💥 Legs Workout:\n- Bulgarian Split Squats (3x10)\n- Calf Raises (4x15)"
                ]
                reply = random.choice(options)

            elif "abs" in user_msg or "core" in user_msg:
                options = [
                    "🔥 Abs:\n- Crunches (3x20)\n- Plank (3x45 sec)",
                    "💪 Core:\n- Leg Raises (3x15)\n- Russian Twists (3x20)",
                    "⚡ Abs Workout:\n- Mountain Climbers (3x30 sec)\n- Bicycle Crunch (3x20)"
                ]
                reply = random.choice(options)

            elif "shoulder" in user_msg:
                options = [
                    "🏋️ Shoulders:\n- Overhead Press (4x10)\n- Lateral Raises (3x12)",
                    "🔥 Shoulder Day:\n- Front Raise (3x12)\n- Shrugs (3x15)",
                    "💥 Delts:\n- Arnold Press (4x10)\n- Rear Delt Fly (3x12)"
                ]
                reply = random.choice(options)

            elif "cardio" in user_msg:
                options = [
                    "🏃 Cardio:\n- Running 20 mins\n- Jump rope 10 mins",
                    "🔥 Fat Burn:\n- HIIT 15 mins\n- Cycling 20 mins",
                    "💥 Cardio Blast:\n- Burpees (3x15)\n- Sprint intervals"
                ]
                reply = random.choice(options)

            elif "diet" in user_msg or "food" in user_msg:
                options = [
                    "🥗 Diet:\n- High protein\n- Avoid junk\n- Drink water",
                    "🍗 Nutrition:\n- Eggs, chicken, dal\n- Fruits daily",
                    "🥦 Healthy Eating:\n- Balanced carbs + protein\n- Fiber rich foods"
                ]
                reply = random.choice(options)

            elif "lose weight" in user_msg:
                options = [
                    "🔥 Weight Loss:\n- Calorie deficit\n- Cardio daily",
                    "⚡ Fat Loss:\n- HIIT workouts\n- Clean diet",
                    "🏃 Burn Fat:\n- Walk 10k steps\n- Avoid sugar"
                ]
                reply = random.choice(options)

            elif "gain muscle" in user_msg or "bulk" in user_msg:
                options = [
                    "💪 Muscle Gain:\n- High protein\n- Lift heavy",
                    "🔥 Bulking:\n- Calorie surplus\n- Progressive overload",
                    "🏋️ Gain Size:\n- Strength training\n- Sleep 8 hours"
                ]
                reply = random.choice(options)

            else:
                reply = random.choice([
                    "🤖 Ask me about workouts, diet, or fitness 💪",
                    "🔥 Tell me your goal (fat loss / muscle gain)",
                    "💬 I can help with gym plans and nutrition!"
                ])

        return JsonResponse({"response": reply})
def chatapp(request):
    return render(request, "users/chatapp.html")
@login_required
def digibook(request):
    return render(request, "users/digibook.html")


@login_required
def save_entry(request):
    if request.method == "POST":
        data = json.loads(request.body)

        entry, _ = JournalEntry.objects.get_or_create(
            user=request.user,
            date=data["date"]
        )

        entry.note = data.get("note", "")
        entry.checked = data.get("checked", False)
        entry.save()

        return JsonResponse({"status": "saved"})


@login_required
def get_entries(request):
    entries = JournalEntry.objects.filter(user=request.user)

    data = {}
    for e in entries:
        data[e.date] = {
            "note": e.note,
            "checked": e.checked
        }

    return JsonResponse(data)

#

import random
from django.shortcuts import render

def diet_planner(request):

    context = {}

    if request.method == "POST":

        age = request.POST.get("age")
        gender = request.POST.get("gender")
        weight = request.POST.get("weight")
        height = request.POST.get("height")
        activity = request.POST.get("activity")
        goal = request.POST.get("goal")
        meals = request.POST.get("meals")
        preference = request.POST.get("preference")

        if not age or not weight or not height:
            context["error"] = "Please fill all required fields."
            return render(request, "users/diet_planner.html", context)

        age = int(age)
        weight = float(weight)
        height = float(height)
        activity = float(activity)
        meals = int(meals)

        # 🔥 Calories (BMR)
        bmr = (10 * weight + 6.25 * height - 5 * age + 5) if gender == "male" \
              else (10 * weight + 6.25 * height - 5 * age - 161)

        calories = int(bmr * activity)

        if goal == "cut":
            calories -= 400
        elif goal == "bulk":
            calories += 400

        meal_calories = round(calories / meals)

        # 🔥 MACROS
        protein = round(weight * (2 if goal == "bulk" else 1.6))
        fats = round(calories * 0.25 / 9)
        carbs = round((calories - (protein*4 + fats*9)) / 4)

        # 🔥 HUGE FOOD DATABASE

        veg = {
            "breakfast": [
                "Oats + milk + nuts", "Poha + peanuts", "Upma", "Smoothie bowl",
                "Sprouts chaat", "Paneer sandwich", "Idli + sambar"
            ],
            "main": [
                "Dal + rice + salad", "Paneer bhurji + roti", "Chole + roti",
                "Veg khichdi", "Tofu stir fry + rice", "Rajma + rice",
                "Vegetable pulao"
            ],
            "snack": [
                "Fruit bowl", "Roasted peanuts", "Yogurt + honey",
                "Boiled corn", "Protein shake", "Dry fruits"
            ]
        }

        nonveg = {
            "breakfast": [
                "Boiled eggs + toast", "Omelette + bread",
                "Scrambled eggs", "Egg sandwich"
            ],
            "main": [
                "Chicken breast + rice", "Fish curry + rice",
                "Egg curry + roti", "Grilled chicken + veggies",
                "Chicken biryani (controlled)", "Tandoori chicken"
            ],
            "snack": [
                "Boiled eggs", "Chicken salad", "Tuna sandwich",
                "Protein shake", "Greek yogurt"
            ]
        }

        # 🔥 SELECT DATA
        if preference == "veg":
            data = veg
        elif preference == "nonveg":
            data = nonveg
        else:
            data = {
                "breakfast": veg["breakfast"] + nonveg["breakfast"],
                "main": veg["main"] + nonveg["main"],
                "snack": veg["snack"] + nonveg["snack"]
            }

        # 🔥 SHUFFLE
        for key in data:
            random.shuffle(data[key])

        meal_plan = []
        used = set()

        for i in range(meals):

            if i == 0:
                meal_type = "Breakfast"
                pool = data["breakfast"]

            elif i == 1:
                meal_type = "Lunch"
                pool = data["main"]

            elif i == meals - 1:
                meal_type = "Dinner"
                pool = data["main"]

            else:
                meal_type = f"Snack {i}"
                pool = data["snack"]

            available = [f for f in pool if f not in used]
            food = random.choice(available if available else pool)

            used.add(food)

            meal_plan.append({
                "type": meal_type,
                "name": food,
                "calories": meal_calories
            })

        # 🔥 EXTRA FEATURES

        hydration = f"Drink {round(weight * 0.04, 1)}L water daily 💧"

        tips = random.sample([
            "Eat protein in every meal 🍗",
            "Avoid late-night eating 🌙",
            "Walk 8–10k steps daily 🚶",
            "Sleep at least 7–8 hours 😴",
            "Limit sugar intake 🍩",
            "Eat whole foods 🥗",
            "Stay consistent with diet 🔥"
        ], 4)

        avoid = random.sample([
            "Sugary drinks 🥤",
            "Deep fried food 🍟",
            "Processed snacks 🍪",
            "Excess alcohol 🍺",
            "Fast food 🍔",
            "Refined sugar 🍰"
        ], 4)

        # 🔥 FINAL CONTEXT
        context = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
            "meals": meal_plan,
            "tips": tips,
            "avoid": avoid,
            "hydration": hydration
        }

    return render(request, "users/diet_planner.html", context)
def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password == confirm:

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return redirect("login")

    return render(request, "users/signup.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        remember = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            if not remember:
                request.session.set_expiry(0)

            return redirect("home")

    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")





def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(username=username, email=email)

            otp = str(random.randint(100000, 999999))

            request.session["reset_otp"] = otp
            request.session["reset_user"] = user.username

            return render(request, "users/show_otp.html", {
                "otp": otp
            })

        except User.DoesNotExist:
            return render(request, "users/forgot_password.html", {
                "error": "User not found"
            })

    return render(request, "users/forgot_password.html")


def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("reset_otp")

        if entered_otp == saved_otp:
            return redirect("reset_password")

        else:
            return render(request, "users/show_otp.html", {
                "error": "Invalid OTP",
                "otp": saved_otp
            })

    return redirect("forgot_password")


def reset_password(request):

    username = request.session.get("reset_user")

    if not username:
        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password == confirm:

            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            request.session.pop("reset_otp", None)
            request.session.pop("reset_user", None)

            return redirect("login")

        else:
            return render(request, "users/reset_password.html", {
                "error": "Passwords do not match"
            })

    return render(request, "users/reset_password.html")

def nutrition(request):
    return render(request, "users/nutrition.html")


def food_ai(request):
    return render(request,"users/food_ai.html")
def exercise_hub(request):
    return render(request, "users/exercise_hub.html")
def ai_assistant(request):
    return render(request, "users/ai_assistant.html")

def exercise_videos(request):
    return render(request, "users/exercise_videos.html")
