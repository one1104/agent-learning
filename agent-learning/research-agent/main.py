# -*- coding: utf-8 -*-
from agents import researcher, writer, reviewer


def research_report(question, max_revise=3):
    key_points = researcher(question)
    report = writer(question, key_points)

    for round_num in range(max_revise):
        score = int(reviewer(report).strip())
        print(f"第 {round_num + 1} 轮评分：{score} 分")

        if score >= 8:
            return report

        report = writer(question, key_points + f"\n\n（上次评分 {score} 分，请改进）")

    return report


if __name__ == "__main__":
    question = input("请输入研究主题：").strip() or "AI 对就业市场有什么影响？"
    report = research_report(question)
    print("\n" + "=" * 50)
    print(report)