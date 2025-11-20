import os
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "default")

PROMPT_TEMPLATE = """
You are a professional Python engineer. Produce a single self-contained Python script (ONLY the Python code, no extra explanation)
that defines a function `def apply_cleaning(input_path: str, output_path: str = 'cleaned.csv') -> None:` which:
1. loads the CSV at input_path with pandas,
2. applies column-level operations exactly as provided in column_config (strip, lowercase, dtype conversions, email validation, enforce_not_null, drop duplicates, fillna, and per-column input_condition using pandas.query),
3. then applies the global business rules (global_conditions) in order by apply_order,
4. before any query that compares dates, convert referenced columns to datetime using pd.to_datetime(..., errors='coerce'),
5. wrap query applications in try/except and print warnings but continue,
6. finally saves cleaned DataFrame to output_path,
Include a one-line inline comment above each logical block. End with an `if __name__ == '__main__':` example call.
Do NOT include langchain or openai client code in the generated file — only pandas and stdlib.
Return only valid Python code.
# Inputs (JSON)
column_config = {column_config}
global_conditions = {global_conditions}
"""

