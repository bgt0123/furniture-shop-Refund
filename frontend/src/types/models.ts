// Types for Customer Support and Refund Service

export interface SupportCase {
  id: string;
  customer_id: string;
  order_id: string;
  products: any[];
  issue_description: string;
  status: string;
  created_at: string;
  closed_at: string | null;
  intends_refund: string;
}

export interface RefundCase {
  id: string;
  support_case_id: string;
  customer_id: string;
  order_id: string;
  products: Array<{
    product_id: string;
    quantity: number;
    price?: number;
    name?: string;
    delivery_date?: string;
    eligibility?: string;
  }>;
  total_refund_amount: number;
  status: 'Pending' | 'Approved' | 'Rejected' | 'Completed';
  eligibility_status: 'Eligible' | 'Partially Eligible' | 'Ineligible';
  created_at: string;
  processed_at: string | null;
  rejection_reason: string | null;
  agent_id: string | null;
  reason: string;
}

export interface SupportAgent {
  id: string;
  name: string;
  email: string;
  role: 'Regular' | 'Senior' | 'Manager' | 'Admin';
  permissions: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RefundCaseApproval {
  approval_notes?: string;
}

export interface RefundCaseRejection {
  reason: string;
}

export interface RefundCaseAdminList {
  id: string;
  support_case_id: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  order_id: string;
  status: string;
  eligibility_status: string;
  total_refund_amount: number;
  created_at: string;
}

export interface AgentRefundListResponse {
  refund_cases: RefundCaseAdminList[];
  total_count: number;
  limit: number;
  offset: number;
}