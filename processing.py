# processing.py
import pandas as pd
from typing import Optional

from helpers import _columns_in_condition

def default_config(profile_df: pd.DataFrame) -> pd.DataFrame:
    cfg = profile_df["column dtype sample"].copy() if "column dtype sample" in profile_df else profile_df
    cfg = profile_df[["column", "dtype", "non_null", "nulls", "% null", "unique"]].copy()
    cfg["enforce_not_null"] = False
    cfg["drop_duplicates_by_this_col"] = False
    cfg["strip_whitespace"] = cfg["dtype"].str.contains("object|string", case=False, regex=True)
    cfg["to_lowercase"] = False
    cfg["validate_email"] = cfg["column"].str.contains("email", case=False)
    cfg["as_dtype"] = "keep"
    cfg["datetime_format"] = ""
    cfg["fillna_value"] = ""
    cfg["input_condition"] = ""
    return cfg


def apply_preview(df: pd.DataFrame, cfg_df: pd.DataFrame, global_conditions: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    tmp = df.copy()
    for _, row in cfg_df.iterrows():
        c = row["column"]
        if c not in tmp.columns:
            continue
        if bool(row.get("strip_whitespace", False)):
            tmp[c] = tmp[c].astype(str).str.strip()
        if bool(row.get("to_lowercase", False)):
            tmp[c] = tmp[c].astype(str).str.lower()
        as_dtype = str(row.get("as_dtype", "keep"))
        if as_dtype == "string":
            tmp[c] = tmp[c].astype("string")
        elif as_dtype == "int":
            tmp[c] = pd.to_numeric(tmp[c], errors="coerce").astype("Int64")
        elif as_dtype == "float":
            tmp[c] = pd.to_numeric(tmp[c], errors="coerce")
        elif as_dtype == "bool":
            tmp[c] = tmp[c].astype(str).str.strip().str.lower().map({"true": True, "false": False, "1": True, "0": False}).astype("boolean")
        elif as_dtype == "datetime":
            fmt = str(row.get("datetime_format", "") or "")
            if fmt:
                tmp[c] = pd.to_datetime(tmp[c], format=fmt, errors="coerce")
            else:
                tmp[c] = pd.to_datetime(tmp[c], errors="coerce")
        if bool(row.get("validate_email", False)):
            mask = tmp[c].astype(str).str.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", na=False)
            tmp = tmp[mask]
        if bool(row.get("enforce_not_null", False)):
            tmp = tmp[tmp[c].notna()]
        if bool(row.get("drop_duplicates_by_this_col", False)):
            tmp = tmp.drop_duplicates(subset=[c])
        fv = row.get("fillna_value", "")
        if str(fv).strip() != "":
            try:
                float(fv)
                val_expr = float(fv)
            except Exception:
                val_expr = fv
            tmp[c] = tmp[c].fillna(val_expr)

        # per-column condition
        cond = str(row.get("input_condition", "") or "").strip()
        if cond:
            try:
                referenced = _columns_in_condition(cond, list(tmp.columns))
                for rc in referenced:
                    if rc in tmp.columns and not pd.api.types.is_datetime64_any_dtype(tmp[rc]):
                        tmp[rc] = pd.to_datetime(tmp[rc], errors="coerce")
                tmp = tmp.query(cond)
            except Exception:
                # leave preview tolerant
                pass

    # apply globals
    if global_conditions is not None:
        for _, g in global_conditions.sort_values("apply_order").iterrows():
            if not bool(g.get("active", True)):
                continue
            cond = str(g.get("condition", "") or "").strip()
            if not cond:
                continue
            try:
                referenced = _columns_in_condition(cond, list(tmp.columns))
                for rc in referenced:
                    if rc in tmp.columns and not pd.api.types.is_datetime64_any_dtype(tmp[rc]):
                        tmp[rc] = pd.to_datetime(tmp[rc], errors="coerce")
                tmp = tmp.query(cond)
            except Exception:
                pass
    return tmp