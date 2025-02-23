from dataclasses import dataclass
from typing import List, Optional

@dataclass
class BuildConfig:
    """Configuration for UE project builds"""
    source_path: str
    target: str = "Editor"
    config: str = "Development" 
    platform: str = "Win64"
    definitions: Optional[List[str]] = None
    non_unity: bool = False
    no_precompiled_headers: bool = False
    debug_only: bool = False
    
    @classmethod
    def from_args(cls, args):
        """Create config from parsed command line arguments"""
        return cls(
            source_path=args.source or args.shellsource,
            target=args.target,
            config=args.config,
            platform=args.platform,
            definitions=args.definitions,
            non_unity=args.nonUnity,
            no_precompiled_headers=args.noPrecompiledHeaders,
            debug_only=args.onlyDebug
        ) 