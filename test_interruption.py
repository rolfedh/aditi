#!/usr/bin/env python3
"""Test script to verify interruption handling works correctly."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

def test_interruption():
    """Test that Ctrl+C handling works during aditi operations."""
    
    # Create a large test file to ensure processing takes some time
    test_dir = Path("test-interruption")
    test_dir.mkdir(exist_ok=True)
    
    # Create multiple large test files  
    for i in range(5):
        test_file = test_dir / f"large_test_{i}.adoc"
        content = """= Large Test Document

This is a test document with lots of content to make processing take time.

""" + "\n".join([f"== Section {j}\n\nContent for section {j} with some text.\n" for j in range(50)])
        
        test_file.write_text(content)
    
    print(f"Created test files in {test_dir}")
    
    # Test 1: Start aditi check and interrupt it
    print("\n🧪 Test 1: Testing interruption during check command...")
    
    try:
        # Start the aditi process
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/rolfedh/aditi/src'
        
        process = subprocess.Popen([
            'python', '-c', 
            "import sys; sys.path.insert(0, '/home/rolfedh/aditi/src'); from aditi.cli import app; app()",
            'check', str(test_dir)
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Let it run for a moment
        time.sleep(2)
        
        # Send SIGINT (Ctrl+C)
        print("Sending SIGINT (Ctrl+C)...")
        process.send_signal(signal.SIGINT)
        
        # Wait for process to complete
        stdout, stderr = process.communicate(timeout=10)
        
        print(f"Process exit code: {process.returncode}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        
        if process.returncode != 0:
            print("✅ Process was successfully interrupted")
        else:
            print("❌ Process was not interrupted as expected")
            
    except subprocess.TimeoutExpired:
        print("❌ Process did not terminate after interrupt")
        process.kill()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    print(f"Cleaned up {test_dir}")

if __name__ == "__main__":
    test_interruption()