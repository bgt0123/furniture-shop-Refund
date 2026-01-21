import React, { useState, useRef, useEffect } from 'react';

interface CustomerCommentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string, files?: File[]) => void;
  caseNumber: string;
}

const CustomerCommentModal: React.FC<CustomerCommentModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  caseNumber
}) => {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
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
      await onSubmit(content, files);
      
      // Reset form
      setContent('');
      setFiles([]);
      handleCancel();
    } catch (error) {
      console.error('Error submitting customer comment:', error);
      alert('Failed to add comment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setContent('');
    setFiles([]);
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
            💬 Add Customer Comment
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
                My Comment for Case #{caseNumber}
              </label>
              <p className="text-sm text-gray-600">
                Your comment will be visible to support agents.
              </p>
            </div>

            <div className="form-field">
              <label className="form-label">
                Comment Content *
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Add your customer comment here..."
                className="form-input form-textarea"
                rows={6}
                disabled={isSubmitting}
                required
              />
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
                id="customer-file-input"
                disabled={isSubmitting}
                accept="image/*,.pdf,.doc,.docx"
              />
              <div className="mt-2 flex items-center space-x-4">
                <label
                  htmlFor="customer-file-input"
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
                   : 'Add Customer Comment'
                 }
               </button>
            </div>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default CustomerCommentModal;