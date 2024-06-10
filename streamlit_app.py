import streamlit as st
import pandas as pd
import json

# Oyuncu sınıfı tanımı
class Player:
    def __init__(self, name):
        self.name = name
        self.league_position = None
        self.target_hit = None
        self.cup_stage = None
        self.yellow_cards = 0
        self.red_cards = 0
        self.goals_conceded = 0
        self.goals_scored = 0
        self.interviews = 0
        self.penalty_points = []
        self.score = 0

# Veri kaydetme fonksiyonu
def save_data(players, filename="players.json"):
    data = []
    for player in players:
        player_data = {
            "name": player.name,
            "league_position": player.league_position,
            "target_hit": player.target_hit,
            "cup_stage": player.cup_stage,
            "yellow_cards": player.yellow_cards,
            "red_cards": player.red_cards,
            "goals_conceded": player.goals_conceded,
            "goals_scored": player.goals_scored,
            "interviews": player.interviews,
            "penalty_points": player.penalty_points,
            "score": player.score
        }
        data.append(player_data)
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

# Veri yükleme fonksiyonu
def load_data(filename="players.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    players = []
    for player_data in data:
        player = Player(player_data["name"])
        player.league_position = player_data["league_position"]
        player.target_hit = player_data["target_hit"]
        player.cup_stage = player_data["cup_stage"]
        player.yellow_cards = player_data["yellow_cards"]
        player.red_cards = player_data["red_cards"]
        player.goals_conceded = player_data["goals_conceded"]
        player.goals_scored = player_data["goals_scored"]
        player.interviews = player_data["interviews"]
        player.penalty_points = player_data["penalty_points"]
        player.score = player_data["score"]
        players.append(player)
    return players

# Fair play ödüllerini belirleme
def calculate_fair_play_points(players):
    if not players:
        st.warning("Oyuncu listesi boş. Lütfen en az bir oyuncu ekleyin.")
        return

    min_yellow_cards = min(players, key=lambda p: p.yellow_cards).yellow_cards
    min_red_cards = min(players, key=lambda p: p.red_cards).red_cards

    for player in players:
        if player.yellow_cards == min_yellow_cards and player.red_cards == min_red_cards:
            player.score += 1

# En az gol yiyen ve en çok gol atan takımlara ödül verme
def calculate_goal_awards(players):
    if not players:
        st.warning("Oyuncu listesi boş. Lütfen en az bir oyuncu ekleyin.")
        return

    min_goals_conceded = min(players, key=lambda p: p.goals_conceded).goals_conceded
    max_goals_scored = max(players, key=lambda p: p.goals_scored).goals_scored

    for player in players:
        if player.goals_conceded == min_goals_conceded:
            player.score += 1
        if player.goals_scored == max_goals_scored:
            player.score += 1

# Kural ihlallerine göre ceza puanları ekleme
def apply_penalty_points(players):
    penalties = {
        "Transfer ihlali": -3,
        "İç transfer ihlali": -5,
        "Aktiflik ihlali": -1,
        "Aynı takım arası iç transfer ihlali": -5,
        "Toplam iç transfer sayısı ihlali": -5,
        "Kadro planlaması ihlali": -6
    }

    for player in players:
        for violation in player.penalty_points:
            if violation in penalties:
                player.score += penalties[violation]

def create_dataframe(players):
    df_players = pd.DataFrame({
        "Oyuncu": [player.name for player in players],
        "Lig Sıralaması": [player.league_position for player in players],
        "Hedef Tutturması": [player.target_hit for player in players],
        "Kupa Aşaması": [player.cup_stage for player in players],
        "Sarı Kartlar": [player.yellow_cards for player in players],
        "Kırmızı Kartlar": [player.red_cards for player in players],
        "Yenilen Goller": [player.goals_conceded for player in players],
        "Atılan Goller": [player.goals_scored for player in players],
        "Röportaj Sayısı": [player.interviews for player in players],
        "Cezalar": [player.penalty_points for player in players],
        "Puan": [player.score for player in players]
    })
    return df_players

def calculate_scores(players):
    penalties = {
        "Transfer ihlali": -3,
        "İç transfer ihlali": -5,
        "Aktiflik ihlali": -1,
        "Aynı takım arası iç transfer ihlali": -5,
        "Toplam iç transfer sayısı ihlali": -5,
        "Kadro planlaması ihlali": -6
    }

    for player in players:
        penalty_score = sum(penalties.get(penalty, 0) for penalty in player.penalty_points)
        player.score = (
            20 - int(player.league_position) +
            int(player.target_hit) +
            int(player.cup_stage) +
            (1 if player.yellow_cards == 0 else 0) +
            (1 if player.goals_conceded == min([p.goals_conceded for p in players]) else 0) +
            (1 if player.goals_scored == max([p.goals_scored for p in players]) else 0) +
            (1 if player.interviews >= 25 else 0) +
            penalty_score
        )

# Ana uygulama akışı
def main():
    st.title("Özel Online Score Manager Ligi")

    player_name = st.text_input("Oyuncu İsmi")
    player_league_position = st.number_input("Lig Sıralaması", min_value=1, max_value=20)
    player_target_hit = st.selectbox("Hedef Tutturması", options=[1, -1], index=0)
    player_cup_stage = st.selectbox("Kupa Aşaması", options=[4, 3, 2, 1], index=0)
    player_yellow_cards = st.number_input("Sarı Kartlar", min_value=0)
    player_red_cards = st.number_input("Kırmızı Kartlar", min_value=0)
    player_goals_conceded = st.number_input("Yenilen Goller", min_value=0)
    player_goals_scored = st.number_input("Atılan Goller", min_value=0)
    player_interviews = st.number_input("Röportaj Sayısı", min_value=0)
    player_penalties = st.multiselect("Kural İhlalleri", options=[
        "Transfer ihlali",
        "İç transfer ihlali",
        "Aktiflik ihlali",
        "Aynı takım arası iç transfer ihlali",
        "Toplam iç transfer sayısı ihlali",
        "Kadro planlaması ihlali"
    ])

    if st.button("Ekle"):
        new_player = Player(player_name)
        new_player.league_position = player_league_position
        new_player.target_hit = player_target_hit
        new_player.cup_stage = player_cup_stage
        new_player.yellow_cards = player_yellow_cards
        new_player.red_cards = player_red_cards
        new_player.goals_conceded = player_goals_conceded
        new_player.goals_scored = player_goals_scored
        new_player.interviews = player_interviews
        new_player.penalty_points = player_penalties

        # Oyuncuyu ekleyip kaydet
        players = load_data()
        players.append(new_player)
        save_data(players)
        st.success(f"{player_name} eklendi!")

    # DataFrame'i oluştur
    players = load_data()
    df_players = create_dataframe(players)

    # Seçilen oyuncunun adını tutacak değişken
    selected_player_name = st.selectbox("Güncellenecek Oyuncu Seç", [player.name for player in players])

    # Seçilen oyuncuyu bul
    selected_player = None
    for player in players:
        if player.name == selected_player_name:
            selected_player = player
            break

    if selected_player:
        st.subheader("Oyuncu Bilgileri")
        st.write(f"Seçilen Oyuncu: {selected_player.name}")
        selected_player.league_position = st.number_input("Lig Sıralaması", min_value=1, max_value=20, value=selected_player.league_position, key="league_position")
        selected_player.target_hit = st.selectbox("Hedef Tutturması", options=[1, -1], index=0 if selected_player.target_hit == 1 else 1, key="target_hit")
        selected_player.cup_stage = st.selectbox("Kupa Aşaması", options=[4, 3, 2, 1], index=selected_player.cup_stage - 1, key="cup_stage")
        selected_player.yellow_cards = st.number_input("Sarı Kartlar", min_value=0, value=selected_player.yellow_cards, key="yellow_cards")
        selected_player.red_cards = st.number_input("Kırmızı Kartlar", min_value=0, value=selected_player.red_cards, key="red_cards")
        selected_player.goals_conceded = st.number_input("Yenilen Goller", min_value=0, value=selected_player.goals_conceded, key="goals_conceded")
        selected_player.goals_scored = st.number_input("Atılan Goller", min_value=0, value=selected_player.goals_scored, key="goals_scored")
        selected_player.interviews = st.number_input("Röportaj Sayısı", min_value=0, value=selected_player.interviews, key="interviews")
        selected_player.penalty_points = st.multiselect("Kural İhlalleri", options=[
            "Transfer ihlali",
            "İç transfer ihlali",
            "Aktiflik ihlali",
            "Aynı takım arası iç transfer ihlali",
            "Toplam iç transfer sayısı ihlali",
            "Kadro planlaması ihlali"
        ], default=selected_player.penalty_points, key="penalty_points")
    
        if st.button("Güncelle"):
            save_data(players)
            st.success(f"{selected_player.name} güncellendi!")
    

    # Hesapla bölümü
    if st.button("Hesapla"):
        players = load_data()
        calculate_fair_play_points(players)
        calculate_goal_awards(players)
        apply_penalty_points(players)
        calculate_scores(players)
        df_players=create_dataframe(players)
        save_data(players)
        st.success("Hesaplamalar yapıldı ve ödüller verildi!")

    # DataFrame'i görüntüle
    st.write(df_players)

    # Excel çıktısı
    if st.button("Excel İndir"):
        # Excel dosyasını oluştur
        df_players.to_excel('oyuncu_verileri.xlsx', index=False)
        # Excel dosyasını indirme linki
        with open('oyuncu_verileri.xlsx', 'rb') as f:
            st.download_button(
                label="Excel Dosyasını İndir",
                data=f,
                file_name='oyuncu_verileri.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

# Uygulama başlatma
if __name__ == "__main__":
    main()
