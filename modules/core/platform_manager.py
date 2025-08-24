#!/usr/bin/env python3
"""
Platform Manager Module
Enhanced 12+ platform detection and optimization
"""

import os
import sys
import subprocess
import platform
import json
import psutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

class PlatformManager:
    """Advanced platform detection and management"""
    
    PLATFORM_SIGNATURES = {
        'colab': {
            'paths': ['/content'],
            'env_vars': ['COLAB_GPU'],
            'commands': ['nvidia-smi'],
            'root': '/content'
        },
        'kaggle': {
            'paths': ['/kaggle'],
            'env_vars': ['KAGGLE_KERNEL_RUN_TYPE'],
            'root': '/kaggle/working'
        },
        'lightning': {
            'env_vars': ['LIGHTNING_CLOUD_PROJECT_ID', 'LIGHTNING_CLOUD_URL'],
            'root': str(Path.home() / 'work')
        },
        'paperspace': {
            'env_vars': ['PAPERSPACE_GRADIENT_ID', 'PS_API_KEY'],
            'paths': ['/notebooks'],
            'root': '/notebooks'
        },
        'runpod': {
            'env_vars': ['RUNPOD_POD_ID', 'RUNPOD_API_KEY'],
            'paths': ['/workspace'],
            'root': '/workspace'
        },
        'vast': {
            'env_vars': ['VAST_CONTAINERLABEL'],
            'paths': ['/workspace'],
            'root': '/workspace'
        },
        'sagemaker': {
            'env_vars': ['SAGEMAKER_INTERNAL_IMAGE_URI', 'SM_CHANNEL_TRAINING'],
            'root': '/opt/ml/code'
        },
        'azure': {
            'env_vars': ['AZURE_BATCH_POOL_ID', 'AZUREML_RUN_ID'],
            'root': '/mnt/batch/tasks/shared/LS_root'
        },
        'gcp': {
            'env_vars': ['GCP_PROJECT', 'GOOGLE_CLOUD_PROJECT'],
            'paths': ['/home/jupyter'],
            'root': '/home/jupyter'
        },
        'lambda': {
            'env_vars': ['LAMBDA_CLOUD', 'LAMBDA_INSTANCE_TYPE'],
            'paths': ['/home/ubuntu'],
            'root': '/home/ubuntu'
        },
        'modal': {
            'env_vars': ['MODAL_ENVIRONMENT', 'MODAL_TASK_ID'],
            'root': '/root'
        },
        'replicate': {
            'env_vars': ['REPLICATE_API_TOKEN', 'REPLICATE_VERSION'],
            'root': '/src'
        }
    }
    
    def __init__(self):
        self.platform = self._detect_platform()
        self.platform_config = self._get_platform_config()
        self.gpu_info = self._detect_gpu()
        self.system_info = self._get_system_info()
        self.optimizations = self._calculate_optimizations()
    
    def _detect_platform(self) -> str:
        """Detect current platform with enhanced detection"""
        # Check each platform signature
        for platform_name, signature in self.PLATFORM_SIGNATURES.items():
            # Check environment variables
            if 'env_vars' in signature:
                for env_var in signature['env_vars']:
                    if env_var in os.environ:
                        logger.info(f"Detected platform: {platform_name} (via env var: {env_var})")
                        return platform_name
            
            # Check paths
            if 'paths' in signature:
                for path in signature['paths']:
                    if os.path.exists(path):
                        logger.info(f"Detected platform: {platform_name} (via path: {path})")
                        return platform_name
        
        # Check for generic workspace
        if os.path.exists('/workspace'):
            return 'workspace'
        
        # Default to local
        return 'local'
    
    def _get_platform_config(self) -> Dict:
        """Get platform-specific configuration"""
        base_config = {
            'platform': self.platform,
            'root': self.PLATFORM_SIGNATURES.get(self.platform, {}).get('root', str(Path.home())),
            'has_gpu': False,
            'gpu_type': None,
            'vram_gb': 0,
            'ram_gb': psutil.virtual_memory().total / (1024**3),
            'cpu_cores': psutil.cpu_count(),
            'python_version': sys.version,
            'os': platform.system(),
            'os_version': platform.version()
        }
        
        # Platform-specific configurations
        platform_configs = {
            'colab': {
                'max_runtime_hours': 12,
                'persistent_storage': False,
                'tunnel_required': True,
                'recommended_tunnel': 'cloudflared',
                'package_manager': 'apt-get'
            },
            'kaggle': {
                'max_runtime_hours': 12,
                'persistent_storage': False,
                'tunnel_required': False,
                'package_manager': 'apt-get'
            },
            'lightning': {
                'persistent_storage': True,
                'tunnel_required': False,
                'studio_enabled': True,
                'package_manager': 'apt-get'
            },
            'paperspace': {
                'persistent_storage': True,
                'tunnel_required': False,
                'gradient_enabled': True,
                'package_manager': 'apt-get'
            },
            'runpod': {
                'persistent_storage': True,
                'tunnel_required': False,
                'ssh_enabled': True,
                'package_manager': 'apt-get'
            },
            'vast': {
                'persistent_storage': True,
                'tunnel_required': True,
                'ssh_enabled': True,
                'package_manager': 'apt-get'
            }
        }
        
        # Merge platform-specific config
        if self.platform in platform_configs:
            base_config.update(platform_configs[self.platform])
        
        return base_config
    
    def _detect_gpu(self) -> Dict:
        """Detect GPU information"""
        gpu_info = {
            'available': False,
            'count': 0,
            'devices': [],
            'cuda_version': None,
            'driver_version': None
        }
        
        try:
            # Try nvidia-smi
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total,memory.free,driver_version,compute_cap',
                 '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                gpu_info['available'] = True
                lines = result.stdout.strip().split('\n')
                gpu_info['count'] = len(lines)
                
                for idx, line in enumerate(lines):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        gpu_info['devices'].append({
                            'index': idx,
                            'name': parts[0],
                            'vram_total': parts[1],
                            'vram_free': parts[2],
                            'driver': parts[3] if len(parts) > 3 else None,
                            'compute_cap': parts[4] if len(parts) > 4 else None
                        })
                
                # Get CUDA version
                cuda_result = subprocess.run(['nvcc', '--version'], 
                                           capture_output=True, text=True)
                if cuda_result.returncode == 0:
                    import re
                    match = re.search(r'release (\d+\.\d+)', cuda_result.stdout)
                    if match:
                        gpu_info['cuda_version'] = match.group(1)
                
                logger.info(f"GPU detected: {gpu_info}")
                
        except Exception as e:
            logger.debug(f"GPU detection failed: {e}")
        
        return gpu_info
    
    def _get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        return {
            'hostname': platform.node(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'disk_total_gb': psutil.disk_usage('/').total / (1024**3),
            'disk_free_gb': psutil.disk_usage('/').free / (1024**3),
            'network_interfaces': list(psutil.net_if_addrs().keys())
        }
    
    def _calculate_optimizations(self) -> Dict:
        """Calculate platform-specific optimizations"""
        optimizations = {
            'batch_size': 1,
            'num_workers': 2,
            'mixed_precision': 'no',
            'gradient_checkpointing': False,
            'cpu_offload': False,
            'attention_slicing': False,
            'vae_slicing': False,
            'sequential_cpu_offload': False,
            'channels_last_memory': False,
            'torch_compile': False,
            'xformers': False,
            'sdp_attention': True
        }
        
        # Adjust based on GPU
        if self.gpu_info['available'] and self.gpu_info['devices']:
            first_gpu = self.gpu_info['devices'][0]
            vram_str = first_gpu.get('vram_total', '0 MiB')
            
            # Parse VRAM
            try:
                vram_mb = float(vram_str.replace(' MiB', '').replace(' MB', ''))
                vram_gb = vram_mb / 1024
                
                if vram_gb >= 24:  # High-end GPU (A100, 3090, 4090)
                    optimizations.update({
                        'batch_size': 8,
                        'num_workers': 8,
                        'mixed_precision': 'fp16',
                        'xformers': True,
                        'torch_compile': True,
                        'channels_last_memory': True
                    })
                elif vram_gb >= 16:  # Mid-high GPU (V100, A10, 3080)
                    optimizations.update({
                        'batch_size': 4,
                        'num_workers': 4,
                        'mixed_precision': 'fp16',
                        'xformers': True,
                        'gradient_checkpointing': True
                    })
                elif vram_gb >= 12:  # Mid GPU (T4, 3060)
                    optimizations.update({
                        'batch_size': 2,
                        'num_workers': 2,
                        'mixed_precision': 'fp16',
                        'gradient_checkpointing': True,
                        'attention_slicing': True,
                        'xformers': True
                    })
                elif vram_gb >= 8:  # Low-mid GPU
                    optimizations.update({
                        'batch_size': 1,
                        'num_workers': 2,
                        'mixed_precision': 'fp16',
                        'gradient_checkpointing': True,
                        'attention_slicing': True,
                        'vae_slicing': True,
                        'cpu_offload': True
                    })
                else:  # Low VRAM
                    optimizations.update({
                        'batch_size': 1,
                        'num_workers': 1,
                        'mixed_precision': 'fp16',
                        'gradient_checkpointing': True,
                        'attention_slicing': True,
                        'vae_slicing': True,
                        'sequential_cpu_offload': True
                    })
                    
            except Exception as e:
                logger.warning(f"Could not parse VRAM: {e}")
        
        # Platform-specific adjustments
        if self.platform == 'colab':
            optimizations['xformers'] = True  # Pre-installed on Colab
            
        elif self.platform == 'kaggle':
            optimizations['gradient_checkpointing'] = True  # Memory constrained
            
        elif self.platform in ['paperspace', 'runpod', 'vast', 'lambda']:
            optimizations['num_workers'] = min(8, psutil.cpu_count())
        
        return optimizations
    
    def get_launch_args(self, webui_type: str = 'A1111') -> List[str]:
        """Get optimized launch arguments for WebUI"""
        args = []
        
        # Common arguments
        args.extend(['--listen', '--enable-insecure-extension-access'])
        
        # GPU optimizations
        if self.gpu_info['available']:
            if self.optimizations['xformers']:
                args.append('--xformers')
            
            if self.optimizations['mixed_precision'] == 'fp16':
                args.extend(['--precision', 'full', '--no-half-vae'])
            
            if self.optimizations['cpu_offload']:
                args.append('--medvram')
            
            if self.optimizations['sequential_cpu_offload']:
                args.append('--lowvram')
            
            if self.optimizations['sdp_attention']:
                args.append('--opt-sdp-attention')
        else:
            # CPU mode
            args.extend(['--skip-torch-cuda-test', '--use-cpu', 'all'])
        
        # Platform-specific arguments
        if self.platform == 'colab':
            args.extend(['--share', '--gradio-debug'])
            
        elif self.platform in ['paperspace', 'runpod']:
            args.append('--api')
        
        # WebUI-specific arguments
        if webui_type == 'ComfyUI':
            # ComfyUI has different argument format
            args = ['--listen', '0.0.0.0']
            if self.gpu_info['available']:
                if self.optimizations['cpu_offload']:
                    args.append('--lowvram')
        
        return args
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get platform-optimized environment variables"""
        env_vars = os.environ.copy()
        
        # CUDA optimizations
        if self.gpu_info['available']:
            env_vars.update({
                'CUDA_LAUNCH_BLOCKING': '0',
                'CUDNN_BENCHMARK': 'True',
                'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512',
                'TORCH_CUDA_ARCH_LIST': '6.0;6.1;7.0;7.5;8.0;8.6'
            })
        
        # Platform-specific environment
        if self.platform == 'colab':
            env_vars['COLAB_GPU'] = '1'
            
        elif self.platform == 'kaggle':
            env_vars['KAGGLE_KERNEL'] = '1'
        
        # Set cache directories
        cache_dir = Path.home() / '.cache'
        env_vars.update({
            'HF_HOME': str(cache_dir / 'huggingface'),
            'TORCH_HOME': str(cache_dir / 'torch'),
            'TRANSFORMERS_CACHE': str(cache_dir / 'transformers')
        })
        
        return env_vars
    
    def get_info_summary(self) -> str:
        """Get formatted platform information summary"""
        lines = [
            f"Platform: {self.platform}",
            f"OS: {self.system_info.get('os', 'Unknown')} {self.system_info.get('os_version', '')}",
            f"Python: {self.system_info.get('python_version', 'Unknown')}",
            f"CPU: {self.system_info.get('cpu_count', 'Unknown')} cores",
            f"RAM: {self.system_info.get('memory_gb', 0):.1f} GB",
            f"Disk: {self.system_info.get('disk_free_gb', 0):.1f} GB free"
        ]
        
        if self.gpu_info['available']:
            for gpu in self.gpu_info['devices']:
                lines.append(f"GPU: {gpu['name']} ({gpu['vram_total']})")
        else:
            lines.append("GPU: Not available")
        
        return "\n".join(lines)