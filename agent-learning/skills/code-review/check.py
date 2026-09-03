import sys


def check_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    issues = []
    for i, line in enumerate(lines, start=1):
        if line.rstrip("\n").endswith(" "):
            issues.append(f"第{i}行：行尾有多余空格")

        if len(line.rstrip("\n")) > 100:
            issues.append(f"第{i}行：超过100字符")

    return issues


if __name__ == "__main__":
    path = sys.argv[1]
    issues = check_file(path)
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("未发现问题")
