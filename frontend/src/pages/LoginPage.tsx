import React, { useEffect, useCallback, useRef } from 'react';
import { Card, Typography, Alert, Space, Spin } from 'antd';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

const errorMessages: Record<string, string> = {
  oauth_failed: 'Google 인증에 실패했습니다. 다시 시도해주세요.',
  unauthorized: '관리자 권한이 없는 계정입니다.',
  invalid_credential: '유효하지 않은 인증 정보입니다.',
};

const LoginPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const error = searchParams.get('error');
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const initializedRef = useRef(false);

  const handleCredentialResponse = useCallback(
    async (response: { credential: string }) => {
      try {
        const res = await fetch('/api/auth/google/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ credential: response.credential }),
        });

        if (res.status === 403) {
          navigate('/login?error=unauthorized', { replace: true });
          return;
        }

        if (!res.ok) {
          navigate('/login?error=invalid_credential', { replace: true });
          return;
        }

        const data = await res.json();
        login(data.token);
        navigate('/', { replace: true });
      } catch {
        navigate('/login?error=oauth_failed', { replace: true });
      }
    },
    [login, navigate],
  );

  useEffect(() => {
    if (initializedRef.current) return;
    if (!GOOGLE_CLIENT_ID) {
      console.error('VITE_GOOGLE_CLIENT_ID is not configured');
      return;
    }

    const initializeGoogle = () => {
      if (!window.google?.accounts?.id || !googleButtonRef.current) return;
      initializedRef.current = true;

      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
      });

      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        width: 352,
        text: 'signin_with',
        locale: 'ko',
      });
    };

    if (window.google?.accounts?.id) {
      initializeGoogle();
    } else {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogle;
      document.head.appendChild(script);
    }
  }, [handleCredentialResponse]);

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

          <div
            ref={googleButtonRef}
            style={{
              display: 'flex',
              justifyContent: 'center',
              minHeight: 44,
              alignItems: 'center',
            }}
          >
            {!initializedRef.current && <Spin size="small" />}
          </div>
        </Space>
      </Card>
    </div>
  );
};

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
          }) => void;
          renderButton: (
            element: HTMLElement,
            config: {
              theme?: string;
              size?: string;
              width?: number;
              text?: string;
              locale?: string;
            },
          ) => void;
        };
      };
    };
  }
}

export default LoginPage;
