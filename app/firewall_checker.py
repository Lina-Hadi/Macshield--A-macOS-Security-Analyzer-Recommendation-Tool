import subprocess
import json
import re

def check_firewall():
    try:
        # Run command to get firewall status
        result = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getglobalstate'], 
                               capture_output=True, text=True, check=True)
        
        # Parse the output
        enabled = "enabled" in result.stdout.lower()
        
        # Get stealth mode status
        stealth = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getstealthmode'], 
                                capture_output=True, text=True, check=True)
        stealth_enabled = "enabled" in stealth.stdout.lower()
        
        # Get application blocking status
        blocking = subprocess.run(['/usr/libexec/ApplicationFirewall/socketfilterfw', '--getblockall'], 
                                 capture_output=True, text=True, check=True)
        block_all = "enabled" in blocking.stdout.lower()
        
        # Calculate security score
        security_score = 0
        if enabled:
            security_score += 50
        if stealth_enabled:
            security_score += 25
        if block_all:
            security_score += 25
        
        # Generate recommendations
        recommendations = []
        if not enabled:
            recommendations.append("Enable the macOS firewall")
        if not stealth_enabled:
            recommendations.append("Enable stealth mode to prevent response to network discovery attempts")
        if not block_all:
            recommendations.append("Consider enabling 'Block all incoming connections' for maximum security")
        
        return {
            "tool": "firewall_checker",
            "check_name": "Firewall Configuration",
            "firewall_enabled": enabled,
            "stealth_mode": stealth_enabled,
            "block_all_connections": block_all,
            "security_score": security_score,
            "secure": enabled and stealth_enabled,
            "recommendations": recommendations
        }
    
    except Exception as e:
        return {
            "tool": "firewall_checker",
            "check_name": "Firewall Configuration",
            "error": str(e),
            "secure": False,
            "recommendations": ["Ensure you have administrative access to check firewall settings"]
        }

if __name__ == "__main__":
    result = check_firewall()
    print(json.dumps(result, indent=4))