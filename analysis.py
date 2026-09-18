import json
import math

import pandas as pd

CSV_PATH = "experiment_results.csv"


def load_data(path: str = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    assert df["user_id"].is_unique, "duplicate user_id found"
    assert df["converted"].isin([0, 1]).all()
    return df


def q1_naive_lift(df: pd.DataFrame):
    g = df.groupby("variant")["converted"].agg(["mean", "count"])
    lift_pp = (g.loc["treatment", "mean"] - g.loc["control", "mean"]) * 100
    return {
        "lift_pp": round(lift_pp, 4),
        "n_control": int(g.loc["control", "count"]),
        "n_treatment": int(g.loc["treatment", "count"]),
        "conv_control": round(g.loc["control", "mean"], 4),
        "conv_treatment": round(g.loc["treatment", "mean"], 4),
    }


def z_test(p1, n1, p2, n2):
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return (p2 - p1) / se if se > 0 else float("nan")


def q2_by_segment(df: pd.DataFrame):
    rows = []
    for seg, sub in df.groupby("segment"):
        c = sub[sub.variant == "control"]["converted"]
        t = sub[sub.variant == "treatment"]["converted"]
        z = z_test(c.mean(), len(c), t.mean(), len(t))
        rows.append(
            {
                "segment": seg,
                "n_control": len(c),
                "n_treatment": len(t),
                "conv_control": round(c.mean(), 4),
                "conv_treatment": round(t.mean(), 4),
                "lift_pp": round((t.mean() - c.mean()) * 100, 2),
                "z_score": round(z, 2),
            }
        )
    return sorted(rows, key=lambda r: -abs(r["lift_pp"]))


def q3_mix_adjusted_lift(df: pd.DataFrame):
    total_n = len(df)
    mix_adj = 0.0
    detail = []
    for seg, sub in df.groupby("segment"):
        c = sub[sub.variant == "control"]["converted"]
        t = sub[sub.variant == "treatment"]["converted"]
        lift = t.mean() - c.mean()
        weight = len(sub) / total_n
        mix_adj += lift * weight
        detail.append({"segment": seg, "weight": round(weight, 4), "lift_pp": round(lift * 100, 2)})
    return round(mix_adj * 100, 2), detail


def q5_assignment_ratios(df: pd.DataFrame):
    ratio = df.groupby("segment")["variant"].value_counts(normalize=True).unstack()
    return ratio.round(4)


def main():
    df = load_data()

    q1 = q1_naive_lift(df)
    print("Q1 - naive overall lift:", q1)

    q2 = q2_by_segment(df)
    print("\nQ2 - by segment:")
    for r in q2:
        print(" ", r)

    q3_val, q3_detail = q3_mix_adjusted_lift(df)
    print("\nQ3 - mix-adjusted lift (pp):", q3_val)
    for d in q3_detail:
        print(" ", d)

    print("\nQ5 - assignment ratio (fraction of segment in each variant):")
    print(q5_assignment_ratios(df))

    answers = {
        "q1_naive_lift_pp": float(q1["lift_pp"]),
        "q1_n_control": int(q1["n_control"]),
        "q1_n_treatment": int(q1["n_treatment"]),
        "q2_untrustworthy_segment": "influencer",
        "q3_mix_adjusted_lift_pp": float(q3_val),
        "q4_real_effect_segment": "app_store",
    }
    with open("answers.json", "w") as f:
        json.dump(answers, f, indent=2)
    print("\nWrote answers.json:", answers)


if __name__ == "__main__":
    main()
