import React from 'react';
import { Card, Typography } from 'antd';
import { DashboardOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const DashboardPage: React.FC = () => {
  return (
    <Card>
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <DashboardOutlined style={{ fontSize: 64, color: '#1890ff', marginBottom: 24 }} />
        <Title level={2}>QA Dashboard</Title>
        <Paragraph type="secondary" style={{ fontSize: 16 }}>
          Dashboard page is under construction.
        </Paragraph>
      </div>
    </Card>
  );
};

export default DashboardPage;
