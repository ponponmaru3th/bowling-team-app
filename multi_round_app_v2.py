import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="🎳 Bowling Team Tournament", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎳 Bowling Team Tournament</h1>", unsafe_allow_html=True)

# 初期化（セッション）
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.names_fixed = False
    st.session_state.player_names = []
    st.session_state.points = {}
    st.session_state.total_scores = {}
    st.session_state.history = []
    st.session_state.victory_points = 1
    st.session_state.defeat_points = -1

# 名前入力フェーズ
if not st.session_state.names_fixed:
    st.subheader("👥 プレイヤー登録")
    num_players = st.number_input("参加人数を選んでください", min_value=2, max_value=20, step=1)
    names = []
    for i in range(num_players):
        name = st.text_input(f"{i+1}人目の名前", key=f"name_{i}")
        names.append(name)

    st.subheader("🏅 ポイント設定")
    st.session_state.victory_points = st.number_input("勝者のポイント", value=1, step=1)
    st.session_state.defeat_points = st.number_input("敗者のポイント", value=-1, step=1)

    if st.button("✅ 登録完了"):
        if all(names):
            st.session_state.player_names = names
            st.session_state.names_fixed = True
            for name in names:
                st.session_state.points[name] = 0
                st.session_state.total_scores[name] = 0
        else:
            st.warning("全員の名前を入力してください。")

# ラウンド実行フェーズ
if st.session_state.names_fixed:
    st.markdown(f"### 🕓 ラウンド {st.session_state.round}")
    scores = {}
    for name in st.session_state.player_names:
        scores[name] = st.number_input(f"{name} のスコア", min_value=0, max_value=300, step=1, key=f"score_r{st.session_state.round}_{name}")

    if st.button("⚖️ チーム分け＆勝敗判定"):
        df = pd.DataFrame(list(scores.items()), columns=["Name", "Score"])
        df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

        # チーム分け（Greedy 2チーム）
        teams = [[], []]
        team_scores = [0, 0]

        for _, row in df_sorted.iterrows():
            idx = team_scores.index(min(team_scores))
            teams[idx].append((row["Name"], row["Score"]))
            team_scores[idx] += row["Score"]

        # 平均スコアで勝敗決定
        avg_scores = [team_scores[i] / len(teams[i]) if len(teams[i]) > 0 else 0 for i in range(2)]
        if avg_scores[0] > avg_scores[1]:
            winner, loser = 0, 1
        elif avg_scores[1] > avg_scores[0]:
            winner, loser = 1, 0
        else:
            # 平均スコアも同じなら、最高得点者がいるチームを勝ちにする
            top_scorer = df_sorted.iloc[0]["Name"]
            for i, team in enumerate(teams):
                if any(member[0] == top_scorer for member in team):
                    winner = i
                    loser = 1 - i
                    break

        # ポイント＆合計スコア加算
        for i, team in enumerate(teams):
            for name, score in team:
                st.session_state.total_scores[name] += score
                if i == winner:
                    st.session_state.points[name] += st.session_state.victory_points
                else:
                    st.session_state.points[name] += st.session_state.defeat_points

        # 結果記録
        st.session_state.history.append({
            "round": st.session_state.round,
            "teams": teams,
            "scores": scores,
            "winner": winner
        })

        # 表示
        st.markdown("### ✅ 勝敗結果")
        for i, team in enumerate(teams):
            members = [f"{n}（{s}）" for n, s in team]
            st.markdown(f"**Team {i+1}** {'🏆 WINNER' if i == winner else ''}")
            st.write(", ".join(members))
            st.markdown(f"平均スコア: {avg_scores[i]:.2f} / 合計: {team_scores[i]}")
            st.markdown("---")

        st.session_state.round += 1

    col1, col2 = st.columns(2)
    if col1.button("🔁 次のラウンドへ"):
        st.rerun()

    if col2.button("🏁 このラウンドで終了"):
        st.session_state.end_flag = True
        st.rerun()

# 終了後：結果表示
if st.session_state.get("end_flag", False):
    st.header("📊 トーナメント結果")

    # ポイント＆スコア ランキング
    data = []
    for name in st.session_state.player_names:
        data.append({
            "Name": name,
            "Total Score": st.session_state.total_scores[name],
            "Points": st.session_state.points[name]
        })
    df_result = pd.DataFrame(data).sort_values(by=["Points", "Total Score"], ascending=False)
    st.subheader("🏅 最終ランキング（ポイント → スコア）")
    st.dataframe(df_result.reset_index(drop=True))

    # 各ラウンド履歴
    st.subheader("📖 各ラウンドの記録")
    for record in st.session_state.history:
        st.markdown(f"### 🕓 Round {record['round']}")
        for i, team in enumerate(record["teams"]):
            members = [f"{n}（{s}）" for n, s in team]
            win_tag = "🏆 WINNER" if i == record["winner"] else ""
            st.markdown(f"**Team {i+1}** {win_tag}")
            st.write(", ".join(members))
        st.markdown("---")
