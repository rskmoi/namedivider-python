import typer
import pandas as pd
import lightgbm as lgb


def get_feature_and_target(df: pd.DataFrame):
    X = df[["rank",
            "fullname_length",
            "family_length",
            "given_length",
            "family_order_score",
            "given_order_score",
            "family_length_score",
            "given_length_score",
            "given_startswith_specific_kanji"]]
    Y = df["target"]
    return X, Y


def train(src_train: str, src_valid: str, dst: str):
    df_train = pd.read_csv(src_train)
    df_train_x, df_train_y = get_feature_and_target(df_train)
    df_valid = pd.read_csv(src_valid)
    df_valid_x, df_valid_y = get_feature_and_target(df_valid)
    lgb_train = lgb.Dataset(df_train_x, df_train_y)
    lgb_valid = lgb.Dataset(df_valid_x, df_valid_y)
    params = {"objective": "binary",
              "metric": "auc",
              "n_estimators": 10000}
    gbm = lgb.train(params, lgb_train, valid_sets=[lgb_valid], early_stopping_rounds=200)
    gbm.save_model(dst)


if __name__ == '__main__':
    typer.run(train)