"""
Scheduler and Automation Module
Schedule video creation and uploads, manage automated workflows
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import (
    ENABLE_AUTO_SCHEDULE,
    DEFAULT_SCHEDULE_TIME,
    SCHEDULE_TIMEZONE,
    MAX_DAILY_VIDEOS
)


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    """Scheduled task data structure"""
    task_id: str
    task_type: str  # 'generate', 'upload', 'full_pipeline'
    config: Dict
    schedule_time: datetime = None
    cron_expression: str = None
    interval_minutes: int = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    last_run: datetime = None
    next_run: datetime = None
    run_count: int = 0
    success_count: int = 0
    error_message: str = None
    result: Dict = None


class TaskQueue:
    """In-memory task queue with persistence"""
    
    def __init__(self, storage_path: str = "output/tasks.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, ScheduledTask] = {}
        self._load()
    
    def add(self, task: ScheduledTask) -> str:
        """Add task to queue"""
        self.tasks[task.task_id] = task
        self._save()
        return task.task_id
    
    def get(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def update(self, task_id: str, **kwargs):
        """Update task attributes"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self._save()
    
    def remove(self, task_id: str) -> bool:
        """Remove task from queue"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save()
            return True
        return False
    
    def list_tasks(self, status: TaskStatus = None) -> List[ScheduledTask]:
        """List all tasks or filter by status"""
        if status:
            return [t for t in self.tasks.values() if t.status == status]
        return list(self.tasks.values())
    
    def _load(self):
        """Load tasks from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for task_data in data.values():
                        self.tasks[task_data['task_id']] = ScheduledTask(**task_data)
            except Exception as e:
                print(f"Load tasks error: {e}")
    
    def _save(self):
        """Save tasks to storage"""
        try:
            data = {
                task_id: {
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'config': task.config,
                    'schedule_time': task.schedule_time.isoformat() if task.schedule_time else None,
                    'cron_expression': task.cron_expression,
                    'interval_minutes': task.interval_minutes,
                    'status': task.status.value,
                    'created_at': task.created_at.isoformat(),
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'next_run': task.next_run.isoformat() if task.next_run else None,
                    'run_count': task.run_count,
                    'success_count': task.success_count,
                    'error_message': task.error_message,
                    'result': task.result
                }
                for task_id, task in self.tasks.items()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Save tasks error: {e}")


class PipelineExecutor:
    """Execute video generation and upload pipeline"""
    
    def __init__(self):
        self.is_running = False
        self.current_task = None
    
    def execute_full_pipeline(
        self,
        topic: str,
        duration: int = 45,
        language: str = 'id',
        voice_provider: str = 'gtts',
        upload_to_youtube: bool = False,
        schedule_time: datetime = None
    ) -> Dict:
        """Execute complete pipeline: generate → edit → upload"""
        self.is_running = True
        result = {
            'started_at': datetime.now().isoformat(),
            'steps': []
        }
        
        try:
            # Step 1: Generate content
            from app.modules.video_generator import VideoProject
            project = VideoProject()
            
            content = project.prepare_content(topic, duration, language)
            result['steps'].append({
                'step': 'content_generation',
                'status': 'success',
                'content': content
            })
            
            # Step 2: Fetch stock videos
            videos = project.fetch_stock_videos(topic, num_clips=3)
            result['steps'].append({
                'step': 'stock_videos',
                'status': 'success',
                'videos_count': len(videos)
            })
            
            # Step 3: Create video
            final_video = project.create_video(content.get('title'))
            result['steps'].append({
                'step': 'video_creation',
                'status': 'success' if final_video else 'failed',
                'video_path': final_video
            })
            
            if final_video:
                # Step 4: Process video (add captions, music)
                from app.modules.video_editor import auto_process_video
                processed = auto_process_video(
                    video_path=final_video,
                    script=content
                )
                result['steps'].append({
                    'step': 'video_processing',
                    'status': processed['status'],
                    'output': processed.get('output')
                })
                
                # Step 5: Upload to YouTube
                if upload_to_youtube:
                    from app.modules.youtube_uploader import YouTubeUploader
                    uploader = YouTubeUploader()
                    
                    upload_result = uploader.upload_video(
                        video_path=processed.get('output', final_video),
                        title=content.get('title', topic),
                        description=content.get('description', ''),
                        tags=content.get('tags', []),
                        privacy='private',
                        scheduled_time=schedule_time
                    )
                    result['steps'].append({
                        'step': 'youtube_upload',
                        'status': upload_result['status'],
                        'result': upload_result
                    })
            
            result['status'] = 'success'
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['steps'].append({
                'step': 'error',
                'status': 'failed',
                'error': str(e)
            })
        
        finally:
            self.is_running = False
            result['completed_at'] = datetime.now().isoformat()
        
        return result
    
    def generate_video_only(self, topic: str, duration: int = 45) -> Dict:
        """Generate video without upload"""
        from app.modules.video_generator import VideoProject
        
        project = VideoProject()
        content = project.prepare_content(topic, duration)
        videos = project.fetch_stock_videos(topic, num_clips=3)
        final_video = project.create_video(content.get('title'))
        
        return {
            'status': 'success' if final_video else 'failed',
            'project': project.get_project_info(),
            'content': content,
            'video_path': final_video
        }


class AutomationScheduler:
    """Main scheduler for automation tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=SCHEDULE_TIMEZONE)
        self.task_queue = TaskQueue()
        self.executor = PipelineExecutor()
        self._running = False
        self.daily_count = 0
        self.last_reset = datetime.now().date()
    
    def start(self):
        """Start the scheduler"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            
            # Start daily reset job
            self.scheduler.add_job(
                self._reset_daily_count,
                trigger=CronTrigger(hour=0, minute=0),
                id='daily_reset'
            )
            
            # Re-schedule saved tasks
            self._reschedule_tasks()
            
            print(f"Scheduler started at {datetime.now()}")
    
    def stop(self):
        """Stop the scheduler"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            print("Scheduler stopped")
    
    def _reset_daily_count(self):
        """Reset daily video count"""
        self.daily_count = 0
        self.last_reset = datetime.now().date()
    
    def _reschedule_tasks(self):
        """Reschedule tasks from storage"""
        for task in self.task_queue.list_tasks():
            if task.status == TaskStatus.PENDING:
                self._schedule_task(task)
    
    def _schedule_task(self, task: ScheduledTask):
        """Schedule a task"""
        job_id = f"task_{task.task_id}"
        
        if task.cron_expression:
            # Parse cron expression
            parts = task.cron_expression.split()
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2] if len(parts) > 2 else '*',
                month=parts[3] if len(parts) > 3 else '*',
                day_of_week=parts[4] if len(parts) > 4 else '*'
            )
        elif task.interval_minutes:
            trigger = IntervalTrigger(minutes=task.interval_minutes)
        elif task.schedule_time:
            delay = (task.schedule_time - datetime.now()).total_seconds()
            if delay > 0:
                self.scheduler.add_job(
                    self._execute_task,
                    'date',
                    run_date=task.schedule_time,
                    args=[task.task_id],
                    id=job_id
                )
                return
        
        self.scheduler.add_job(
            self._execute_task,
            trigger,
            args=[task.task_id],
            id=job_id
        )
    
    def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        task = self.task_queue.get(task_id)
        if not task:
            return
        
        # Check daily limit
        if self.daily_count >= MAX_DAILY_VIDEOS:
            task.status = TaskStatus.FAILED
            task.error_message = "Daily limit reached"
            self.task_queue.update(task_id, status=TaskStatus.FAILED, error_message="Daily limit reached")
            return
        
        task.status = TaskStatus.RUNNING
        self.task_queue.update(task_id, status=TaskStatus.RUNNING)
        
        try:
            config = task.config
            
            if task.task_type == 'full_pipeline':
                result = self.executor.execute_full_pipeline(
                    topic=config.get('topic', ''),
                    duration=config.get('duration', 45),
                    language=config.get('language', 'id'),
                    voice_provider=config.get('voice_provider', 'gtts'),
                    upload_to_youtube=config.get('upload_to_youtube', False),
                    schedule_time=config.get('schedule_time')
                )
            elif task.task_type == 'generate':
                result = self.executor.generate_video_only(
                    topic=config.get('topic', ''),
                    duration=config.get('duration', 45)
                )
            else:
                result = {'status': 'unknown_task_type'}
            
            task.status = TaskStatus.COMPLETED if result.get('status') == 'success' else TaskStatus.FAILED
            task.result = result
            task.last_run = datetime.now()
            task.run_count += 1
            
            if task.status == TaskStatus.COMPLETED:
                task.success_count += 1
                self.daily_count += 1
            
            self.task_queue.update(
                task_id,
                status=task.status,
                result=result,
                last_run=task.last_run,
                run_count=task.run_count,
                success_count=task.success_count
            )
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.task_queue.update(
                task_id,
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
    
    def schedule_video_generation(
        self,
        topic: str,
        schedule_time: datetime = None,
        cron: str = None,
        interval_minutes: int = None,
        config: Dict = None
    ) -> str:
        """Schedule a video generation task"""
        task_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = ScheduledTask(
            task_id=task_id,
            task_type='full_pipeline' if config and config.get('upload_to_youtube') else 'generate',
            config=config or {
                'topic': topic,
                'duration': 45,
                'language': 'id'
            },
            schedule_time=schedule_time,
            cron_expression=cron,
            interval_minutes=interval_minutes
        )
        
        self.task_queue.add(task)
        
        if schedule_time or cron or interval_minutes:
            self._schedule_task(task)
        
        return task_id
    
    def schedule_batch(
        self,
        topics: List[str],
        interval_hours: int = 4,
        upload_to_youtube: bool = False
    ) -> List[str]:
        """Schedule batch of videos"""
        task_ids = []
        
        for i, topic in enumerate(topics):
            schedule_time = datetime.now() + timedelta(hours=interval_hours * i)
            
            task_id = self.schedule_video_generation(
                topic=topic,
                schedule_time=schedule_time,
                config={
                    'topic': topic,
                    'duration': 45,
                    'language': 'id',
                    'voice_provider': 'gtts',
                    'upload_to_youtube': upload_to_youtube,
                    'schedule_time': schedule_time
                }
            )
            task_ids.append(task_id)
        
        return task_ids
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            job_id = f"task_{task_id}"
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        self.task_queue.update(task_id, status=TaskStatus.CANCELLED)
        return True
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'running': self._running,
            'active_jobs': len(self.scheduler.get_jobs()),
            'pending_tasks': len(self.task_queue.list_tasks(TaskStatus.PENDING)),
            'running_tasks': len(self.task_queue.list_tasks(TaskStatus.RUNNING)),
            'completed_today': self.daily_count,
            'max_daily': MAX_DAILY_VIDEOS,
            'tasks': [
                {
                    'task_id': t.task_id,
                    'type': t.task_type,
                    'status': t.status.value,
                    'next_run': t.next_run.isoformat() if t.next_run else None,
                    'last_run': t.last_run.isoformat() if t.last_run else None
                }
                for t in self.task_queue.list_tasks()
            ]
        }


# Global scheduler instance
_scheduler = None

def get_scheduler() -> AutomationScheduler:
    """Get global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AutomationScheduler()
    return _scheduler


def start_automation():
    """Start automation scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_automation():
    """Stop automation scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None


if __name__ == "__main__":
    # Test the scheduler
    scheduler = AutomationScheduler()
    print("Scheduler module loaded successfully")
    print(f"Daily limit: {MAX_DAILY_VIDEOS} videos")