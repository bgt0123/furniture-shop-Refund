import React, { useState } from 'react';

interface CreateCaseFormProps {
  onSubmit: (data: SupportCaseFormData) => void;
  onCancel: () => void;
  userRole: 'customer' | 'agent';
}

interface SupportCaseFormData {
  caseType: string;
  subject: string;
  description: string;
  refundRequestId?: string;
  evidenceFiles: File[];
}

const CreateCaseForm: React.FC<CreateCaseFormProps> = ({
  onSubmit,
  onCancel,
  userRole,
}) => {
  const [formData, setFormData] = useState<SupportCaseFormData>({
    caseType: 'question',
    subject: '',
    description: '',
    evidenceFiles: [],
  });

  const handleInputChange = (
    field: keyof SupportCaseFormData,
    value: string
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      setFormData((prev) => ({
        ...prev,
        evidenceFiles: Array.from(files),
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="create-case-form bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">
        {userRole === 'agent'
          ? 'Create Support Case (Agent)'
          : 'Create Support Case'}
      </h2>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Case Type</label>
          <select
            value={formData.caseType}
            onChange={(e) => handleInputChange('caseType', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          >
            <option value="question">General Question</option>
            <option value="refund">Refund Request</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Subject</label>
          <input
            type="text"
            value={formData.subject}
            onChange={(e) => handleInputChange('subject', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Description</label>
          <textarea
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            rows={4}
            required
          />
        </div>

        {formData.caseType === 'refund' && (
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">
              Refund Request ID (if already created)
            </label>
            <input
              type="text"
              value={formData.refundRequestId || ''}
              onChange={(e) =>
                handleInputChange('refundRequestId', e.target.value)
              }
              className="w-full p-2 border border-gray-300 rounded"
            />
          </div>
        )}

        <div className="mb-4">
          <label className="block text-gray-700 mb-2">Evidence Photos</label>
          <input
            type="file"
            onChange={handleFileChange}
            multiple
            accept="image/*,.pdf"
            className="w-full p-2 border border-gray-300 rounded"
          />
          {formData.evidenceFiles.length > 0 && (
            <div className="mt-2">
              <p className="text-sm text-gray-600">
                Selected files:{' '}
                {formData.evidenceFiles.map((f) => f.name).join(', ')}
              </p>
            </div>
          )}
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Create Case
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateCaseForm;
