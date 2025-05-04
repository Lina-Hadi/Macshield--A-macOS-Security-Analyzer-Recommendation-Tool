import subprocess

def run_lynis_scan():
    try:
        # Run the Lynis scan command
        result = subprocess.run(['sudo', 'lynis', 'audit', 'system'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + "\n" + result.stderr
        return output
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    output = run_lynis_scan()
    print(output)
