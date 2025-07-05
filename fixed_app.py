import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎳 Bowling Team Balancer", layout="centered")

st.markdown("<h1 style='text-align: center;'>🎳 Bowling Team Balancer</h1>", unsafe_allow_html=True)

# 初期化（初回のみ）
if "names_fixed" not in st.session_state:
    st.session_state.names_fixed = False
if "player_names" not in st.session_state:
    st.session_state.player_names = []
if "num_players" not in st.session_state:
    st.session_state.num_players = 2

# 名前登録フェーズ
if not st.session_state.names_fixed:
    st.subheader("👥 プレイヤーの名前を登録")
    st.session_state.num_players = st.number_input("人数を選んでください", min_value=2, max_value=20, step=1)

    names = []
    for i in range(st.session_state.num_players):
        name = st.text_input(f"{i+1}人目の名前", key=f"name_{i}")
        names.append(name)

    if st.button("✅ 登録完了"):
        if all(names):
            st.session_state.player_names = names
            st.session_state.names_fixed = True
        else:
            st.warning("全員の名前を入力してください。")

# スコア入力とチーム分けフェーズ
if st.session_state.names_fixed:
    st.subheader("🎯 今回のスコアを入力")
    scores = {}
    for name in st.session_state.player_names:
        scores[name] = st.number_input(f"{name} のスコア", min_value=0, max_value=300, step=1, key=f"score_{name}")

    st.subheader("🔢 チーム数を選択")
    team_count = st.number_input("チーム数", min_value=2, max_value=len(st.session_state.player_names), step=1, value=2)

    if st.button("⚖️ チーム分けを実行"):
        df = pd.DataFrame(list(scores.items()), columns=["Name", "Score"])
        df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

        st.markdown("### 🏆 ランキング")
        st.dataframe(df_sorted)

        # チーム分け（貪欲法）
        teams = [[] for _ in range(team_count)]
        team_scores = [0] * team_count

        for _, row in df_sorted.iterrows():
            idx = team_scores.index(min(team_scores))
            teams[idx].append((row["Name"], row["Score"]))
            team_scores[idx] += row["Score"]

        st.markdown("### 📦 チーム分け結果")
        for i, team in enumerate(teams):
            members = [f"{name}（{score}）" for name, score in team]
            total = sum(score for _, score in team)
            st.markdown(f"**Team {i+1}**（合計スコア：{total}）")
            st.write(", ".join(members))
            st.markdown("---")

    st.markdown("🔄 プレイヤー登録をリセットしたい場合は、ページをリロードしてください。")
