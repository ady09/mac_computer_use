#!/usr/bin/env python3
"""
Debug test runner with verbose output using modular components
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.test_runner_modular import ModularTestRunner


class DebugModularTestRunner(ModularTestRunner):
    """Test runner with enhanced debugging using modular components"""
    
    async def run_test(self, test_file_path: str):
        """Run test with detailed debugging output"""
        print("="*80)
        print(f"🐛 DEBUG MODE: Running modular test {test_file_path}")
        print("="*80)
        
        result = await super().run_test(test_file_path)
        
        print("="*80)
        print(f"🐛 DEBUG SUMMARY for {result.test_name}")
        print(f"Status: {result.status}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Steps: {result.total_steps}")
        print(f"Passed: {result.passed_steps}")
        print(f"Failed: {result.failed_steps}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        print("\\n📝 Step-by-step breakdown:")
        for i, step in enumerate(result.step_results, 1):
            status_emoji = "✅" if step.status == "passed" else "❌"
            print(f"{status_emoji} Step {i}: {step.step_name}")
            print(f"   Action: {step.action}")
            print(f"   Duration: {step.duration:.2f}s")
            if step.error_message:
                print(f"   ❌ Error: {step.error_message}")
            if step.output:
                print(f"   📤 Output: {step.output}")
            print()
        
        print("="*80)
        return result


async def run_orcasheets_debug():
    """Run OrcaSheets search projects test with debug output using modular runner"""
    
    # Initialize debug test runner
    script_dir = Path(__file__).parent
    tests_dir = script_dir.parent / "tests"
    runner = DebugModularTestRunner(str(tests_dir))
    
    # Test file path
    test_file = tests_dir / "projects" / "orcasheets" / "search_projects.json"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"🚀 Running OrcaSheets search projects test with modular debugging...")
    print(f"📁 Test file: {test_file}")
    
    try:
        # Run the test
        result = await runner.run_test(str(test_file))
        
        # Generate report
        report_path = runner.generate_report([result])
        print(f"\\n📄 Report generated: {report_path}")
        
        # Try to open report
        if sys.platform == "darwin":
            os.system(f"open '{report_path}'")
        
        return result.status == "passed"
        
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("🐛 OrcaSheets Modular Debug Test Runner")
    print("This will run the search projects test with detailed debugging output using modular components")
    print()
    
    success = asyncio.run(run_orcasheets_debug())
    
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())