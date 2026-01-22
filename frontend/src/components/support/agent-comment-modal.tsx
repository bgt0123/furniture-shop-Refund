import React, { useState, useRef, useEffect } from 'react';

interface AgentCommentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string, commentType?: string, isInternal?: boolean, files?: File[], shouldCloseCase?: boolean) => void;
  caseNumber: string;
  allowCloseCase?: boolean;
  currentStatus?: string;
}

const AgentCommentModal: React.FC<AgentCommentModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  caseNumber,
  allowCloseCase = false,
  currentStatus = 'open'
}) => {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [commentType, setCommentType] = useState('agent_note');
  const [isInternal, setIsInternal] = useState(false);
  const [shouldCloseCase, setShouldCloseCase] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (isOpen) {
      dialogRef.current?.showModal();
    } else {
      dialogRef.current?.close();
    }
  }, [isOpen]);

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

    setIsSubmitting(true);

    try {
      await onSubmit(content, commentType, isInternal, files, shouldCloseCase && allowCloseCase);
      
      // Reset form
      setContent('');
      setFiles([]);
      setCommentType('agent_note');
      setIsInternal(false);
      setShouldCloseCase(false);
      handleCancel();
    } catch (error) {
      console.error('Error submitting agent comment:', error);
      alert('Failed to add agent comment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setContent('');
    setFiles([]);
    setIsInternal(false);
    setShouldCloseCase(false);
    onClose();
  };

  return (
    <dialog
      ref={dialogRef}
      className="dialog-modal max-w-3xl"
      onClose={handleCancel}
    >
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">
            🛠️ Add Agent Comment
          </h2>
          <button
            onClick={handleCancel}
            className="modal-close-btn"
            disabled={isSubmitting}
          >
            ×
          </button>
        </div>

        <div className="modal-body">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="mb-8">
              <label className="form-label">
                Agent Comment for Case #{caseNumber}
              </label>
              <p className="text-sm text-gray-600">
                Your response will be visible to the customer unless marked as internal.
              </p>
            </div>

            <div className="form-field">
              <label className="form-label">
                Comment Type *
              </label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="commentType"
                    value="agent_note"
                    checked={commentType === 'agent_note'}
                    onChange={(e) => setCommentType(e.target.value)}
                    className="w-4 h-4"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-gray-700">Regular Agent Note</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="commentType"
                    value="customer_feedback"
                    checked={commentType === 'customer_feedback'}
                    onChange={(e) => setCommentType(e.target.value)}
                    className="w-4 h-4"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-gray-700">Customer Feedback Response</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="commentType"
                    value="resolution_update"
                    checked={commentType === 'resolution_update'}
                    onChange={(e) => setCommentType(e.target.value)}
                    className="w-4 h-4"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-gray-700">Resolution Update</span>
                </label>
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">
                Comment Content *
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Type your agent comment..."
                className="form-input form-textarea"
                rows={6}
                disabled={isSubmitting}
                required
              />
            </div>

            {/* Agent-specific options */}
            <div className="space-y-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800">Agent Options</h3>
              
              <div className="space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isInternal}
                    onChange={(e) => setIsInternal(e.target.checked)}
                    className="rounded border-gray-300 w-4 h-4"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-gray-700 font-medium">
                    📝 Internal note (not visible to customer)
                  </span>
                </label>
                
                {allowCloseCase && currentStatus !== 'closed' && (
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={shouldCloseCase}
                      onChange={(e) => setShouldCloseCase(e.target.checked)}
                      className="rounded border-gray-300 w-4 h-4"
                      disabled={isSubmitting}
                    />
                    <span className="text-sm text-green-700 font-medium">
                      🔒 Close case with this response
                    </span>
                  </label>
                )}
                
                {shouldCloseCase && (
                  <div className="bg-green-100 border-l-4 border-green-500 pl-3 py-2 rounded">
                    <p className="text-xs text-green-700 font-medium">
                      ✅ Case will be closed immediately after submitting this response
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* File upload section */}
            <div className="form-field">
              <label className="form-label">
                Attachments ({files.length} files selected)
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                multiple
                className="form-input"
                id="agent-file-input"
                disabled={isSubmitting}
                accept="image/*,.pdf,.doc,.docx"
              />
              <div className="mt-2 flex items-center space-x-4">
                <label
                  htmlFor="agent-file-input"
                  className="cursor-pointer bg-blue-100 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-200 transition-colors disabled:opacity-50"
                >
                  📎 Choose Files
                </label>
                <span className="text-sm text-gray-600">
                  {files.length === 0 && 'No files selected'}
                </span>
              </div>
              
              {files.length > 0 && (
                <div className="file-list mt-4">
                  <ul className="space-y-2">
                    {files.map((file, index) => (
                      <li key={index} className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-lg">
                        <span className="text-sm text-gray-700 truncate flex-1">{file.name}</span>
                        <button
                          type="button"
                          onClick={() => removeFile(index)}
                          className="text-red-500 hover:text-red-700 ml-2 disabled:opacity-50"
                          disabled={isSubmitting}
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Action buttons */}
            <div className="modal-actions">
              <button 
                type="button" 
                onClick={handleCancel} 
                className="btn btn-cancel"
                disabled={isSubmitting}
              >
                Cancel
              </button>
               <button 
                 type="submit" 
                 className="btn btn-submit"
                 disabled={isSubmitting || !content.trim()}
               >
            {isSubmitting 
              ? 'Adding Comment...' 
              : 'Add Agent Comment'
            }
               </button>
            </div>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default AgentCommentModal;