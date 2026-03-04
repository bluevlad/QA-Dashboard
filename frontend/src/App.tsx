import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import ApiGuidePage from './pages/ApiGuidePage';

const App: React.FC = () => {
  return (
    <ConfigProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/api-guide" element={<ApiGuidePage />} />
        </Route>
      </Routes>
    </ConfigProvider>
  );
};

export default App;
