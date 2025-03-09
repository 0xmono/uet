import unittest
from build_config import BuildConfig
from argparse import Namespace
import copy

class TestBuildConfig(unittest.TestCase):
    def setUp(self):
        # Create a base args object that can be modified for different tests
        self.base_args = Namespace(
            source="test/path",
            shellsource="shell/path",
            target="Editor",
            config="Development",
            platform="Win64",
            definitions=["TEST_DEF=1", "DEBUG=1"],
            nonUnity=False,
            noPrecompiledHeaders=False,
            onlyDebug=False
        )

    def test_default_values(self):
        # Test creation with minimal args
        args = copy.deepcopy(self.base_args)
        
        config = BuildConfig.from_args(args)
        
        self.assertEqual(config.source_path, "test/path")
        self.assertEqual(config.target, "Editor")
        self.assertEqual(config.config, "Development")
        self.assertEqual(config.platform, "Win64")
        self.assertEqual(config.definitions, ["TEST_DEF=1", "DEBUG=1"])
        self.assertFalse(config.non_unity)
        self.assertFalse(config.no_precompiled_headers)
        self.assertFalse(config.debug_only)

    def test_shellsource_fallback(self):
        # Test that shellsource is used when source is None
        args = copy.deepcopy(self.base_args)
        args.source = None
        
        config = BuildConfig.from_args(args)
        self.assertEqual(config.source_path, "shell/path")
        
    def test_build_flags(self):
        # Test build flags
        args = copy.deepcopy(self.base_args)
        args.nonUnity = True
        args.noPrecompiledHeaders = True
        args.onlyDebug = True
        
        config = BuildConfig.from_args(args)
        self.assertTrue(config.non_unity)
        self.assertTrue(config.no_precompiled_headers)
        self.assertTrue(config.debug_only)
        
    def test_multiple_targets_configs_platforms(self):
        # Test with multiple values for target, config, platform
        args = copy.deepcopy(self.base_args)
        args.target = ["Editor", "Game"]
        args.config = ["Development", "Shipping"]
        args.platform = ["Win64", "Linux"]
        
        config = BuildConfig.from_args(args)
        self.assertEqual(config.target, ["Editor", "Game"])
        self.assertEqual(config.config, ["Development", "Shipping"])
        self.assertEqual(config.platform, ["Win64", "Linux"]) 