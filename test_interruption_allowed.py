#!/usr/bin/env python3
"""Test script to verify interruption handling works correctly with allowed paths."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

def test_interruption():
    """Test that Ctrl+C handling works during aditi operations."""
    
    # Use the test-repo directory which is already allowed
    test_dir = Path("/home/rolfedh/aditi/test-repo")
    
    # Create a large test file to ensure processing takes some time
    large_test_file = test_dir / "large_interruption_test.adoc" 
    content = """= Large Test Document for Interruption Testing

This is a test document with lots of content to make processing take time.

""" + "\n".join([f"== Section {j}\n\nContent for section {j} with some text that might trigger Vale rules like &amp; and other entities{{nbsp}}.\n\n=== Subsection {j}.1\n\nMore content here to trigger NestedSection rules.\n" for j in range(100)])
        
    large_test_file.write_text(content)
    
    print(f"Created large test file: {large_test_file}")
    
    # Test 1: Start aditi check and interrupt it
    print("\n🧪 Test 1: Testing interruption during check command with large file...")
    
    try:
        # Start the aditi process
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/rolfedh/aditi/src'
        
        process = subprocess.Popen([
            'python', '-c', 
            "import sys; sys.path.insert(0, '/home/rolfedh/aditi/src'); from aditi.cli import app; app()",
            'check', str(large_test_file)
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it run for a moment to start processing
        time.sleep(3)
        
        # Send SIGINT (Ctrl+C)
        print("Sending SIGINT (Ctrl+C)...")
        process.send_signal(signal.SIGINT)
        
        # Wait for process to complete
        stdout, stderr = process.communicate(timeout=15)
        
        print(f"Process exit code: {process.returncode}")
        print("--- Stdout ---")
        print(stdout[-500:] if len(stdout) > 500 else stdout)  # Show last 500 chars
        print("--- Stderr ---") 
        print(stderr[-200:] if len(stderr) > 200 else stderr)  # Show last 200 chars
        
        # Check if we see graceful shutdown messages
        if "interrupted" in stdout.lower() or "interrupted" in stderr.lower():
            print("✅ Process showed graceful interruption handling")
        elif process.returncode != 0:
            print("✅ Process was successfully interrupted (exit code != 0)")
        else:
            print("❌ Process completed normally - interruption may not have worked")
            
    except subprocess.TimeoutExpired:
        print("❌ Process did not terminate after interrupt within timeout")
        process.kill()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Cleanup
        if large_test_file.exists():
            large_test_file.unlink()
            print(f"Cleaned up {large_test_file}")

if __name__ == "__main__":
    test_interruption()