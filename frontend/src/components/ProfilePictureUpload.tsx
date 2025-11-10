'use client';

import { useState, useRef } from 'react';
import { Camera, X, Loader2 } from 'lucide-react';

interface ProfilePictureUploadProps {
  currentPicture?: string | null;
  onUpload: (file: File) => Promise<void>;
  onDelete?: () => Promise<void>;
  size?: 'sm' | 'md' | 'lg';
}

export default function ProfilePictureUpload({
  currentPicture,
  onUpload,
  onDelete,
  size = 'md'
}: ProfilePictureUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload file
    handleUpload(file);
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await onUpload(file);
      setPreview(null);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload profile picture');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete your profile picture?')) {
      return;
    }

    setDeleting(true);
    try {
      if (onDelete) {
        await onDelete();
      }
      setPreview(null);
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete profile picture');
    } finally {
      setDeleting(false);
    }
  };

  const getImageUrl = () => {
    if (preview) return preview;
    if (currentPicture) {
      // If it's a relative path, prepend the API base URL
      if (currentPicture.startsWith('/')) {
        const { getApiBaseUrl } = await import('@/lib/get-api-url');
        const apiUrl = getApiBaseUrl();
        return `${apiUrl}${currentPicture}`;
      }
      return currentPicture;
    }
    return null;
  };

  const imageUrl = getImageUrl();
  const sizeClass = sizeClasses[size];

  return (
    <div className="relative inline-block">
      <div className={`${sizeClass} relative rounded-full overflow-hidden border-2 border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 flex items-center justify-center group`}>
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Profile"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-amber-400 via-orange-500 to-pink-500">
            <span className="text-white text-2xl font-bold">
              {size === 'sm' ? 'U' : size === 'md' ? 'U' : 'U'}
            </span>
          </div>
        )}
        
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="p-2 bg-white/90 hover:bg-white rounded-full transition-colors disabled:opacity-50"
            title="Upload photo"
          >
            {uploading ? (
              <Loader2 className="w-4 h-4 text-slate-700 animate-spin" />
            ) : (
              <Camera className="w-4 h-4 text-slate-700" />
            )}
          </button>
          {imageUrl && onDelete && (
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="p-2 bg-red-500/90 hover:bg-red-500 rounded-full transition-colors disabled:opacity-50"
              title="Delete photo"
            >
              {deleting ? (
                <Loader2 className="w-4 h-4 text-white animate-spin" />
              ) : (
                <X className="w-4 h-4 text-white" />
              )}
            </button>
          )}
        </div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
}



