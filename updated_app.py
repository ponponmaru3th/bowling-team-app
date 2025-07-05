import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="🎳 Bowling Team Balancer", layout="centered")

st.markdown("<h1 style='text-align: center;'>🎳 Bowling Team Balancer</h1>", unsafe_allow_html=True)

# 初回の名前登録（セッションで保存）
if "player_names" not in st.session_state:
    st.subheader("👥 プレイヤーの名前を登録")
    num_players = st.number_input("人数を選んでください", min_value=2, max_value=20, step=1, key="num_players")
    st.session_state.player_names = [st.text_input(f"{i+1}人目の名前", key=f"name_{i}") for i in range(num_players)]
    if st.button("✅ 登録完了"):
        if all(st.session_state.player_names):
            st.session_state.names_fixed = True
        else:
            st.warning("全員の名前を入力してください。")

# 名前が確定した後のスコア入力
if st.session_state.get("names_fixed", False):
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

        # チーム分け：貪欲法（Greedy）
        teams = [[] for _ in range(team_count)]
        team_scores = [0] * team_count

        for _, row in df_sorted.iterrows():
            # 最もスコアが低いチームに追加
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
