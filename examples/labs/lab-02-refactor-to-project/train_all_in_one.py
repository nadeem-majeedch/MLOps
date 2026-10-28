"""Lab 02 starter: the script that "works on my machine".

Everything is in one file, three decisions are hard-coded, and the data is read
when the module is imported rather than when training is requested. It produces
a useful number, which is exactly why nobody has refactored it yet.

    python train_all_in_one.py
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

DATA = pd.read_csv("data/sessions.csv")  # runs at import time
FEATURES = ["hours", "prior_score", "sleep_hours"]
TARGET = "score"


def main():
    train, test = train_test_split(DATA, test_size=0.25, random_state=42)
    model = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42)
    model.fit(train[FEATURES], train[TARGET])
    predictions = model.predict(test[FEATURES])
    print("rows", len(train), len(test))
    print("mae", round(mean_absolute_error(test[TARGET], predictions), 4))
    print("r2", round(r2_score(test[TARGET], predictions), 4))
    joblib.dump(model, "model.pkl")
    print("wrote model.pkl")


main()
