import requests
import pandas as pd
import json
from functools import lru_cache

FACTION_HUES = {
    "shaper": "limegreen",
    "criminal": "royalblue",
    "anarch": "orangered",
    "adam": "gold",
    "jinteki": "crimson",
    "nbn": "darkorange",
    "haas-bioroid": "blueviolet",
    "weyland-consortium": "darkgreen",
    "sunny_lebeau": "violetpurple",
    "apex": "darkred",
    "neutralcorp": "gray",
    "neutralrunner": "gray",
}


@lru_cache
def get_cards():
    raw_card_data = requests.request(
        url="http://api-preview.netrunnerdb.com/api/v3/public/cards",
        method="GET",
        params={"page[limit]": 3000},
    ).json()["data"]
    df = pd.json_normalize(raw_card_data)
    df = df.drop(columns=df.columns[df.columns.str.startswith("relationships")])
    df.columns = df.columns.str.replace("attributes.", "")
    return df


@lru_cache
def get_tournament_json(tid, route="cobra"):
    """
    route: "cobra" or "alwaysberunning"
    tid: tournament id
    """
    if route == "cobra":
        url = f"https://tournaments.nullsignal.games/tournaments/{tid}.json"
    elif route == "alwaysberunning":
        print("Only cobra is supported for now")
        return None
    else:
        raise ValueError("route must be 'cobra' or 'alwaysberunning'")
    return requests.request(url=url, method="GET").json()


def get_player_dataframe(tournament_json):
    players = pd.DataFrame(tournament_json["players"])
    players = pd.merge(
        players,
        get_cards().query("card_type_id == 'corp_identity'")[
            ["stripped_title", "faction_id"]
        ],
        how="left",
        left_on="corpIdentity",
        right_on="stripped_title",
    ).rename(columns={"faction_id": "corpFaction"})
    players = pd.merge(
        players,
        get_cards().query("card_type_id == 'runner_identity'")[
            ["stripped_title", "faction_id"]
        ],
        how="left",
        left_on="runnerIdentity",
        right_on="stripped_title",
    ).rename(columns={"faction_id": "runnerFaction"})
    players = players.drop(columns=["stripped_title_x", "stripped_title_y"])
    return players


def get_elim_rankings(tournament_json):
    return pd.DataFrame(tournament_json["eliminationPlayers"])


def get_matches_dataframe(tournamet_json):
    return (
        pd.concat(
            [
                pd.json_normalize(tournamet_json["rounds"][i])
                for i in range(len(tournamet_json["rounds"]))
            ],
            keys=range(len(tournamet_json["rounds"])),
            names=["round"],
        )
        .reset_index(level=1, drop=True)
        .reset_index()
    )


def get_tournament_dataframes(tid):
    tournament_json = get_tournament_json(tid)
    return (
        get_player_dataframe(tournament_json),
        get_matches_dataframe(tournament_json),
        get_elim_rankings(tournament_json),
    )


def get_winrates_swiss(
    matches: pd.DataFrame,
    players: pd.DataFrame,
    n: int | None = None,
):
    if n is None or n <= 1:
        n = len(players)
    if n > len(players):
        n = len(players)
    if players is None or matches is None:
        raise ValueError("Must provide both players and matches")

    swiss_played_games = matches[
        (matches["intentionalDraw"] == False)
        & (matches["twoForOne"] == False)
        & (matches["eliminationGame"] == False)
    ]
    swiss_played_games = pd.merge(
        players.loc[: n - 1, ["id"]],
        swiss_played_games,
        how="left",
        left_on="id",
        right_on="player1.id",
    )
    result = swiss_played_games[
        [
            "player1.runnerScore",
            "player2.runnerScore",
            "player1.corpScore",
            "player2.corpScore",
        ]
    ].agg("sum")
    return {
        "runner_wins": round(
            (result["player1.runnerScore"] + result["player2.runnerScore"]) / 3, 0
        ),
        "corp_wins": round(
            (result["player1.corpScore"] + result["player2.corpScore"]) / 3, 0
        ),
    }


def get_winrates_cut(matches):
    elim_matches = matches[matches["eliminationGame"]].copy()

    elim_matches["winning_side"] = elim_matches.apply(
        lambda row: row["player1.role"]
        if row["player1.winner"]
        else row["player2.role"],
        axis=1,
    )
    win_counts = (
        elim_matches["winning_side"].groupby(elim_matches["winning_side"]).size()
    )
    return {
        "runner_wins": win_counts["runner"],
        "corp_wins": win_counts["corp"],
    }
