"""SQLite database schema for Support Service"""

CREATE_SUPPORT_CASES_TABLE = """
CREATE TABLE IF NOT EXISTS support_cases (
    case_number TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    case_type TEXT NOT NULL CHECK(case_type IN ('question', 'refund')),
    refund_request_id TEXT,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open', 'in_progress', 'closed')),
    assigned_agent_id TEXT,
    order_id TEXT,
    product_ids TEXT, -- Comma-separated list of product IDs
    delivery_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_SUPPORT_RESPONSES_TABLE = """
CREATE TABLE IF NOT EXISTS support_responses (
    response_id TEXT PRIMARY KEY,
    case_number TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    sender_type TEXT NOT NULL CHECK(sender_type IN ('customer', 'agent')),
    content TEXT NOT NULL,
    message_type TEXT NOT NULL CHECK(message_type IN ('question', 'answer', 'status_update', 'close_case')),
    attachments TEXT, -- JSON array of file paths
    is_internal BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_number) REFERENCES support_cases(case_number)
);
"""

CREATE_SUPPORT_COMMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS support_comments (
    comment_id TEXT PRIMARY KEY,
    case_number TEXT NOT NULL,
    author_id TEXT NOT NULL,
    author_type TEXT NOT NULL CHECK(author_type IN ('customer', 'agent', 'refund_service')),
    content TEXT NOT NULL,
    comment_type TEXT NOT NULL CHECK(comment_type IN ('customer_comment', 'agent_response', 'refund_feedback')),
    attachments TEXT, -- JSON array of file paths
    is_internal BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_number) REFERENCES support_cases(case_number)
);
"""

# Indexes for performance
CREATE_SUPPORT_CASES_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_support_cases_customer ON support_cases(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_support_cases_status ON support_cases(status);",
    "CREATE INDEX IF NOT EXISTS idx_support_cases_agent ON support_cases(assigned_agent_id);"
]

CREATE_SUPPORT_RESPONSES_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_support_responses_case ON support_responses(case_number);",
    "CREATE INDEX IF NOT EXISTS idx_support_responses_timestamp ON support_responses(timestamp);"
]

CREATE_SUPPORT_COMMENTS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_support_comments_case ON support_comments(case_number);",
    "CREATE INDEX IF NOT EXISTS idx_support_comments_timestamp ON support_comments(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_support_comments_type ON support_comments(comment_type);"
]