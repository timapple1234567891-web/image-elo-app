import streamlit as st
import os
import random
import json

# ----------------------------
# CONFIG
# ----------------------------
IMAGE_FOLDER = "images"
STATE_FILE = "ratings.json"
K = 32

# ----------------------------
# LOAD IMAGES
# ----------------------------
images = [f for f in os.listdir(IMAGE_FOLDER)
          if f.lower().endswith((".png", ".jpg", ".jpeg"))]

# ----------------------------
# LOAD / INIT RATINGS
# ----------------------------
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        ratings = json.load(f)
else:
    ratings = {img: 1500 for img in images}

# Ensure new images get added
for img in images:
    if img not in ratings:
        ratings[img] = 1500


# ----------------------------
# ELO FUNCTION
# ----------------------------
def expected(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))


def update_elo(winner, loser):
    global ratings
    r_w = ratings[winner]
    r_l = ratings[loser]

    ew = expected(r_w, r_l)
    el = 1 - ew

    ratings[winner] = r_w + K * (1 - ew)
    ratings[loser] = r_l + K * (0 - el)


def save():
    with open(STATE_FILE, "w") as f:
        json.dump(ratings, f)


# ----------------------------
# SESSION STATE PAIR
# ----------------------------
if "pair" not in st.session_state:
    st.session_state.pair = random.sample(images, 2)


def new_pair():
    st.session_state.pair = random.sample(images, 2)


img1, img2 = st.session_state.pair

# ----------------------------
# UI
# ----------------------------
st.title("📊 Image Elo Ranking")

col1, col2 = st.columns(2)

with col1:
    st.image(os.path.join(IMAGE_FOLDER, img1), use_container_width=True)
    if st.button("⬅️ Left wins"):
        update_elo(img1, img2)
        save()
        new_pair()

with col2:
    st.image(os.path.join(IMAGE_FOLDER, img2), use_container_width=True)
    if st.button("Right wins ➡️"):
        update_elo(img2, img1)
        save()
        new_pair()

# ----------------------------
# LEADERBOARD
# ----------------------------
st.divider()
st.subheader("🏆 Ranking")

sorted_imgs = sorted(ratings.items(), key=lambda x: x[1], reverse=True)

for img, score in sorted_imgs:
    st.write(f"{img} — {round(score, 1)}")
