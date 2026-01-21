import React, { useState } from 'react';

interface CommentFormProps {
  caseNumber: string;
  authorId: string;
  authorType: 'customer' | 'agent';
  onCommentAdded: () => void;
}

interface CommentData {
  author_id: string;
  author_type: string;
  content: string;
  comment_type: string;
  attachments?: string[];
  is_internal: boolean;
}

const CommentForm: React.FC<CommentFormProps> = ({ caseNumber, authorId, authorType, onCommentAdded }) => {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files));
    }
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) return;

    setIsUploading(true);

    try {
      // Upload files if any
      let uploadedAttachments: string[] = [];
      
      if (files.length > 0) {
        // For now, we'll just use the file names as mock attachments
        // In a real implementation, you would upload these to a file storage service
        uploadedAttachments = files.map(file => file.name);
        // TODO: Implement actual file upload
      }

      const commentData: CommentData = {
        author_id: authorId,
        author_type: authorType,
        content: content,
        comment_type: authorType === 'agent' ? 'agent_response' : 'customer_comment',
        attachments: uploadedAttachments.length > 0 ? uploadedAttachments : undefined,
        is_internal: authorType === 'agent'
      };

      // Call the API to add the comment
      const response = await fetch(`http://localhost:8001/support-cases/${caseNumber}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(commentData)
      });

      if (!response.ok) {
        throw new Error('Failed to add comment');
      }

      // Clear form
      setContent('');
      setFiles([]);
      
      // Notify parent component
      onCommentAdded();
      
    } catch (error) {
      console.error('Error adding comment:', error);
      alert('Failed to add comment. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="comment-form-container bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        {authorType === 'agent' ? '💬 Add Response' : '💬 Add Comment'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={authorType === 'agent' ? 'Type your response here...' : 'Add your comment here...'}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          rows={4}
          disabled={isUploading}
        />
        
        <div className="file-upload-section">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attachments ({files.length} files selected)
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            multiple
            className="hidden"
            id="file-input"
          />
          <div className="flex items-center space-x-4">
            <label
              htmlFor="file-input"
              className="cursor-pointer bg-blue-100 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors"
            >
              📎 Choose Files
            </label>
            <span className="text-sm text-gray-600">
              {files.length === 0 && 'No files selected'}
            </span>
          </div>
          
          {files.length > 0 && (
            <div className="file-list mt-3">
              <ul className="space-y-2">
                {files.map((file, index) => (
                  <li key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                    <span className="text-sm text-gray-700 truncate flex-1">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700 ml-2"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isUploading || !content.trim()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? 'Adding...' : 'Add Comment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CommentForm;