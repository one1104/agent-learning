import check

test_file = "test_bad_code.py"
with open(test_file, "w", encoding="utf-8") as f:
    f.write("def foo():   \n")

issues = check.check_file(test_file)

if len(issues) >= 1:
    print("✅ smoke test 通过：正确查出了问题")
else:
    print("❌ smoke test 失败：没查出问题")
