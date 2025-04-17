import subprocess

def count_failed_logins():
    result = subprocess.run(
        ["log", "show", "--predicate", 'eventMessage CONTAINS[c] "login" AND eventMessage CONTAINS[c] "failed"', "--last", "1d"],
        capture_output=True, text=True
    )

    lines = result.stdout.splitlines()
    failed_lines = [line for line in lines if "failed" in line.lower()]
    return len(failed_lines)

result = count_failed_logins()
print(result)