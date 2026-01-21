import React, { useState } from 'react';

interface AgentCommentFormProps {
  caseNumber: string;
  agentId: string;
  onCommentAdded: () => void;
  allowCloseCase?: boolean;
  currentStatus: string;
}

interface CommentData {
  author_id: string;
  author_type: string;
  content: string;
  comment_type: string;
  attachments?: string[];
  is_internal: boolean;
}

const AgentCommentForm: React.FC<AgentCommentFormProps> = ({ 
  caseNumber, 
  agentId, 
  onCommentAdded,
  allowCloseCase = false,
  currentStatus 
}) => {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isInternal, setIsInternal] = useState(false);
  const [shouldCloseCase, setShouldCloseCase] = useState(false);

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
        uploadedAttachments = files.map(file => file.name);
        // TODO: Implement actual file upload
      }

      const commentData: CommentData = {
        author_id: agentId,
        author_type: 'agent',
        content: content,
        comment_type: 'agent_response',
        attachments: uploadedAttachments.length > 0 ? uploadedAttachments : undefined,
        is_internal: isInternal
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
        throw new Error('Failed to add agent comment');
      }

      // If should close case and allowed to do so
      if (shouldCloseCase && allowCloseCase && currentStatus !== 'closed') {
        try {
          const closeResponse = await fetch(`http://localhost:8001/support-cases/${caseNumber}/close`, {
            method: 'PUT'
          });
          
          if (!closeResponse.ok) {
            console.warn('Failed to close case after adding comment');
          }
        } catch (closeError) {
          console.warn('Error closing case:', closeError);
        }
      }

      // Clear form
      setContent('');
      setFiles([]);
      setIsInternal(false);
      setShouldCloseCase(false);
      
      // Notify parent component
      onCommentAdded();
      
    } catch (error) {
      console.error('Error adding agent comment:', error);
      alert('Failed to add comment. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="agent-comment-form-container bg-white rounded-lg shadow-md p-6 mb-6 border-l-4 border-green-500">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">🛠️ Add Agent Response</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Type your response to the customer..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
          rows={4}
          disabled={isUploading}
        />
        
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={isInternal}
              onChange={(e) => setIsInternal(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Internal note (not visible to customer)</span>
          </label>
          
          {allowCloseCase && currentStatus !== 'closed' && (
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={shouldCloseCase}
                onChange={(e) => setShouldCloseCase(e.target.checked)}
                className="rounded border-gray-300"
              />
              <span className="text-sm text-green-700 font-medium">Close case after response</span>
            </label>
          )}
        </div>
        
        <div className="file-upload-section">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attachments ({files.length} files selected)
          </label>
          <input
            type="file"
            onChange={handleFileChange}
            multiple
            className="hidden"
            id="agent-file-input"
          />
          <div className="flex items-center space-x-4">
            <label
              htmlFor="agent-file-input"
              className="cursor-pointer bg-green-100 text-green-700 px-4 py-2 rounded-lg hover:bg-green-200 transition-colors"
            >
              📎 Attach Files
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
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">
            {isInternal ? '📋 Internal note' : '👤 Customer response'}
          </span>
          <button
            type="submit"
            disabled={isUploading || !content.trim()}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? 'Adding...' : 'Add Response'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AgentCommentForm;