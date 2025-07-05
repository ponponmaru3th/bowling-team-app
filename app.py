import streamlit as st
import itertools

# カスタムCSS（デザイン）
st.markdown("""
    <style>
    .title {
        font-size: 36px;
        color: #4CAF50;
        font-weight: bold;
    }
    .team-box {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 2px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="title">🎳 Bowling Team Balancer</div>', unsafe_allow_html=True)

players = st.text_area("Enter players and scores (Name, Score)", 
"""A, 120
B, 150
C, 80
D, 100
E, 110
F, 130""")

if st.button("⚖️ Shuffle Teams"):
    lines = players.strip().split("\n")
    names_scores = [(line.split(",")[0].strip(), int(line.split(",")[1].strip())) for line in lines]

    best_diff = float('inf')
    best_teams = None
    n = len(names_scores)

    for team1 in itertools.combinations(names_scores, n // 2):
        team2 = [x for x in names_scores if x not in team1]
        score1 = sum(p[1] for p in team1)
        score2 = sum(p[1] for p in team2)
        diff = abs(score1 - score2)
        if diff < best_diff:
            best_diff = diff
            best_teams = (team1, team2)

    st.markdown('<div class="team-box">', unsafe_allow_html=True)
    st.subheader("🏆 Team 1")
    st.write([p[0] for p in best_teams[0]], " | Total Score:", sum(p[1] for p in best_teams[0]))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="team-box">', unsafe_allow_html=True)
    st.subheader("🎯 Team 2")
    st.write([p[0] for p in best_teams[1]], " | Total Score:", sum(p[1] for p in best_teams[1]))
    st.markdown('</div>', unsafe_allow_html=True)
