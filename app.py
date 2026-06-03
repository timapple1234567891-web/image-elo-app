import streamlit as st
import os
import random
import json

# ----------------------------
# CONFIG
# ----------------------------
IMAGE_FOLDER = "images"
STATE_FILE = "ratings.json"
STATS_FILE = "stats.json"
K = 32
IMAGES_PER_MODEL = 4

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

if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r") as f:
        stats = json.load(f)
else:
    stats = {
        m: {"wins": 0, "losses": 0}
        for m in models
    }

for m in models:
    if m not in stats:
        stats[m] = {"wins": 0, "losses": 0}


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

    stats[winner]["wins"] += 1
    stats[loser]["losses"] += 1


def save():
    with open(STATE_FILE, "w") as f:
        json.dump(ratings, f)

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)


# ----------------------------
# GET RANDOM MODELS
# ----------------------------

def get_two_models():
    return random.sample(models, 2)

if "A" not in st.session_state:
    st.session_state.A, st.session_state.B = get_two_models()


A = st.session_state.A
B = st.session_state.B


def show_model(model_name):
    path = os.path.join(IMAGE_FOLDER, model_name)

    imgs = os.listdir(path)

    if len(imgs) > IMAGES_PER_MODEL:
        imgs = random.sample(imgs, IMAGES_PER_MODEL)

    for img in imgs:
        st.image(
            os.path.join(path, img),
            use_container_width=True
        )


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
    st.session_state.A, st.session_state.B = get_two_models()
    st.rerun()

if st.button("➡️ Right Model Wins"):
    update_elo(B, A)
    save()
    st.session_state.A, st.session_state.B = get_two_models()
    st.rerun()

if st.button("🔄 Reset Ratings"):
    ratings = {m: 1500 for m in models}
    save()
    st.rerun()

# ----------------------------
# LEADERBOARD
# ----------------------------
st.divider()
st.subheader("🏆 Model Rankings")

for m, r in sorted(ratings.items(), key=lambda x: x[1], reverse=True):

    wins = stats[m]["wins"]
    losses = stats[m]["losses"]

    games = wins + losses

    if games > 0:
        win_pct = wins / games * 100
    else:
        win_pct = 0

    st.write(
        f"{m} — Elo: {round(r,1)} | "
        f"{wins}-{losses} | "
        f"{win_pct:.1f}%"
    )
