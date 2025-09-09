#!/usr/bin/env python3
"""
Diagnostic logger for Joshua system health checks.
This module adds comprehensive logging to identify potential issues.
"""

import logging
import sys
import os
import platform
import importlib
import subprocess
from typing import Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/joshua_diagnostic.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class JoshuaDiagnostics:
    """Diagnostic tool for Joshua system validation."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_dependencies(self) -> Tuple[List[str], List[str]]:
        """Check if all required dependencies are installed."""
        logger.info("Checking dependencies...")
        
        required_modules = {
            'fdb': 'foundationdb',
            'boto3': 'boto3',
            'kubernetes': 'kubernetes', 
            'lxml': 'lxml',
            'dateutil': 'python-dateutil',
            'subprocess32': 'subprocess32'  # Python 2 only
        }
        
        missing = []
        installed = []
        
        for module, package in required_modules.items():
            try:
                importlib.import_module(module)
                installed.append(package)
                logger.debug(f"✓ {package} is installed")
            except ImportError:
                if module == 'subprocess32' and sys.version_info[0] >= 3:
                    logger.debug(f"✓ {package} not needed for Python 3+")
                else:
                    missing.append(package)
                    logger.warning(f"✗ {package} is missing")
                    
        return missing, installed
        
    def check_platform_compatibility(self) -> Dict[str, any]:
        """Check platform-specific compatibility."""
        logger.info("Checking platform compatibility...")
        
        platform_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python_version': sys.version,
            'is_linux': platform.system() == 'Linux'
        }
        
        logger.debug(f"Platform: {platform_info}")
        
        if not platform_info['is_linux']:
            self.warnings.append("Joshua agent requires Linux for full functionality")
            logger.warning("⚠ Non-Linux platform detected - some features may not work")
            
        # Check for /proc filesystem (Linux-specific)
        try:
            if os.path.exists('/proc'):
                logger.debug("✓ /proc filesystem available")
            else:
                self.issues.append("/proc filesystem not available")
                logger.error("✗ /proc filesystem not found - process management will fail")
        except Exception as e:
            logger.error(f"Error checking /proc: {e}")
            
        return platform_info
        
    def check_fdb_connection(self, cluster_file=None) -> bool:
        """Test FoundationDB connection."""
        logger.info("Checking FoundationDB connection...")
        
        try:
            import fdb
            fdb.api_version(630)
            db = fdb.open(cluster_file)
            
            # Try a simple read operation
            @fdb.transactional
            def test_read(tr):
                tr['test_key'].wait()
                return True
                
            test_read(db)
            logger.debug("✓ FoundationDB connection successful")
            return True
            
        except Exception as e:
            self.issues.append(f"FoundationDB connection failed: {e}")
            logger.error(f"✗ FoundationDB error: {e}")
            return False
            
    def check_childsubreaper(self) -> bool:
        """Check if childsubreaper module is available."""
        logger.info("Checking childsubreaper module...")
        
        try:
            import childsubreaper
            logger.debug("✓ childsubreaper module available")
            return True
        except ImportError:
            self.warnings.append("childsubreaper module not available - orphaned processes may occur")
            logger.warning("⚠ childsubreaper not installed")
            return False
            
    def check_docker_environment(self) -> Dict[str, any]:
        """Check if running in Docker environment."""
        logger.info("Checking Docker environment...")
        
        docker_info = {
            'in_docker': False,
            'in_kubernetes': False
        }
        
        # Check for Docker
        if os.path.exists('/.dockerenv'):
            docker_info['in_docker'] = True
            logger.debug("✓ Running in Docker container")
            
        # Check for Kubernetes
        if os.path.exists('/var/run/secrets/kubernetes.io'):
            docker_info['in_kubernetes'] = True
            logger.debug("✓ Running in Kubernetes pod")
            
        return docker_info
        
    def check_file_permissions(self, work_dir='/tmp/joshua_agent') -> bool:
        """Check file system permissions."""
        logger.info(f"Checking file permissions for {work_dir}...")
        
        try:
            # Try to create directory
            os.makedirs(work_dir, mode=0o755, exist_ok=True)
            
            # Try to write a file
            test_file = os.path.join(work_dir, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            logger.debug(f"✓ Write permissions OK for {work_dir}")
            return True
            
        except Exception as e:
            self.issues.append(f"File permission error: {e}")
            logger.error(f"✗ Permission error: {e}")
            return False
            
    def run_full_diagnostic(self, cluster_file=None) -> Dict[str, any]:
        """Run complete diagnostic check."""
        logger.info("=" * 60)
        logger.info("Starting Joshua System Diagnostics")
        logger.info("=" * 60)
        
        results = {
            'dependencies': {},
            'platform': {},
            'fdb_connection': False,
            'childsubreaper': False,
            'docker': {},
            'file_permissions': False,
            'issues': [],
            'warnings': []
        }
        
        # Run all checks
        missing_deps, installed_deps = self.check_dependencies()
        results['dependencies'] = {
            'missing': missing_deps,
            'installed': installed_deps
        }
        
        results['platform'] = self.check_platform_compatibility()
        results['fdb_connection'] = self.check_fdb_connection(cluster_file)
        results['childsubreaper'] = self.check_childsubreaper()
        results['docker'] = self.check_docker_environment()
        results['file_permissions'] = self.check_file_permissions()
        
        results['issues'] = self.issues
        results['warnings'] = self.warnings
        
        # Summary
        logger.info("=" * 60)
        logger.info("Diagnostic Summary")
        logger.info("=" * 60)
        
        if self.issues:
            logger.error(f"Found {len(self.issues)} critical issues:")
            for issue in self.issues:
                logger.error(f"  - {issue}")
        else:
            logger.info("✓ No critical issues found")
            
        if self.warnings:
            logger.warning(f"Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
                
        return results
        

def main():
    """Main entry point for diagnostic tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Joshua System Diagnostics")
    parser.add_argument('-C', '--cluster-file', help='FoundationDB cluster file')
    args = parser.parse_args()
    
    diagnostics = JoshuaDiagnostics()
    results = diagnostics.run_full_diagnostic(args.cluster_file)
    
    # Exit with error code if issues found
    if results['issues']:
        sys.exit(1)
    else:
        sys.exit(0)
        

if __name__ == '__main__':
    main()