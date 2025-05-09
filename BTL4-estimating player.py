import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import logging
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import spearmanr, randint, uniform
from math import sqrt
import xgboost as xgb

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger('sklearn').setLevel(logging.CRITICAL)
plt.style.use('ggplot')


def load_data():
    features = pd.read_csv("BTL1.csv")
    values = pd.read_csv("BTL4.csv")
    for df in [features, values]:
        df["Player"] = df["Player"].str.strip().str.lower()
    merged = pd.merge(features, values, on="Player", how="inner", suffixes=('', '_drop'))
    merged = merged.filter(regex='^(?!.*_drop)')
    return merged


def preprocess_data(df):
    def convert_value(value):
        try:
            value = str(value).lower().replace("\u20ac", "").replace(",", "").strip()
            if 'm' in value: return float(value.replace('m', '')) * 1e6
            if 'k' in value: return float(value.replace('k', '')) * 1e3
            return float(value)
        except:
            return np.nan

    df["Transfer Value"] = df["Transfer Value"].apply(convert_value)
    df = df[df["Transfer Value"] > 1000]

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    extra_cols = ['Goal', 'Assists', 'Age']
    for col in extra_cols:
        if col in df.columns and col not in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            num_cols.append(col)

    df['Goal_per_Age'] = df['Goal'] / df['Age']
    df['Assists_per_Age'] = df['Assists'] / df['Age']
    df['Log_Transfer_Value'] = np.log1p(df['Transfer Value'])

    df[['Goal_per_Age', 'Assists_per_Age']] = df[['Goal_per_Age', 'Assists_per_Age']].fillna(0)
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    return df


def build_model(numeric_features):
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numeric_features)
    ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', xgb.XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1, verbosity=0))
    ])

    return model


def evaluate_model(model, X, y, log_target=True):
    pred = model.predict(X)
    if log_target:
        y_true = np.expm1(y)
        pred = np.expm1(pred)
    else:
        y_true = y

    rmse = sqrt(mean_squared_error(y_true, pred))
    mae = mean_absolute_error(y_true, pred)
    r2 = r2_score(y_true, pred)
    spear_corr, _ = spearmanr(y_true, pred)

    print(f"  R2 Score: {r2:.4f}")
    print(f"  RMSE: {rmse/1e6:.4f}")
    print(f"  MAE: {mae/1e6:.4f}")
    print(f"  Spearman: {spear_corr:.4f}")


if __name__ == "__main__":
    df = load_data()
    df = preprocess_data(df)

    X = df.drop(columns=['Transfer Value', 'Log_Transfer_Value', 'Player'])
    y = df['Log_Transfer_Value']
    numeric_features = X.select_dtypes(include=np.number).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = build_model(numeric_features)

    param_dist = {
        'regressor__n_estimators': randint(100, 400),
        'regressor__learning_rate': uniform(0.05, 0.2),
        'regressor__max_depth': randint(4, 8),
        'regressor__subsample': uniform(0.7, 0.3),
        'regressor__colsample_bytree': uniform(0.7, 0.3)
    }

    search = RandomizedSearchCV(model, param_dist, n_iter=15, cv=3,
                                scoring='neg_root_mean_squared_error', random_state=42, n_jobs=-1)
    search.fit(X_train, y_train)

    best_model = search.best_estimator_

    print("\nTrain:")
    evaluate_model(best_model, X_train, y_train)
    print("Test:")
    evaluate_model(best_model, X_test, y_test)
