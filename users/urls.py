from django.urls import path
from .views import login_view, signup_view, logout_view, home,forgot_password,verify_otp,reset_password,nutrition,diet_planner,food_ai,exercise_hub,ai_assistant,exercise_videos,chatbot_api,chatapp,profile,edit_profile,create_post,chat,friends_list,discover_users,send_request,accept_request,user_profile,chat_inbox
from django.urls import path
from . import views
urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("logout/", logout_view, name="logout"),
path("forgot-password/", forgot_password, name="forgot_password"),
path("verify-otp/", verify_otp, name="verify_otp"),
path("reset-password/", reset_password, name="reset_password"),
path("nutrition/", nutrition, name="nutrition"),
path("diet-planner/", diet_planner, name="diet_planner"),
path("food-ai/", food_ai, name="food_ai"),
path("exercise/", exercise_hub, name="exercise_hub"),
    path("ai-assistant/", ai_assistant, name="ai_assistant"),  # ✅ ADD
    path("exercise-videos/", exercise_videos, name="exercise_videos"),
    path('digibook/', views.digibook, name='digibook'),
    path('save-entry/', views.save_entry, name='save_entry'),
    path('get-entries/', views.get_entries, name='get_entries'),

path("chatapp/", chatapp, name="chatapp"),
path("chatbot/", chatbot_api, name="chatbot_api"),
path("profile/", profile, name="profile"),
path("edit-profile/", edit_profile, name="edit_profile"),
path("create-post/", create_post, name="create_post"),

path("friends/", friends_list, name="friends"),
path("chat/<int:user_id>/", chat, name="chat"),
path("discover/", discover_users, name="discover"),
path("send-request/<int:user_id>/", send_request, name="send_request"),
path("accept-request/<int:req_id>/", accept_request, name="accept_request"),
path("user/<int:user_id>/", user_profile, name="view_profile"),
path("chat/", chat_inbox, name="chat_inbox"),
]