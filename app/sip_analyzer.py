import subprocess
import json

def check_sip_status():
    try:
        # Run csrutil to check SIP status
        result = subprocess.run(['csrutil', 'status'], 
                               capture_output=True, text=True, check=True)
        
        # Parse the output
        if "enabled" in result.stdout.lower():
            status = "enabled"
            secure = True
        else:
            status = "disabled"
            secure = False
            
        # Return structured data
        return {
            "tool": "sip_analyzer",
            "check_name": "System Integrity Protection",
            "status": status,
            "secure": secure,
            "raw_output": result.stdout,
            "recommendation": "Enable System Integrity Protection for enhanced security" if not secure else None
        }
    except Exception as e:
        return {
            "tool": "sip_analyzer",
            "check_name": "System Integrity Protection",
            "status": "error",
            "secure": False,
            "error": str(e),
            "recommendation": "Run the tool with administrator privileges"
        }

if __name__ == "__main__":
    result = check_sip_status()
    # Ajout de cette ligne pour afficher le résultat
    print(json.dumps(result, indent=4))