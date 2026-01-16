interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

interface SupportCaseData {
  customer_id: string;
  order_id: string;
  products: Array<{ id: string; name: string; price?: number }>;
  issue_description: string;
  attachments?: Array<any>;
}

export const validateSupportCase = (data: SupportCaseData): ValidationResult => {
  const errors: string[] = [];

  if (!data.customer_id || typeof data.customer_id !== 'string') {
    errors.push('Customer ID is required');
  }

  if (!data.order_id || typeof data.order_id !== 'string') {
    errors.push('Order ID is required');
  }

  if (!Array.isArray(data.products)) {
    errors.push('Products must be an array');
  } else if (data.products.length === 0) {
    errors.push('At least one product must be selected');
  } else {
    data.products.forEach((product, index) => {
      if (!product.id || typeof product.id !== 'string') {
        errors.push(`Product ${index + 1}: ID is required`);
      }
      if (!product.name || typeof product.name !== 'string') {
        errors.push(`Product ${index + 1}: Name is required`);
      }
    });
  }

  if (!data.issue_description || typeof data.issue_description !== 'string') {
    errors.push('Issue description is required');
  } else if (data.issue_description.trim().length < 10) {
    errors.push('Issue description must be at least 10 characters long');
  } else if (data.issue_description.trim().length > 5000) {
    errors.push('Issue description must be less than 5000 characters');
  }

  if (data.attachments && !Array.isArray(data.attachments)) {
    errors.push('Attachments must be an array');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateUUID = (uuid: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};