#!/usr/bin/env python3
"""
Download Manager Module
Handles all download operations with progress tracking and error recovery
"""

import os
import asyncio
import aiohttp
import aiofiles
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
from tqdm.asyncio import tqdm
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

@dataclass
class DownloadTask:
    """Download task information"""
    url: str
    destination: Path
    filename: Optional[str] = None
    asset_type: str = "model"
    expected_size: Optional[int] = None
    expected_hash: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    priority: int = 5
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    progress: float = 0.0
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __post_init__(self):
        if not self.filename:
            # Extract filename from URL
            parsed_url = urlparse(self.url)
            self.filename = unquote(os.path.basename(parsed_url.path))
            if not self.filename:
                self.filename = f"download_{hashlib.md5(self.url.encode()).hexdigest()[:8]}"

class DownloadManager:
    """Advanced download manager with async operations"""
    
    def __init__(self, storage_manager=None, max_concurrent: int = 3):
        self.storage_manager = storage_manager
        self.max_concurrent = max_concurrent
        self.download_queue: List[DownloadTask] = []
        self.active_downloads: Dict[str, DownloadTask] = {}
        self.completed_downloads: List[DownloadTask] = []
        self.failed_downloads: List[DownloadTask] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.progress_callbacks: List[Callable] = []
        self.total_downloaded = 0
        self.total_failed = 0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=self.max_concurrent),
            timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def add_download(self, url: str, destination: Path = None, 
                    asset_type: str = "model", **kwargs) -> DownloadTask:
        """Add a download task to the queue"""
        if destination is None:
            destination = Path("/workspace/SD-DarkMaster-Pro/storage/downloads")
        
        task = DownloadTask(
            url=url,
            destination=destination,
            asset_type=asset_type,
            **kwargs
        )
        
        self.download_queue.append(task)
        logger.info(f"Added download task: {task.filename}")
        return task
    
    def add_batch_downloads(self, urls: List[str], asset_type: str = "model") -> List[DownloadTask]:
        """Add multiple download tasks"""
        tasks = []
        for url in urls:
            task = self.add_download(url, asset_type=asset_type)
            tasks.append(task)
        return tasks
    
    async def download_file(self, task: DownloadTask) -> bool:
        """Download a single file with progress tracking"""
        task.status = "downloading"
        task.start_time = time.time()
        
        try:
            # Ensure destination directory exists
            task.destination.mkdir(parents=True, exist_ok=True)
            file_path = task.destination / task.filename
            
            # Check if file already exists
            if file_path.exists() and not self._should_redownload(file_path, task):
                logger.info(f"File already exists: {task.filename}")
                task.status = "completed"
                task.progress = 100.0
                return True
            
            # Download with progress tracking
            async with self.session.get(task.url) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                task.expected_size = total_size
                
                # Create progress bar
                progress_bar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=task.filename[:30]
                )
                
                # Download in chunks
                async with aiofiles.open(file_path, 'wb') as file:
                    downloaded = 0
                    async for chunk in response.content.iter_chunked(8192):
                        await file.write(chunk)
                        downloaded += len(chunk)
                        progress_bar.update(len(chunk))
                        
                        # Update task progress
                        if total_size > 0:
                            task.progress = (downloaded / total_size) * 100
                        
                        # Call progress callbacks
                        for callback in self.progress_callbacks:
                            callback(task)
                
                progress_bar.close()
            
            # Verify download
            if task.expected_hash:
                if not self._verify_hash(file_path, task.expected_hash):
                    raise ValueError("Hash verification failed")
            
            # Organize file if storage manager is available
            if self.storage_manager:
                final_path = self.storage_manager.organize_downloads(file_path, task.asset_type)
                task.metadata['final_path'] = str(final_path)
            
            task.status = "completed"
            task.progress = 100.0
            task.end_time = time.time()
            self.completed_downloads.append(task)
            self.total_downloaded += 1
            
            logger.info(f"✅ Downloaded: {task.filename}")
            return True
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                logger.warning(f"Download failed, retrying ({task.retry_count}/{task.max_retries}): {e}")
                task.status = "retry"
                return await self.download_file(task)  # Retry
            else:
                task.status = "failed"
                task.end_time = time.time()
                self.failed_downloads.append(task)
                self.total_failed += 1
                logger.error(f"❌ Download failed: {task.filename} - {e}")
                return False
    
    async def process_queue(self) -> Dict[str, int]:
        """Process all downloads in the queue"""
        if not self.session:
            async with self:
                return await self._process_queue_internal()
        else:
            return await self._process_queue_internal()
    
    async def _process_queue_internal(self) -> Dict[str, int]:
        """Internal queue processing"""
        # Sort queue by priority
        self.download_queue.sort(key=lambda x: x.priority, reverse=True)
        
        # Process downloads with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_semaphore(task):
            async with semaphore:
                self.active_downloads[task.filename] = task
                result = await self.download_file(task)
                del self.active_downloads[task.filename]
                return result
        
        # Create tasks for all downloads
        download_tasks = [
            download_with_semaphore(task) 
            for task in self.download_queue
        ]
        
        # Execute all downloads
        results = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        # Summary
        summary = {
            'total': len(self.download_queue),
            'completed': self.total_downloaded,
            'failed': self.total_failed,
            'duration': sum(
                (t.end_time - t.start_time) 
                for t in self.completed_downloads 
                if t.end_time and t.start_time
            )
        }
        
        logger.info(f"Download summary: {summary}")
        return summary
    
    def _should_redownload(self, file_path: Path, task: DownloadTask) -> bool:
        """Check if file should be redownloaded"""
        if not file_path.exists():
            return True
        
        # Check file size if expected size is known
        if task.expected_size:
            actual_size = file_path.stat().st_size
            if actual_size != task.expected_size:
                logger.info(f"Size mismatch: expected {task.expected_size}, got {actual_size}")
                return True
        
        # Check hash if provided
        if task.expected_hash:
            if not self._verify_hash(file_path, task.expected_hash):
                logger.info("Hash mismatch, redownloading")
                return True
        
        return False
    
    def _verify_hash(self, file_path: Path, expected_hash: str) -> bool:
        """Verify file hash"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        calculated_hash = sha256_hash.hexdigest()
        return calculated_hash == expected_hash
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback function"""
        self.progress_callbacks.append(callback)
    
    def get_active_downloads(self) -> List[DownloadTask]:
        """Get list of active downloads"""
        return list(self.active_downloads.values())
    
    def get_download_stats(self) -> Dict:
        """Get download statistics"""
        total_size = sum(
            t.expected_size for t in self.completed_downloads 
            if t.expected_size
        )
        
        total_time = sum(
            (t.end_time - t.start_time) 
            for t in self.completed_downloads 
            if t.end_time and t.start_time
        )
        
        avg_speed = total_size / total_time if total_time > 0 else 0
        
        return {
            'total_downloads': self.total_downloaded,
            'failed_downloads': self.total_failed,
            'total_size_bytes': total_size,
            'total_size_gb': total_size / (1024**3),
            'total_time_seconds': total_time,
            'average_speed_mbps': avg_speed / (1024**2),
            'queue_remaining': len(self.download_queue),
            'active_downloads': len(self.active_downloads)
        }
    
    async def download_with_metadata(self, url: str, metadata_url: str = None) -> DownloadTask:
        """Download file with associated metadata"""
        # Download main file
        task = self.add_download(url)
        
        # Download metadata if URL provided
        if metadata_url:
            metadata_task = self.add_download(
                metadata_url,
                asset_type="metadata",
                priority=task.priority + 1  # Higher priority for metadata
            )
            
            # Process metadata first
            await self.download_file(metadata_task)
            
            # Load and attach metadata to main task
            if metadata_task.status == "completed":
                metadata_path = metadata_task.destination / metadata_task.filename
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        task.metadata = json.load(f)
        
        # Download main file
        await self.download_file(task)
        return task
    
    def cancel_download(self, filename: str) -> bool:
        """Cancel a download"""
        # Remove from queue
        self.download_queue = [
            t for t in self.download_queue 
            if t.filename != filename
        ]
        
        # Mark active download for cancellation
        if filename in self.active_downloads:
            self.active_downloads[filename].status = "cancelled"
            return True
        
        return False
    
    def clear_queue(self):
        """Clear the download queue"""
        self.download_queue.clear()
        logger.info("Download queue cleared")