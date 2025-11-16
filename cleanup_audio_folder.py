"""
Cleanup Audio Folder - Remove Old User Audio Files

The audio/ folder should ONLY contain TTS responses (Harry's voice).
This script removes any old user audio files that might be there from before the update.
"""

from pathlib import Path
import shutil


def cleanup_audio_folder():
    """Remove old user audio files from audio/ folder"""
    
    print("="*70)
    print(" AUDIO FOLDER CLEANUP ".center(70))
    print("="*70)
    print()
    print("The audio/ folder should only contain TTS responses (Harry's voice).")
    print("This script will remove old user audio files.")
    print()
    
    audio_dir = Path("audio")
    
    if not audio_dir.exists():
        print("✅ Audio folder doesn't exist yet. Nothing to clean up.")
        return
    
    # Find old user audio files
    user_audio_files = list(audio_dir.glob("user_*.wav"))
    user_text_files = list(audio_dir.glob("user_*.txt"))
    
    # Also find old harry files without "tts" in the name
    old_harry_files = [f for f in audio_dir.glob("harry_*.wav") if "tts" not in f.name]
    old_harry_text = [f for f in audio_dir.glob("harry_*.txt") if "tts" not in f.name]
    
    all_old_files = user_audio_files + user_text_files + old_harry_files + old_harry_text
    
    if not all_old_files:
        print("✅ Audio folder is already clean!")
        print(f"   Found {len(list(audio_dir.glob('harry_tts_*.wav')))} TTS audio files")
        print()
        return
    
    print(f"Found {len(all_old_files)} old file(s) to remove:")
    print()
    
    # Show what will be removed
    for file in all_old_files[:10]:  # Show first 10
        print(f"  - {file.name}")
    
    if len(all_old_files) > 10:
        print(f"  ... and {len(all_old_files) - 10} more")
    
    print()
    
    # Ask for confirmation
    response = input("Remove these files? (y/n): ")
    
    if response.lower() != 'y':
        print("\nCleanup cancelled.")
        return
    
    print()
    print("Removing files...")
    
    # Create backup directory
    backup_dir = Path("audio_backup_old_files")
    backup_dir.mkdir(exist_ok=True)
    
    # Move files to backup
    moved_count = 0
    for file in all_old_files:
        try:
            backup_path = backup_dir / file.name
            shutil.move(str(file), str(backup_path))
            moved_count += 1
        except Exception as e:
            print(f"  ⚠️  Error moving {file.name}: {e}")
    
    print()
    print("="*70)
    print(f"✅ Cleanup complete! Moved {moved_count} file(s) to: {backup_dir}")
    print()
    print("Current audio/ folder contents:")
    
    # Show remaining files
    tts_files = list(audio_dir.glob("harry_tts_*.wav"))
    if tts_files:
        print(f"  ✅ {len(tts_files)} TTS audio files (harry_tts_*.wav)")
    else:
        print("  (empty - no conversations recorded yet)")
    
    print()
    print("If you want to restore these files, they're in:")
    print(f"  {backup_dir}/")
    print()
    print("To permanently delete the backup:")
    print(f"  Remove-Item -Recurse {backup_dir}")
    print()


if __name__ == "__main__":
    cleanup_audio_folder()

