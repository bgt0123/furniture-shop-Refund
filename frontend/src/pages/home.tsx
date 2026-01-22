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
          Welcome to the Furniture Shop Customer Portal powered by our microservices architecture. 
          Choose the dashboard for your specific needs.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link
            to="/support-cases"
            className="dashboard-card"
          >
            <div className="icon mb-4 text-4xl">📋</div>
            <h2 className="text-2xl font-bold mb-2">Support Case Dashboard</h2>
            <p className="mb-4 opacity-90">
              Comprehensive customer support management powered by Support Service (Port 8001). 
              Handle general inquiries, product assistance, and initiate refund workflows.
            </p>
            <div className="features text-left space-y-2 text-sm opacity-80">
              <div className="flex items-center">
                • Full support case lifecycle management
              </div>
              <div className="flex items-center">
                • Real-time status tracking and comments
              </div>
              <div className="flex items-center">• Direct refund case creation</div>
              <div className="flex items-center">
                • Agent responses and timeline tracking
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
              Specialized refund service (Port 8002). 
              Process financial refunds with integrated support case workflows.
            </p>
            <div className="features text-left space-y-2 text-sm opacity-80">
              <div className="flex items-center">• Dedicated refund request lifecycle</div>
              <div className="flex items-center">• Evidence upload and validation from support agent</div>
              <div className="flex items-center">• Agent approval/rejection workflow</div>
              <div className="flex items-center">• Integrated with support service APIs</div>
              <div className="flex items-center">• Status persistence across services</div>
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
