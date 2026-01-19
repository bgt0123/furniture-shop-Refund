import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="home">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">
          🪑 Furniture Shop Support
        </h1>
        <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
          Welcome to our customer support portal. Choose the dashboard that fits
          your needs.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link
            to="/support-cases"
            className="dashboard-card"
          >
            <div className="icon mb-4 text-4xl">📋</div>
            <h2 className="text-2xl font-bold mb-2">Support Case Dashboard</h2>
            <p className="mb-4 opacity-90">
              Create and manage support cases for product issues, questions, or
              general inquiries
            </p>
            <div className="features text-left space-y-2 text-sm opacity-80">
              <div className="flex items-center">
                • Create new support cases
              </div>
              <div className="flex items-center">
                • Track case status and updates
              </div>
              <div className="flex items-center">• Upload evidence photos</div>
              <div className="flex items-center">
                • Communicate with support agents
              </div>
            </div>
            <div className="mt-6 text-lg font-semibold">
              Go to Support Cases →
            </div>
          </Link>

          <Link
            to="/refund-cases"
            className="dashboard-card"
          >
            <div className="icon mb-4 text-4xl">💸</div>
            <h2 className="text-2xl font-bold mb-2">Refund Case Dashboard</h2>
            <p className="mb-4 opacity-90">
              Submit and track refund requests for damaged, defective, or
              incorrect products
            </p>
            <div className="features text-left space-y-2 text-sm opacity-80">
              <div className="flex items-center">• Submit refund requests</div>
              <div className="flex items-center">• Upload damage evidence</div>
              <div className="flex items-center">• Track refund status</div>
              <div className="flex items-center">
                • Receive refund decisions
              </div>
            </div>
            <div className="mt-6 text-lg font-semibold">
              Go to Refund Cases →
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
