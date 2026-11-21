import pandas as pd
from config import RANK_WEIGHTS

def determine_rank_type(rank_str: str) -> str:
    """
    Classifies rank / qualification string:
    - 'Судейская категория' (спортивные судьи)
    - 'Спортивный' (взрослые спортивные разряды и звания)
    - 'Юношеский' (юношеские спортивные разряды)
    - 'Без разряда' / 'Ученик'
    """
    if not rank_str:
        return "Без разряда"
    r = str(rank_str).strip().lower()
    if any(w in r for w in ["судья", "судейск", "категори", "юсс", "ссвк"]):
        return "Судейская категория"
    if any(w in r for w in ["спортивный", "кмс", "мс", "мсмк", "змс", "мастер спорта"]):
        return "Спортивный"
    if "юношеский" in r:
        return "Юношеский"
    if "без разряда" in r:
        return "Без разряда"
    return "Спортивный"

def is_judge_rank(rank_str: str) -> bool:
    """Returns True if the rank is a referee / judging category."""
    return determine_rank_type(rank_str) == "Судейская категория"

def is_sport_rank(rank_str: str) -> bool:
    """Returns True if the rank is a sport or junior rank."""
    return determine_rank_type(rank_str) in ["Спортивный", "Юношеский"]

def get_rank_weight(rank_str: str) -> int:
    """Calculates hierarchy weight for rank according to EVSK & judge regulations."""
    if not rank_str:
        return 0
    rank_clean = str(rank_str).strip()
    for k, w in RANK_WEIGHTS.items():
        if k.lower() in rank_clean.lower():
            return w
    return 0

def get_highest_rank_record(ranks_df: pd.DataFrame):
    """
    Selects the active (highest seniority) qualification record for an athlete.
    Sorts primarily by rank seniority weight, secondarily by latest order date.
    """
    if ranks_df is None or ranks_df.empty:
        return None
    df_sorted = ranks_df.copy()
    df_sorted["weight"] = df_sorted["rank"].map(get_rank_weight)
    df_sorted["parsed_date"] = pd.to_datetime(df_sorted["order_date"], format="%d.%m.%Y", errors="coerce")
    df_sorted = df_sorted.sort_values(by=["weight", "parsed_date"], ascending=[False, False])
    return df_sorted.iloc[0]

def get_highest_sport_rank_record(ranks_df: pd.DataFrame):
    """Selects the highest sports or junior rank record."""
    if ranks_df is None or ranks_df.empty:
        return None
    sport_df = ranks_df[ranks_df["rank"].map(is_sport_rank)]
    if sport_df.empty:
        return None
    return get_highest_rank_record(sport_df)

def get_highest_judge_rank_record(ranks_df: pd.DataFrame):
    """Selects the highest referee / judging qualification record."""
    if ranks_df is None or ranks_df.empty:
        return None
    judge_df = ranks_df[ranks_df["rank"].map(is_judge_rank)]
    if judge_df.empty:
        return None
    return get_highest_rank_record(judge_df)
