#!/usr/bin/env python3
"""
Direct test runner for debugging and standalone execution
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.test_runner import TestRunner


async def run_spotify_test(test_name: str = "play_music"):
    """Run a specific Spotify test"""
    
    # Initialize test runner
    script_dir = Path(__file__).parent
    tests_dir = script_dir.parent / "tests"
    runner = TestRunner(str(tests_dir))
    
    # Test file path
    test_file = tests_dir / "projects" / "spotify" / f"{test_name}.json"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        available_tests = list((tests_dir / "projects" / "spotify").glob("*.json"))
        print("Available tests:")
        for test in available_tests:
            print(f"  - {test.stem}")
        return False
    
    print(f"🚀 Running Spotify test: {test_name}")
    print(f"📁 Test file: {test_file}")
    print("-" * 50)
    
    try:
        # Run the test
        result = await runner.run_test(str(test_file))
        
        # Print results
        print(f"\n📊 Test Results:")
        print(f"Test Name: {result.test_name}")
        print(f"Status: {result.status}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Steps: {result.total_steps}")
        print(f"Passed: {result.passed_steps}")
        print(f"Failed: {result.failed_steps}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        # Print step details
        print(f"\n📝 Step Details:")
        for i, step in enumerate(result.step_results, 1):
            status_emoji = "✅" if step.status == "passed" else "❌"
            print(f"{status_emoji} Step {i}: {step.step_name} ({step.duration:.2f}s)")
            if step.error_message:
                print(f"   Error: {step.error_message}")
        
        # Generate report
        report_path = runner.generate_report([result])
        print(f"\n📄 Report generated: {report_path}")
        
        # Try to open report
        if sys.platform == "darwin":
            os.system(f"open '{report_path}'")
        
        return result.status == "passed"
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_spotify_tests():
    """Run all Spotify tests"""
    script_dir = Path(__file__).parent
    tests_dir = script_dir.parent / "tests" / "projects" / "spotify"
    
    if not tests_dir.exists():
        print("❌ Spotify tests directory not found")
        return False
    
    test_files = list(tests_dir.glob("*.json"))
    
    if not test_files:
        print("❌ No Spotify test files found")
        return False
    
    print(f"🚀 Running {len(test_files)} Spotify tests")
    print("-" * 50)
    
    results = []
    for test_file in test_files:
        test_name = test_file.stem
        print(f"\n▶️ Running: {test_name}")
        success = await run_spotify_test(test_name)
        results.append((test_name, success))
        
        # Reduced wait between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print(f"\n📊 Overall Results:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nSummary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return passed == total


def main():
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "all":
            success = asyncio.run(run_all_spotify_tests())
        else:
            success = asyncio.run(run_spotify_test(test_name))
    else:
        print("Usage:")
        print("  python test_runner_direct.py play_music")
        print("  python test_runner_direct.py create_playlist")
        print("  python test_runner_direct.py shuffle_play")
        print("  python test_runner_direct.py search_artist")
        print("  python test_runner_direct.py all")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())