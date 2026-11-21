import pandas as pd
from config import RANK_WEIGHTS

def get_rank_weight(rank_str: str) -> int:
    """Calculates hierarchy weight for rank according to EVSK standard."""
    if not rank_str:
        return 0
    rank_clean = str(rank_str).strip()
    for k, w in RANK_WEIGHTS.items():
        if k.lower() in rank_clean.lower():
            return w
    return 0

def get_highest_rank_record(ranks_df: pd.DataFrame):
    """
    Selects the active (highest seniority) rank record for an athlete.
    Sorts primarily by rank seniority weight, secondarily by latest order date.
    """
    if ranks_df is None or ranks_df.empty:
        return None
    df_sorted = ranks_df.copy()
    df_sorted["weight"] = df_sorted["rank"].map(get_rank_weight)
    df_sorted["parsed_date"] = pd.to_datetime(df_sorted["order_date"], format="%d.%m.%Y", errors="coerce")
    df_sorted = df_sorted.sort_values(by=["weight", "parsed_date"], ascending=[False, False])
    return df_sorted.iloc[0]
