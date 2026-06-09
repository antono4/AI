#!/usr/bin/env python3
"""
AI Video Shorts Generator - CLI Interface
Command-line interface untuk generate dan upload video
"""

import argparse
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_generate(args):
    """Generate video dari command line"""
    from app.modules.video_generator import create_video_from_topic
    
    print(f"🎬 Generating video: {args.topic}")
    
    result = create_video_from_topic(
        topic=args.topic,
        duration=args.duration,
        language=args.language
    )
    
    if result['status'] == 'success':
        print(f"✅ Video created: {result['final_video']}")
        print(f"📁 Location: {result['project']['output_dir']}")
    else:
        print(f"❌ Failed to generate video")
        sys.exit(1)


def cmd_upload(args):
    """Upload video ke YouTube"""
    from app.modules.youtube_uploader import quick_upload
    
    print(f"📤 Uploading to YouTube: {args.video}")
    
    result = quick_upload(
        video_path=args.video,
        title=args.title or "AI Generated Video",
        description=args.description or "",
        tags=args.tags.split(',') if args.tags else [],
        privacy=args.privacy
    )
    
    if result['status'] == 'success':
        print(f"✅ Uploaded: {result['video_url']}")
    else:
        print(f"❌ Upload failed: {result.get('message', 'Unknown error')}")
        sys.exit(1)


def cmd_pipeline(args):
    """Execute full pipeline"""
    from app.modules.scheduler import PipelineExecutor
    
    print(f"🚀 Executing full pipeline: {args.topic}")
    
    executor = PipelineExecutor()
    result = executor.execute_full_pipeline(
        topic=args.topic,
        duration=args.duration,
        language=args.language,
        voice_provider=args.voice,
        upload_to_youtube=args.upload
    )
    
    print(f"\n📊 Pipeline Results:")
    for step in result.get('steps', []):
        status = "✅" if step.get('status') == 'success' else "❌"
        print(f"  {status} {step['step']}: {step.get('status', 'unknown')}")
    
    if result['status'] != 'success':
        print(f"\n❌ Pipeline failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


def cmd_schedule(args):
    """Schedule video generation"""
    from datetime import datetime, timedelta
    from app.modules.scheduler import get_scheduler, start_automation
    
    scheduler = get_scheduler()
    
    if not scheduler._running:
        print("🔄 Starting scheduler...")
        start_automation()
    
    schedule_time = None
    if args.at:
        schedule_time = datetime.fromisoformat(args.at)
    elif args.in_hours:
        schedule_time = datetime.now() + timedelta(hours=args.in_hours)
    
    print(f"⏰ Scheduling video: {args.topic}")
    
    task_id = scheduler.schedule_video_generation(
        topic=args.topic,
        schedule_time=schedule_time,
        config={
            'topic': args.topic,
            'duration': args.duration,
            'language': args.language,
            'voice_provider': args.voice,
            'upload_to_youtube': args.upload
        }
    )
    
    print(f"✅ Task scheduled: {task_id}")
    print(f"📅 Time: {schedule_time or 'ASAP'}")


def cmd_batch(args):
    """Schedule batch of videos"""
    from app.modules.scheduler import get_scheduler, start_automation
    
    scheduler = get_scheduler()
    start_automation()
    
    topics = [t.strip() for t in args.topics.split(',')]
    
    print(f"📦 Scheduling batch: {len(topics)} videos")
    
    task_ids = scheduler.schedule_batch(
        topics=topics,
        interval_hours=args.interval,
        upload_to_youtube=args.upload
    )
    
    print(f"✅ {len(task_ids)} tasks scheduled")


def cmd_status(args):
    """Check system status"""
    from app.modules.youtube_uploader import YouTubeAuth
    from app.modules.scheduler import get_scheduler
    
    auth = YouTubeAuth()
    scheduler = get_scheduler()
    
    print("📊 System Status:")
    print(f"  YouTube: {'✅ Connected' if auth.is_authenticated() else '❌ Not Connected'}")
    print(f"  Scheduler: {'🟢 Running' if scheduler._running else '🔴 Stopped'}")
    
    status = scheduler.get_status()
    print(f"  Active Jobs: {status['active_jobs']}")
    print(f"  Pending Tasks: {status['pending_tasks']}")
    print(f"  Videos Today: {status['completed_today']}/{status['max_daily']}")


def main():
    parser = argparse.ArgumentParser(
        description="AI Video Shorts Generator - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate video')
    gen_parser.add_argument('topic', help='Video topic')
    gen_parser.add_argument('-d', '--duration', type=int, default=45, help='Duration in seconds')
    gen_parser.add_argument('-l', '--language', default='id', help='Language code')
    gen_parser.set_defaults(func=cmd_generate)
    
    # Upload command
    up_parser = subparsers.add_parser('upload', help='Upload video to YouTube')
    up_parser.add_argument('video', help='Video file path')
    up_parser.add_argument('-t', '--title', help='Video title')
    up_parser.add_argument('-D', '--description', help='Video description')
    up_parser.add_argument('--tags', help='Comma-separated tags')
    up_parser.add_argument('-p', '--privacy', default='private', choices=['public', 'private', 'unlisted'])
    up_parser.set_defaults(func=cmd_upload)
    
    # Pipeline command
    pipe_parser = subparsers.add_parser('pipeline', help='Execute full pipeline')
    pipe_parser.add_argument('topic', help='Video topic')
    pipe_parser.add_argument('-d', '--duration', type=int, default=45, help='Duration in seconds')
    pipe_parser.add_argument('-l', '--language', default='id', help='Language code')
    pipe_parser.add_argument('--voice', default='gtts', choices=['gtts', 'elevenlabs', 'openai'], help='Voice provider')
    pipe_parser.add_argument('--upload', action='store_true', help='Upload to YouTube')
    pipe_parser.set_defaults(func=cmd_pipeline)
    
    # Schedule command
    sched_parser = subparsers.add_parser('schedule', help='Schedule video generation')
    sched_parser.add_argument('topic', help='Video topic')
    sched_parser.add_argument('-d', '--duration', type=int, default=45, help='Duration in seconds')
    sched_parser.add_argument('-l', '--language', default='id', help='Language code')
    sched_parser.add_argument('--voice', default='gtts', choices=['gtts', 'elevenlabs', 'openai'], help='Voice provider')
    sched_parser.add_argument('--upload', action='store_true', help='Upload to YouTube')
    sched_parser.add_argument('--at', help='Schedule at (ISO format)')
    sched_parser.add_argument('--in-hours', type=int, help='Schedule in N hours')
    sched_parser.set_defaults(func=cmd_schedule)
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Schedule batch of videos')
    batch_parser.add_argument('topics', help='Comma-separated topics')
    batch_parser.add_argument('-i', '--interval', type=int, default=4, help='Hours between videos')
    batch_parser.add_argument('--upload', action='store_true', help='Upload to YouTube')
    batch_parser.set_defaults(func=cmd_batch)
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check system status')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()