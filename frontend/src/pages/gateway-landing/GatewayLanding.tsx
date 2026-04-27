import React, { useState, useEffect, useCallback } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './GatewayLanding.css';

type Level = 'public' | 'member' | 'admin';

interface Feature {
  icon: string;
  name: string;
  desc: string;
  level: Level;
  to: string;
  external?: boolean;
}

const FEATURES: Feature[] = [
  {
    icon: '📊',
    name: 'QA 대시보드',
    desc: '테스트 실행 결과 · 성공/실패 추이 · 커버리지 종합',
    level: 'member',
    to: '/dashboard',
  },
  {
    icon: '⚖️',
    name: '엔진 비교',
    desc: 'Playwright · httpx 등 테스트 엔진별 성능·결과 비교',
    level: 'member',
    to: '/engine-comparison',
  },
  {
    icon: '📘',
    name: 'API 가이드',
    desc: '테스트 트리거·결과 조회 RESTful API 사용 가이드',
    level: 'member',
    to: '/api-guide',
  },
  {
    icon: '🔌',
    name: 'API Docs',
    desc: 'Swagger UI 기반 OpenAPI 명세 (FastAPI 자동 생성)',
    level: 'public',
    to: '/api/docs',
    external: true,
  },
];

interface Tech { name: string; dot: string; }
const TECH_STACK: Tech[] = [
  { name: 'React 18', dot: '#61dafb' },
  { name: 'TypeScript', dot: '#3178c6' },
  { name: 'Ant Design', dot: '#1677ff' },
  { name: 'FastAPI', dot: '#009688' },
  { name: 'Playwright', dot: '#2ead33' },
  { name: 'httpx', dot: '#7c3aed' },
  { name: 'GitHub API', dot: '#333333' },
  { name: 'PostgreSQL', dot: '#336791' },
  { name: 'Docker', dot: '#2496ed' },
];

interface Connected { name: string; role: string; href: string; dot: string; }
const CONNECTED_SERVICES: Connected[] = [
  { name: 'AllergyInsight', role: '테스트 대상', href: 'https://allergy.unmong.com', dot: '#f43f5e' },
  { name: 'EduFit', role: '테스트 대상', href: 'https://edufit.unmong.com', dot: '#22c55e' },
  { name: 'HopenVision', role: '테스트 대상', href: 'https://hopenvision.unmong.com', dot: '#3b82f6' },
  { name: 'NewsLetterPlatform', role: '테스트 대상', href: 'https://newsletter.unmong.com', dot: '#ec4899' },
  { name: 'StandUp', role: '테스트 대상', href: 'https://standup.unmong.com', dot: '#14b8a6' },
  { name: 'LogAnalyzer', role: '테스트 대상', href: 'https://loganalyzer.unmong.com', dot: '#f59e0b' },
];

type AccessState = 'granted' | 'member-locked' | 'admin-locked';

function accessFor(level: Level, isAuthenticated: boolean): AccessState {
  if (level === 'public') return 'granted';
  if (level === 'member') return isAuthenticated ? 'granted' : 'member-locked';
  return 'admin-locked';
}

function tagInfo(state: AccessState, level: Level): { label: string; variant: string } {
  if (state === 'granted' && level === 'public') return { label: '🌐 공개', variant: 'public' };
  if (state === 'granted') return { label: '✓ 사용 가능', variant: 'granted' };
  if (state === 'member-locked') return { label: '🔒 회원전용', variant: 'member-locked' };
  if (state === 'admin-locked') return { label: '🔐 관리자 전용', variant: 'admin-locked' };
  return { label: '', variant: '' };
}

interface ToastData { icon: string; message: string; actionLabel: string; actionTo: string; }

function lockedToastFor(state: AccessState): ToastData | null {
  if (state === 'member-locked') {
    return { icon: '🔒', message: '회원전용 서비스입니다', actionLabel: '로그인', actionTo: '/login' };
  }
  if (state === 'admin-locked') {
    return { icon: '🔐', message: '관리자 전용입니다', actionLabel: '관리자 로그인', actionTo: '/login' };
  }
  return null;
}

interface FeatureCardProps {
  feature: Feature;
  accessState: AccessState;
  onLocked: (state: AccessState) => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ feature, accessState, onLocked }) => {
  const locked = accessState !== 'granted';
  const { label, variant } = tagInfo(accessState, feature.level);

  const handleClick = (e: React.MouseEvent) => {
    if (locked) {
      e.preventDefault();
      onLocked(accessState);
    }
  };

  const inner = (
    <>
      {locked && <span className="sl-feature-lock" aria-hidden="true">🔒</span>}
      <span className="sl-feature-icon" aria-hidden="true">{feature.icon}</span>
      <div className="sl-feature-name">{feature.name}</div>
      <div className="sl-feature-desc">{feature.desc}</div>
      <span className={`sl-feature-tag sl-feature-tag--${variant}`}>{label}</span>
    </>
  );

  const commonProps = {
    className: 'sl-feature',
    'data-locked': locked ? 'true' : 'false',
    onClick: handleClick,
  };

  if (feature.external) {
    return <a {...commonProps} href={feature.to} target="_blank" rel="noopener noreferrer">{inner}</a>;
  }
  if (locked) {
    return <a {...commonProps} href={feature.to}>{inner}</a>;
  }
  return <Link {...commonProps} to={feature.to}>{inner}</Link>;
};

