
import subprocess
import json
import re

def check_software_updates():
    try:
        # Run softwareupdate to check for updates
        result = subprocess.run(['softwareupdate', '--list'], 
                                capture_output=True, text=True, check=True)
        
        # Parse the output
        updates = []
        security_updates = []
        
        for line in result.stdout.splitlines():
            if "recommended" in line.lower():
                update_name = line.strip()
                updates.append(update_name)
                
                # Check if it's a security update
                if "security" in line.lower():
                    security_updates.append(update_name)
        
        return {
            "tool": "update_checker",
            "check_name": "Software Update Status",
            "updates_available": len(updates) > 0,
            "security_updates": len(security_updates) > 0,
            "total_updates": len(updates),
            "security_update_count": len(security_updates),
            "update_list": updates,
            "security_update_list": security_updates,
            "secure": len(security_updates) == 0,
            "recommendation": "Install pending security updates" if security_updates else None
        }
    
    except Exception as e:
        return {
            "tool": "update_checker",
            "check_name": "Software Update Status",
            "error": str(e),
            "secure": False,
            "recommendation": "Unable to check for updates. Ensure you have an internet connection."
        }

if __name__ == "__main__":
    result = check_software_updates()
    print(json.dumps(result, indent=4))