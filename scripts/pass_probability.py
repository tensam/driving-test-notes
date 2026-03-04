#!/usr/bin/env python3
"""
驾考通过概率预测脚本

=== 使用说明 ===
1. 每次做完模拟考试后，在下面的 TEST_ERRORS 列表末尾追加一个数字
   数字 = 该次模拟考试答错的题数（满分30题）
2. 运行: python3 scripts/pass_probability.py
3. 查看预测结果

例如做了第3次模拟考，错了2题:
  TEST_ERRORS = [7, 4, 2]   # ← 在末尾加上 2

注意：只统计完整的30题模拟考试，散题练习不算在内。
"""

import numpy as np
from scipy import stats
from scipy.special import comb as ncomb

# ============================================================
# >>> 在这里更新你的模拟考试错题数 <<<
# 每个数字 = 一次完整模拟考试（30题）中答错的题数
# ============================================================
TEST_ERRORS = [7, 4, 2]
# ============================================================

TOTAL_QUESTIONS = 30
MAX_ERRORS_TO_PASS = 3


def bayesian_analysis(errors, n_questions=TOTAL_QUESTIONS, max_wrong=MAX_ERRORS_TO_PASS):
    total_questions_seen = len(errors) * n_questions
    total_wrong = sum(errors)
    total_right = total_questions_seen - total_wrong

    alpha_prior, beta_prior = 1, 1
    alpha_post = alpha_prior + total_wrong
    beta_post = beta_prior + total_right

    posterior = stats.beta(alpha_post, beta_post)
    p_mean = posterior.mean()
    p_median = posterior.median()
    ci_low, ci_high = posterior.ppf(0.025), posterior.ppf(0.975)

    n_grid = 5000
    p_grid = np.linspace(1e-8, 1 - 1e-8, n_grid)
    posterior_pdf = posterior.pdf(p_grid)
    posterior_pdf /= np.trapezoid(posterior_pdf, p_grid)

    pass_prob_given_p = np.zeros_like(p_grid)
    for k in range(max_wrong + 1):
        pass_prob_given_p += ncomb(n_questions, k, exact=False) * \
            p_grid**k * (1 - p_grid)**(n_questions - k)

    pass_prob = np.trapezoid(pass_prob_given_p * posterior_pdf, p_grid)

    return {
        "alpha": alpha_post,
        "beta": beta_post,
        "p_mean": p_mean,
        "p_median": p_median,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "pass_prob": pass_prob,
    }


def frequentist_analysis(errors, n_questions=TOTAL_QUESTIONS, max_wrong=MAX_ERRORS_TO_PASS):
    n_tests = len(errors)
    err_array = np.array(errors, dtype=float)
    mean_errors = err_array.mean()
    std_errors = err_array.std(ddof=1) if n_tests > 1 else err_array.mean() * 0.5
    se = std_errors / np.sqrt(n_tests)

    p_hat = mean_errors / n_questions
    p_ci_low = max(0, p_hat - stats.t.ppf(0.975, df=max(n_tests - 1, 1)) * se / n_questions)
    p_ci_high = min(1, p_hat + stats.t.ppf(0.975, df=max(n_tests - 1, 1)) * se / n_questions)

    if n_tests >= 5:
        z = (max_wrong + 0.5 - mean_errors) / std_errors if std_errors > 0 else float('inf')
        pass_prob = stats.norm.cdf(z)
        method = "正态近似"
    elif n_tests >= 2:
        t_val = (max_wrong + 0.5 - mean_errors) / std_errors if std_errors > 0 else float('inf')
        pass_prob = stats.t.cdf(t_val, df=n_tests - 1)
        method = f"t分布 (df={n_tests - 1})"
    else:
        pass_prob = 1.0 if mean_errors <= max_wrong else 0.0
        method = "样本不足，仅供参考"

    return {
        "mean_errors": mean_errors,
        "std_errors": std_errors,
        "p_hat": p_hat,
        "p_ci_low": p_ci_low,
        "p_ci_high": p_ci_high,
        "pass_prob": pass_prob,
        "method": method,
        "n_tests": n_tests,
    }