interface ToastProps { toast: ToastData | null; onClose: () => void; }

const Toast: React.FC<ToastProps> = ({ toast, onClose }) => {
  if (!toast) return null;
  return (
    <div className="sl-toast" role="status" aria-live="polite">
      <span className="sl-toast-icon" aria-hidden="true">{toast.icon}</span>
      <span className="sl-toast-msg">{toast.message}</span>
      <Link className="sl-toast-action" to={toast.actionTo} onClick={onClose}>
        {toast.actionLabel} →
      </Link>
      <button type="button" className="sl-toast-close" onClick={onClose} aria-label="닫기">×</button>
    </div>
  );
};

const GatewayLanding: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [toast, setToast] = useState<ToastData | null>(null);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(null), 4500);
    return () => clearTimeout(timer);
  }, [toast]);

  const handleLocked = useCallback((accessState: AccessState) => {
    const next = lockedToastFor(accessState);
    if (next) setToast(next);
  }, []);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="gateway-landing-root">
      <div className="sl-container">
        <section className="sl-hero">
          <h1>QA-Agent</h1>
          <p className="tagline">Autonomous Quality Assurance · Test Dashboard</p>
          <p className="desc">
            E2E·API 테스트를 자동 실행하고, 결과를 분석해 GitHub Issue 까지 자동 생성하는 품질 보증 자동화 에이전트
          </p>
        </section>

        <section className="sl-section">
          <div className="sl-section-title">Features</div>
          <div className="sl-features">
            {FEATURES.map((feature) => (
              <FeatureCard
                key={feature.name}
                feature={feature}
                accessState={accessFor(feature.level, isAuthenticated)}
                onLocked={handleLocked}
              />
            ))}
          </div>
        </section>

        <section className="sl-section sl-arch">
          <div className="sl-section-title">Architecture</div>
          <div className="sl-arch-diagram">
            <div className="sl-arch-node">
              <div className="sl-arch-node-label">Test Engine</div>
              <div className="sl-arch-node-tech">Playwright<br /><span className="sl-arch-node-tech-sub">/ httpx</span></div>
            </div>
            <div className="sl-arch-arrow">→</div>
            <div className="sl-arch-node highlight">
              <div className="sl-arch-node-label">Backend</div>
              <div className="sl-arch-node-tech">FastAPI<br /><span className="sl-arch-node-tech-sub">+ Scheduler</span></div>
            </div>
            <div className="sl-arch-arrow">→</div>
            <div className="sl-arch-node">
              <div className="sl-arch-node-label">GitHub</div>
              <div className="sl-arch-node-tech">Issues API<br /><span className="sl-arch-node-tech-sub">자동 생성</span></div>
            </div>
            <div className="sl-arch-arrow">←</div>
            <div className="sl-arch-node">
              <div className="sl-arch-node-label">Frontend</div>
              <div className="sl-arch-node-tech">React + AntD<br /><span className="sl-arch-node-tech-sub">TypeScript</span></div>
            </div>
          </div>
        </section>

        <section className="sl-section sl-flow">
          <div className="sl-section-title">Service Flow</div>
          <div className="sl-flow-steps">
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">1</div>
              <div className="sl-flow-step-label">트리거</div>
              <div className="sl-flow-step-desc">스케줄 / 수동</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">2</div>
              <div className="sl-flow-step-label">테스트 실행</div>
              <div className="sl-flow-step-desc">E2E · API 테스트</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">3</div>
              <div className="sl-flow-step-label">결과 분석</div>
              <div className="sl-flow-step-desc">성공/실패 판정</div>
            </div>
            <div className="sl-flow-arrow">→</div>
            <div className="sl-flow-step">
              <div className="sl-flow-step-num">4</div>
              <div className="sl-flow-step-label">Issue 생성</div>
              <div className="sl-flow-step-desc">GitHub 자동 등록</div>
            </div>
          </div>
        </section>

        <section className="sl-section sl-tech">
          <div className="sl-section-title">Tech Stack</div>
          <div className="sl-tech-list">
            {TECH_STACK.map((tech) => (
              <span className="sl-tech-badge" key={tech.name}>
                <span className="sl-tech-dot" style={{ background: tech.dot }} />
                {tech.name}
              </span>
            ))}
          </div>
        </section>

        <section className="sl-section sl-connected">
          <div className="sl-section-title">Test Targets</div>
          <div className="sl-connected-grid">
            {CONNECTED_SERVICES.map((svc) => (
              <a
                key={svc.name}
                href={svc.href}
                target="_blank"
                rel="noopener noreferrer"
                className="sl-connected-card"
              >
                <span className="sl-connected-dot" style={{ background: svc.dot }} />
                <div className="sl-connected-info">
                  <div className="sl-connected-name">{svc.name}</div>
                  <div className="sl-connected-role">{svc.role}</div>
                </div>
                <span className="sl-connected-arrow">→</span>
              </a>
            ))}
          </div>
        </section>
      </div>

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
};

export default GatewayLanding;
