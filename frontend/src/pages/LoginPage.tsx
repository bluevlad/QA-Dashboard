import React from 'react';
import { Button, Card, Typography, Alert, Space } from 'antd';
import { GoogleOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';

const { Title, Text } = Typography;

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:9095';

const errorMessages: Record<string, string> = {
  oauth_failed: 'Google 인증에 실패했습니다. 다시 시도해주세요.',
  no_user_info: '사용자 정보를 가져올 수 없습니다.',
  unauthorized: '관리자 권한이 없는 계정입니다.',
};

const LoginPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const error = searchParams.get('error');

  const handleGoogleLogin = () => {
    window.location.href = `${BACKEND_URL}/api/auth/google/login`;
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: '#f0f2f5',
      }}
    >
      <Card style={{ width: 400, textAlign: 'center' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Title level={3} style={{ marginBottom: 4 }}>
              QA Dashboard
            </Title>
            <Text type="secondary">관리자 로그인이 필요합니다</Text>
          </div>

          {error && (
            <Alert
              type="error"
              message={errorMessages[error] || '알 수 없는 오류가 발생했습니다.'}
              showIcon
            />
          )}

          <Button
            type="primary"
            icon={<GoogleOutlined />}
            size="large"
            block
            onClick={handleGoogleLogin}
          >
            Google 관리자 로그인
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default LoginPage;