def trend_analysis(errors):
    n = len(errors)
    if n < 2:
        return "数据不足", 0.0
    if n == 2:
        diff = errors[-1] - errors[-2]
        if diff < -1:
            return "改善中", diff
        elif diff > 1:
            return "退步中", diff
        else:
            return "基本稳定", diff
    x = np.arange(n, dtype=float)
    slope, _, r, p_val, _ = stats.linregress(x, errors)
    if p_val > 0.1:
        return "基本稳定（趋势不显著）", slope
    elif slope < -0.3:
        return "明显改善", slope
    elif slope < 0:
        return "略有改善", slope
    elif slope > 0.3:
        return "明显退步", slope
    else:
        return "略有退步", slope


def main():
    if not TEST_ERRORS:
        print("暂无模拟考试数据，请在脚本顶部 TEST_ERRORS 列表中添加数据。")
        return

    n_tests = len(TEST_ERRORS)
    print("=" * 56)
    print("         西班牙驾照考试 — 通过概率预测")
    print("=" * 56)
    print(f"\n考试规则: {TOTAL_QUESTIONS}题, 最多错{MAX_ERRORS_TO_PASS}题通过")
    print(f"已完成模拟考: {n_tests}次")
    print(f"错题记录: {TEST_ERRORS}")
    print(f"平均错题: {np.mean(TEST_ERRORS):.1f} / {TOTAL_QUESTIONS}")

    print("\n" + "-" * 56)
    print("【贝叶斯分析】（后验预测概率）")
    print("-" * 56)
    bayes = bayesian_analysis(TEST_ERRORS)
    print(f"  每题错误率估计: {bayes['p_mean']:.1%}")
    print(f"  95% 可信区间:   [{bayes['ci_low']:.1%}, {bayes['ci_high']:.1%}]")
    print(f"  后验分布参数:   Beta({bayes['alpha']}, {bayes['beta']})")
    print(f"  ★ 预测通过概率: {bayes['pass_prob']:.1%}")

    print("\n" + "-" * 56)
    print("【频率学派分析】")
    print("-" * 56)
    freq = frequentist_analysis(TEST_ERRORS)
    print(f"  平均错题数:     {freq['mean_errors']:.1f} ± {freq['std_errors']:.1f}")
    print(f"  每题错误率:     {freq['p_hat']:.1%}  [{freq['p_ci_low']:.1%}, {freq['p_ci_high']:.1%}]")
    print(f"  估计方法:       {freq['method']}")
    print(f"  ★ 预测通过概率: {freq['pass_prob']:.1%}")

    print("\n" + "-" * 56)
    print("【趋势与建议】")
    print("-" * 56)
    trend_label, slope = trend_analysis(TEST_ERRORS)
    print(f"  趋势判断: {trend_label}", end="")
    if n_tests >= 2:
        print(f"  (斜率: {slope:+.1f}题/次)")
    else:
        print()

    avg_errors = np.mean(TEST_ERRORS)
    gap = avg_errors - MAX_ERRORS_TO_PASS
    if gap > 0:
        print(f"  还需平均多对: {gap:.1f} 题才能达到及格线")
        target_rate = MAX_ERRORS_TO_PASS / TOTAL_QUESTIONS
        print(f"  目标错误率:   ≤ {target_rate:.1%} (当前 {bayes['p_mean']:.1%})")
    else:
        print(f"  当前水平已达及格线以上 (+{-gap:.1f}题余量)")

    print("\n" + "-" * 56)
    print("【结论】")
    print("-" * 56)
    combined = (bayes['pass_prob'] + freq['pass_prob']) / 2
    if combined >= 0.8:
        verdict = "状态良好，通过概率较高。保持练习节奏。"
    elif combined >= 0.5:
        verdict = "有一定通过可能，但仍需加强薄弱环节。"
    elif combined >= 0.2:
        verdict = "通过概率偏低，建议继续练习，重点复习错题类型。"
    else:
        verdict = "目前通过概率较低，建议系统复习后再考。"
    print(f"  综合通过概率: {combined:.1%}")
    print(f"  评估: {verdict}")

    if n_tests < 5:
        print(f"\n  ⚠ 注意: 目前仅有{n_tests}次模拟数据，样本较少，预测置信度有限。")
        print(f"    建议至少完成5次模拟考试以获得更可靠的预测。")

    print("\n" + "=" * 56)


if __name__ == "__main__":
    main()
