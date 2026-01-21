import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import SupportCaseDashboard from './pages/support-case/dashboard';
import SupportCaseDetail from './pages/support-case/detail';
import RefundCaseDashboard from './pages/refund-case/dashboard';
import RefundCaseDetail from './pages/refund-case/detail';
import './styles.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/support-cases" element={<SupportCaseDashboard />} />
        <Route path="/support-cases/:caseNumber" element={<SupportCaseDetail />} />
        <Route path="/refund-cases" element={<RefundCaseDashboard />} />
        <Route path="/refund-cases/:refundCaseId" element={<RefundCaseDetail />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
}

export default App;
