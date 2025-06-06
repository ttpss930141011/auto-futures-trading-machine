#!/usr/bin/env python
"""Integration test for Gateway-enabled AllInOneController.

This script tests the complete integration of the DLL Gateway architecture
with the AllInOneController to ensure everything works seamlessly.
"""

import sys
import time
import subprocess
import signal
from pathlib import Path

# Ensure the project root is in the path
sys.path.append(str(Path(__file__).resolve().parent))

from src.infrastructure.services.dll_gateway_client import DllGatewayClient
from src.infrastructure.loggers.logger_default import LoggerDefault


class GatewayIntegrationTest:
    """Integration test for Gateway architecture."""

    def __init__(self):
        self.logger = LoggerDefault()
        self.main_process = None
        self.test_results = []

    def run_tests(self):
        """Run comprehensive integration tests."""
        print("="*60)
        print("Gateway Integration Test Suite")
        print("="*60)
        
        try:
            # Test 1: Start main application with Gateway
            self.test_main_application_startup()
            
            # Test 2: Test Gateway connectivity
            self.test_gateway_connectivity()
            
            # Test 3: Test Gateway health check
            self.test_gateway_health_check()
            
            # Print results
            self.print_test_results()
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        finally:
            self.cleanup()

    def test_main_application_startup(self):
        """Test that main application starts with Gateway."""
        print("\n1. Testing main application startup with Gateway...")
        
        try:
            # Start main application in subprocess
            self.main_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it time to start
            time.sleep(3)
            
            # Check if process is still running
            if self.main_process.poll() is None:
                self.test_results.append("✓ Main application started successfully")
                return True
            else:
                stdout, stderr = self.main_process.communicate()
                self.test_results.append(f"✗ Main application failed to start")
                self.test_results.append(f"   Error: {stderr}")
                return False
                
        except Exception as e:
            self.test_results.append(f"✗ Error starting main application: {e}")
            return False

    def test_gateway_connectivity(self):
        """Test Gateway connectivity."""
        print("2. Testing Gateway connectivity...")
        
        try:
            # Get configuration
            from src.app.cli_pfcf.config import Config
            config = Config(None)  # We don't need exchange_api for getting addresses
            
            # Create Gateway client
            client = DllGatewayClient(
                server_address=config.DLL_GATEWAY_CONNECT_ADDRESS,
                logger=self.logger,
                timeout_ms=3000,
                retry_count=1
            )
            
            # Test connectivity with health check
            health_status = client.get_health_status()
            
            if health_status.get("status") == "healthy":
                self.test_results.append("✓ Gateway connectivity successful")
                client.close()
                return True
            else:
                self.test_results.append(f"✗ Gateway unhealthy: {health_status}")
                client.close()
                return False
                
        except Exception as e:
            self.test_results.append(f"✗ Gateway connectivity failed: {e}")
            return False

    def test_gateway_health_check(self):
        """Test Gateway health check functionality."""
        print("3. Testing Gateway health check...")
        
        try:
            # Get configuration
            from src.app.cli_pfcf.config import Config
            config = Config(None)  # We don't need exchange_api for getting addresses
            
            client = DllGatewayClient(
                server_address=config.DLL_GATEWAY_CONNECT_ADDRESS,
                logger=self.logger,
                timeout_ms=3000,
                retry_count=1
            )
            
            # Test multiple health checks
            for i in range(3):
                health_status = client.get_health_status()
                if "status" not in health_status:
                    self.test_results.append(f"✗ Health check {i+1} failed")
                    client.close()
                    return False
                    
                time.sleep(0.5)
            
            self.test_results.append("✓ Gateway health checks successful")
            client.close()
            return True
            
        except Exception as e:
            self.test_results.append(f"✗ Gateway health check failed: {e}")
            return False

    def print_test_results(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("Test Results Summary")
        print("="*60)
        
        for result in self.test_results:
            print(result)
            
        # Count successes and failures
        successes = sum(1 for result in self.test_results if result.startswith("✓"))
        failures = sum(1 for result in self.test_results if result.startswith("✗"))
        
        print(f"\nTotal: {successes + failures} tests")
        print(f"Passed: {successes}")
        print(f"Failed: {failures}")
        
        if failures == 0:
            print("\n🎉 All tests passed! Gateway integration is working correctly.")
            print("\nYou can now use:")
            print("1. python app.py - Main application with integrated Gateway")
            print("2. Option 10 in the menu - AllInOneController with Gateway support")
        else:
            print("\n❌ Some tests failed. Please check the error messages above.")

    def cleanup(self):
        """Clean up test processes."""
        print("\nCleaning up test processes...")
        
        if self.main_process and self.main_process.poll() is None:
            try:
                # Send SIGINT (Ctrl+C) first for graceful shutdown
                self.main_process.send_signal(signal.SIGINT)
                
                # Wait for graceful shutdown
                try:
                    self.main_process.wait(timeout=5)
                    print("Main application shut down gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.main_process.kill()
                    print("Main application force killed")
                    
            except Exception as e:
                print(f"Error during cleanup: {e}")


def main():
    """Run the integration test."""
    test = GatewayIntegrationTest()
    test.run_tests()


if __name__ == "__main__":
    main()