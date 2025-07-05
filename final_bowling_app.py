import streamlit as st
import pandas as pd

st.set_page_config(page_title="🎳 Bowling Tournament", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎳 Bowling Tournament</h1>", unsafe_allow_html=True)

# 初期化
if "round" not in st.session_state:
    st.session_state.round = 0  # プレラウンド
    st.session_state.names_fixed = False
    st.session_state.player_names = []
    st.session_state.points = {}
    st.session_state.total_scores = {}
    st.session_state.history = []
    st.session_state.victory_points = 1
    st.session_state.defeat_points = -1

# 名前登録
if not st.session_state.names_fixed:
    st.subheader("👥 プレイヤー登録")
    num_players = st.number_input("参加人数", min_value=2, max_value=20, step=1)
    names = []
    for i in range(num_players):
        name = st.text_input(f"{i+1}人目の名前", key=f"name_{i}")
        names.append(name)

    st.subheader("🏅 ポイント設定")
    st.session_state.victory_points = st.number_input("勝利ポイント", value=1)
    st.session_state.defeat_points = st.number_input("敗北ポイント", value=-1)

    if st.button("✅ 登録完了"):
        if all(names):
            st.session_state.player_names = names
            st.session_state.names_fixed = True
            for name in names:
                st.session_state.points[name] = 0
                st.session_state.total_scores[name] = 0
        else:
            st.warning("全員の名前を入力してください。")

# スコア入力フェーズ
if st.session_state.names_fixed:
    if st.session_state.round == 0:
        st.subheader("🟡 プレラウンド（参考スコア）")
    else:
        st.subheader(f"🕓 ラウンド {st.session_state.round}")

    scores = {}
    for name in st.session_state.player_names:
        scores[name] = st.number_input(f"{name} のスコア", min_value=0, max_value=300, step=1, key=f"score_r{st.session_state.round}_{name}")

    if st.button("⚖️ チーム分け" if st.session_state.round == 0 else "🏁 勝敗判定とチーム再編成"):
        df = pd.DataFrame(list(scores.items()), columns=["Name", "Score"])
        df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

        # バランスよくチーム分け：奇数は先に多く
        team1, team2 = [], []
        for idx, row in df_sorted.iterrows():
            if idx % 2 == 0:
                team1.append((row["Name"], row["Score"]))
            else:
                team2.append((row["Name"], row["Score"]))

        teams = [team1, team2]
        team_scores = [sum(score for _, score in team) for team in teams]
        avg_scores = [team_scores[i]/len(teams[i]) if len(teams[i]) else 0 for i in range(2)]

        if st.session_state.round == 0:
            # プレラウンド：チーム表示だけ
            st.markdown("### 🟡 プレラウンド結果（参考）")
            for i, team in enumerate(teams):
                members = [f"{n}（{s}）" for n, s in team]
                st.markdown(f"**Team {i+1}**")
                st.write(", ".join(members))
                st.markdown("---")
        else:
            # 勝敗判定
            if avg_scores[0] > avg_scores[1]:
                winner, loser = 0, 1
            elif avg_scores[1] > avg_scores[0]:
                winner, loser = 1, 0
            else:
                top_name = df_sorted.iloc[0]["Name"]
                winner = 0 if any(n == top_name for n, _ in team1) else 1
                loser = 1 - winner

            # ポイント加算＆記録
            for i, team in enumerate(teams):
                for name, score in team:
                    st.session_state.total_scores[name] += score
                    if i == winner:
                        st.session_state.points[name] += st.session_state.victory_points
                    else:
                        st.session_state.points[name] += st.session_state.defeat_points

            st.session_state.history.append({
                "round": st.session_state.round,
                "teams": teams,
                "scores": scores,
                "winner": winner
            })

            # 表示
            st.markdown(f"### ✅ ラウンド {st.session_state.round} 結果")
            for i, team in enumerate(teams):
                members = [f"{n}（{s}）" for n, s in team]
                tag = "🏆 WINNER" if i == winner else ""
                st.markdown(f"**Team {i+1}** {tag}")
                st.write(", ".join(members))
                st.markdown(f"平均スコア: {avg_scores[i]:.2f}")
                st.markdown("---")

        st.session_state.round += 1
        st.rerun()

    col1, col2 = st.columns(2)
    if col1.button("▶ 次のラウンドへ"):
        st.rerun()

    if col2.button("🛑 このラウンドで終了"):
        st.session_state.end_flag = True
        st.rerun()

# 終了後：最終結果
if st.session_state.get("end_flag", False):
    st.header("📊 トーナメント結果")

    data = []
    for name in st.session_state.player_names:
        data.append({
            "Name": name,
            "Total Score": st.session_state.total_scores[name],
            "Points": st.session_state.points[name]
        })
    df_result = pd.DataFrame(data).sort_values(by=["Points", "Total Score"], ascending=False)
    st.subheader("🏅 最終ランキング")
    st.dataframe(df_result.reset_index(drop=True))

    st.subheader("📖 各ラウンドの記録")
    for record in st.session_state.history:
        st.markdown(f"### 🕓 Round {record['round']}")
        for i, team in enumerate(record["teams"]):
            members = [f"{n}（{s}）" for n, s in team]
            win_tag = "🏆 WINNER" if i == record["winner"] else ""
            st.markdown(f"**Team {i+1}** {win_tag}")
            st.write(", ".join(members))
        st.markdown("---")
