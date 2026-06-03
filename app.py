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
IMAGES_PER_MODEL = 3

# ----------------------------
# LOAD MODELS
# ----------------------------
models = [
    d for d in os.listdir(IMAGE_FOLDER)
    if os.path.isdir(os.path.join(IMAGE_FOLDER, d))
]

if len(models) < 2:
    st.error("You need at least 2 model folders inside /images")
    st.stop()

# ----------------------------
# LOAD RATINGS
# ----------------------------
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        ratings = json.load(f)
else:
    ratings = {m: 1500 for m in models}

for m in models:
    if m not in ratings:
        ratings[m] = 1500


# ----------------------------
# ELO
# ----------------------------
def expected(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))


def update_elo(winner, loser):
    r_w = ratings[winner]
    r_l = ratings[loser]

    ew = expected(r_w, r_l)

    ratings[winner] = r_w + K * (1 - ew)
    ratings[loser] = r_l + K * (0 - (1 - ew))


def save():
    with open(STATE_FILE, "w") as f:
        json.dump(ratings, f)


# ----------------------------
# GET RANDOM MODELS
# ----------------------------
if "A" not in st.session_state:
    st.session_state.A = random.choice(models)

if "B" not in st.session_state:
    st.session_state.B = random.choice(models)


A = st.session_state.A
B = st.session_state.B


def show_model(model_name):
    path = os.path.join(IMAGE_FOLDER, model_name)
    imgs = os.listdir(path)[:IMAGES_PER_MODEL]

    for img in imgs:
        st.image(os.path.join(path, img), use_container_width=True)


# ----------------------------
# UI
# ----------------------------
st.title("📊 Model Ranking (Elo System)")

colA, colB = st.columns(2)

with colA:
    st.subheader(A)
    show_model(A)

with colB:
    st.subheader(B)
    show_model(B)

st.divider()

if st.button("⬅️ Left Model Wins"):
    update_elo(A, B)
    save()
    st.session_state.A = random.choice(models)
    st.session_state.B = random.choice(models)
    st.rerun()

if st.button("➡️ Right Model Wins"):
    update_elo(B, A)
    save()
    st.session_state.A = random.choice(models)
    st.session_state.B = random.choice(models)
    st.rerun()


# ----------------------------
# LEADERBOARD
# ----------------------------
st.divider()
st.subheader("🏆 Model Rankings")

for m, r in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
    st.write(f"{m} — {round(r, 1)}")
