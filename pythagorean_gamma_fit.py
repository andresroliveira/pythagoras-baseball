import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar


def prepare_data(teams):
    df = teams[["yearID", "teamID", "lgID", "W", "L", "R", "RA"]].copy()

    df = df.dropna(subset=["W", "L", "R", "RA"])
    df = df[(df["W"] > 0) & (df["L"] > 0) & (df["R"] > 0) & (df["RA"] > 0)]

    df["G"] = df["W"] + df["L"]
    df["WinPct"] = df["W"] / df["G"]
    df["RA_over_RS"] = df["RA"] / df["R"]

    df["X"] = np.log(df["RA_over_RS"])
    df["Y"] = np.log(1 / df["WinPct"] - 1)

    return df


def predict_win_pct(df, gamma):
    return 1 / (1 + df["RA_over_RS"] ** gamma)


def error_summary(df, gamma):
    pred_win_pct = predict_win_pct(df, gamma)
    pred_wins = pred_win_pct * df["G"]

    win_pct_error = df["WinPct"] - pred_win_pct
    wins_error = df["W"] - pred_wins

    return {
        "gamma": gamma,

        # erros em winning percentage
        "mean_error_winpct": win_pct_error.mean(),
        "mae_winpct": win_pct_error.abs().mean(),
        "rmse_winpct": np.sqrt(np.mean(win_pct_error ** 2)),

        # erros em número de vitórias
        "mean_error_wins": wins_error.mean(),
        "mae_wins": wins_error.abs().mean(),
        "rmse_wins": np.sqrt(np.mean(wins_error ** 2)),
    }


def calculate_gamma(df):
    # Regressão linearizada pela origem: Y = gamma X
    gamma_linear = np.sum(df["X"] * df["Y"]) / np.sum(df["X"] ** 2)

    # Ajuste não linear direto em WinPct
    def sse(gamma):
        pred = predict_win_pct(df, gamma)
        return np.sum((df["WinPct"] - pred) ** 2)

    res = minimize_scalar(sse, bounds=(0.5, 3.0), method="bounded")
    gamma_nonlinear = res.x

    # Regressão linearizada com intercepto: Y = a + gamma X
    X = df["X"].to_numpy()
    Y = df["Y"].to_numpy()

    A = np.column_stack([np.ones_like(X), X])
    a_intercept, gamma_intercept = np.linalg.lstsq(A, Y, rcond=None)[0]

    return {
        "gamma_linear": gamma_linear,
        "gamma_nonlinear": gamma_nonlinear,
        "gamma_intercept": gamma_intercept,
        "a_intercept": a_intercept,
    }


def analyze_sample(df, label):
    gammas = calculate_gamma(df)

    print("=" * 80)
    print(label)
    print(f"n = {len(df)} team-seasons")
    print()
    print("Estimativas de gamma:")
    print(f"gamma_linear:     {gammas['gamma_linear']:.6f}")
    print(f"gamma_nonlinear:  {gammas['gamma_nonlinear']:.6f}")
    print(f"gamma_intercept:  {gammas['gamma_intercept']:.6f}")
    print(f"a_intercept:      {gammas['a_intercept']:.6f}")
    print()

    comparison_gammas = [
        2.0,
        1.83,
        gammas["gamma_nonlinear"],
    ]

    rows = []
    for gamma in comparison_gammas:
        rows.append(error_summary(df, gamma))

    errors = pd.DataFrame(rows)

    print("Comparação de erros:")
    print(
        errors[
            [
                "gamma",
                "mae_winpct",
                "rmse_winpct",
                "mae_wins",
                "rmse_wins",
                "mean_error_wins",
            ]
        ].to_string(index=False)
    )

    print()

    return gammas, errors

def compare_periods(df):
    rows = []

    for start in [1871, 1901, 1920, 1947, 1961, 1969, 1998, 2000]:
        gdf = df[df["yearID"] >= start]
        gammas = calculate_gamma(gdf)

        for gamma_name, gamma in [
            ("2.00", 2.0),
            ("1.83", 1.83),
            ("estimated", gammas["gamma_nonlinear"]),
        ]:
            err = error_summary(gdf, gamma)

            rows.append({
                "start": start,
                "model": gamma_name,
                "gamma": gamma,
                "mae_wins": err["mae_wins"],
                "rmse_wins": err["rmse_wins"],
                "mae_winpct": err["mae_winpct"],
                "rmse_winpct": err["rmse_winpct"],
            })

    return pd.DataFrame(rows)


def main():
    teams = pd.read_csv("Teams.csv")
    df = prepare_data(teams)

    all_results = []

    samples = [("geral", df)]

    for start in [1871, 1901, 1920, 1947, 1961, 1969, 1998, 2000]:
        samples.append((f"{start}+", df[df["yearID"] >= start]))

    for label, gdf in samples:
        gammas, errors = analyze_sample(gdf, label)

        row = {
            "sample": label,
            "n": len(gdf),
            **gammas,
        }

        for _, err in errors.iterrows():
            gamma_label = f"gamma_{err['gamma']:.6f}"
            row[f"{gamma_label}_mae_wins"] = err["mae_wins"]
            row[f"{gamma_label}_rmse_wins"] = err["rmse_wins"]
            row[f"{gamma_label}_mae_winpct"] = err["mae_winpct"]
            row[f"{gamma_label}_rmse_winpct"] = err["rmse_winpct"]

        all_results.append(row)

    summary = pd.DataFrame(all_results)

    print("=" * 80)
    print("Resumo das estimativas:")
    print(
        summary[
            [
                "sample",
                "n",
                "gamma_linear",
                "gamma_nonlinear",
                "gamma_intercept",
                "a_intercept",
            ]
        ].to_string(index=False)
    )
    print()
    print("Comparação das estimativas:")
    comparison = compare_periods(df)
    print(comparison.to_string(index=False))
    summary.to_csv("gamma_summary.csv", index=False)
    comparison.to_csv("gamma_error_comparison.csv", index=False)




main()
