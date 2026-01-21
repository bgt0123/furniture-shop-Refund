import React, { useState, useRef, useEffect } from 'react';

interface AgentResponseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (content: string, messageType: string, files?: File[], shouldCloseCase?: boolean) => void;
  caseNumber: string;
  currentStatus: string;
}

const AgentResponseModal: React.FC<AgentResponseModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  caseNumber,
  currentStatus
}) => {
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [messageType, setMessageType] = useState('answer');
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
      await onSubmit(content, messageType, files, shouldCloseCase);
      
      // Reset form
      setContent('');
      setFiles([]);
      setMessageType('answer');
      setShouldCloseCase(false);
      handleCancel();
    } catch (error) {
      console.error('Error submitting response:', error);
      alert('Failed to add response. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setContent('');
    setFiles([]);
    setMessageType('answer');
    setShouldCloseCase(false);
    onClose();
  };

  const messageTypes = [
    { value: 'answer', label: 'Answer', description: 'Provide a solution or response to the customer inquiry' },
    { value: 'status_update', label: 'Status Update', description: 'Update the customer on case progress' },
    { value: 'question', label: 'Clarification Question', description: 'Ask the customer for more information' }
  ];

  return (
    <dialog
      ref={dialogRef}
      className="dialog-modal"
      onClose={handleCancel}
    >
      <div className="modal-container">
        <div className="modal-header">
          <h2 className="modal-title">
            🛠️ Add Agent Response
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
                Response for Case #{caseNumber}
              </label>
              <p className="text-sm text-gray-600">
                Your response will be visible to the customer.
              </p>
            </div>

            {/* Message type selection */}
            <div className="form-field">
              <label className="form-label">Response Type *</label>
              <div className="space-y-4">
                {messageTypes.map((type) => (
                  <label key={type.value} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      name="messageType"
                      value={type.value}
                      checked={messageType === type.value}
                      onChange={(e) => setMessageType(e.target.value)}
                      className="mt-1 rounded border-gray-300 w-4 h-4"
                      disabled={isSubmitting}
                    />
                    <div className="flex-1">
                      <span className="text-sm font-medium text-gray-900">{type.label}</span>
                      <p className="text-xs text-gray-500 mt-1">{type.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="form-field">
              <label className="form-label">
                Response Content *
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Type your response to the customer..."
                className="form-input form-textarea"
                rows={6}
                disabled={isSubmitting}
                required
              />
            </div>

            {/* Agent-specific options */}
            <div className="space-y-4">
              {currentStatus !== 'Closed' && (
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={shouldCloseCase}
                    onChange={(e) => setShouldCloseCase(e.target.checked)}
                    className="rounded border-gray-300 w-4 h-4"
                    disabled={isSubmitting}
                  />
                  <span className="text-sm text-green-700 font-medium">
                    🔒 Close case after response
                  </span>
                </label>
              )}
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
                id="file-input"
                disabled={isSubmitting}
                accept="image/*,.pdf,.doc,.docx"
              />
              <div className="mt-2 flex items-center space-x-4">
                <label
                  htmlFor="file-input"
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
                {isSubmitting ? 'Adding...' : 'Add Response'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default AgentResponseModal;