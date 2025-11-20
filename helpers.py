import pandas as pd
import re
from typing import List

EMAIL_REGEX = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def memory_usage_mb(df: pd.DataFrame) -> float:
    return round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)


def read_uploaded_file(upload) -> pd.DataFrame:
    if upload.name.endswith((".xlsx", ".xls")):
        return pd.read_excel(upload)
    return pd.read_csv(upload)


def basic_profile(df: pd.DataFrame) -> pd.DataFrame:
    info = []
    for col in df.columns:
        s = df[col]
        info.append({
            "column": col,
            "dtype": str(s.dtype),
            "non_null": int(s.notna().sum()),
            "nulls": int(s.isna().sum()),
            "% null": round(100 * s.isna().mean(), 2),
            "unique": int(s.nunique(dropna=True)),
            "sample": s.dropna().astype(str).head(5).tolist()
        })
    return pd.DataFrame(info)


def _columns_in_condition(cond: str, available_cols: List[str]) -> List[str]:
    if not cond:
        return []
    cols_found = set()
    for m in re.finditer(r"`([^`]+)`", cond):
        name = m.group(1)
        if name in available_cols:
            cols_found.add(name)
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", cond):
        name = m.group(1)
        if name in available_cols:
            cols_found.add(name)
    return list(cols_found)