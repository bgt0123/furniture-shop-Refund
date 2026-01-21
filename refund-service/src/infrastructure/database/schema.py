"""SQLite database schema for Refund Service"""

CREATE_REFUND_CASES_TABLE = """
CREATE TABLE IF NOT EXISTS refund_cases (
    refund_case_id TEXT PRIMARY KEY,
    case_number TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_REFUND_REQUESTS_TABLE = """
CREATE TABLE IF NOT EXISTS refund_requests (
    refund_request_id TEXT PRIMARY KEY,
    support_case_number TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_ids TEXT NOT NULL, -- comma-separated product IDs
    request_reason TEXT NOT NULL,
    evidence_photos TEXT, -- comma-separated file paths
    status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
    decision_reason TEXT,
    refund_amount TEXT,
    decision_date TIMESTAMP,
    decision_agent_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_REFUND_RESPONSES_TABLE = """
CREATE TABLE IF NOT EXISTS refund_responses (
    response_id TEXT PRIMARY KEY,
    refund_request_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    response_type TEXT NOT NULL CHECK(response_type IN ('approval', 'rejection', 'request_additional_evidence')),
    response_content TEXT NOT NULL,
    attachments TEXT, -- JSON array of file paths
    refund_amount TEXT,
    refund_method TEXT CHECK(refund_method IN ('money', 'voucher', 'replacement')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (refund_request_id) REFERENCES refund_requests(refund_request_id)
);
"""

CREATE_CASE_TIMELINE_TABLE = """
CREATE TABLE IF NOT EXISTS case_timeline (
    timeline_id TEXT PRIMARY KEY,
    refund_case_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    actor TEXT,
    notes TEXT,
    FOREIGN KEY (refund_case_id) REFERENCES refund_cases(refund_case_id)
);
"""

# Indexes for performance
REFUND_SERVICE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_refund_requests_case ON refund_requests(support_case_number);",
    "CREATE INDEX IF NOT EXISTS idx_refund_requests_customer ON refund_requests(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_refund_requests_status ON refund_requests(status);"
]