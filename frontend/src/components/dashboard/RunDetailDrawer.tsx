import React, { useEffect, useState } from 'react';
import {
  Drawer,
  Descriptions,
  Table,
  Tag,
  Spin,
  Alert,
  Tabs,
  Badge,
  Space,
  Typography,
  Collapse,
  Tooltip,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  BugOutlined,
  LinkOutlined,
  ToolOutlined,
  SyncOutlined,
  ClockCircleOutlined,
  BranchesOutlined,
  PullRequestOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { fetchRunDetail } from '../../services/api';
import type {
  RunDetail,
  HealthResult,
  TestResult,
  FailureDetail,
  Suggestion,
  IssueResult,
  FixResult,
  LifecycleItem,
} from '../../types/dashboard';

const { Text } = Typography;

interface Props {
  runId: string | null;
  onClose: () => void;
}

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  const sec = Math.round(ms / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  return `${min}m ${sec % 60}s`;
};

const RunDetailDrawer: React.FC<Props> = ({ runId, onClose }) => {
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) {
      setDetail(null);
      return;
    }
    setLoading(true);
    setError(null);
    fetchRunDetail(runId)
      .then(setDetail)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [runId]);

  const tabItems = detail
    ? [
        {
          key: 'health',
          label: (
            <span>
              Health ({detail.healthResults.length})
            </span>
          ),
          children: <HealthTab results={detail.healthResults} />,
        },
        {
          key: 'tests',
          label: (
            <span>
              Tests ({detail.testResults.length})
            </span>
          ),
          children: <TestTab results={detail.testResults} />,
        },
        {
          key: 'failures',
          label: (
            <span>
              <Badge count={detail.failureDetails.length} size="small" offset={[8, 0]}>
                Failures
              </Badge>
            </span>
          ),
          children: <FailureTab failures={detail.failureDetails} />,
        },
        {
          key: 'suggestions',
          label: `Suggestions (${detail.suggestions.length})`,
          children: <SuggestionTab suggestions={detail.suggestions} />,
        },
        {
          key: 'issues',
          label: `Issues (${detail.issueResults.length})`,
          children: <IssueTab issues={detail.issueResults} />,
        },
        {
          key: 'fixes',
          label: (
            <span>
              <ToolOutlined />{' '}
              <Badge
                count={detail.fixResults.length}
                size="small"
                offset={[4, 0]}
                showZero={false}
                style={{ backgroundColor: detail.fixResults.some(f => f.status === 'failed') ? '#ff4d4f' : '#52c41a' }}
              >
                Fixes
              </Badge>
            </span>
          ),
          children: <FixTab fixes={detail.fixResults} />,
        },
        {
          key: 'lifecycle',
          label: (
            <span>
              <SyncOutlined /> Lifecycle ({detail.lifecycleItems.length})
            </span>
          ),
          children: <LifecycleTab items={detail.lifecycleItems} />,
        },
      ]
    : [];

  return (
    <Drawer
      title={`Run Detail: ${runId || ''}`}
      open={!!runId}
      onClose={onClose}
      width={720}
      destroyOnClose
    >
      {loading && (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
        </div>
      )}
      {error && <Alert type="error" message={error} showIcon />}
      {detail && (
        <>
          <Descriptions size="small" column={2} bordered style={{ marginBottom: 16 }}>
            <Descriptions.Item label="Run ID">{detail.runId}</Descriptions.Item>
            <Descriptions.Item label="Duration">
              {formatDuration(detail.durationMs)}
            </Descriptions.Item>
            <Descriptions.Item label="Started">
              {dayjs(detail.startedAt).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="Finished">
              {dayjs(detail.finishedAt).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="Projects">
              {detail.summary.healthyProjects} / {detail.summary.totalProjects} healthy
            </Descriptions.Item>
            <Descriptions.Item label="Tests">
              <Space>
                <Tag color="green">{detail.summary.totalPassed} passed</Tag>
                <Tag color="red">{detail.summary.totalFailed} failed</Tag>
                {detail.summary.totalSkipped > 0 && (
                  <Tag>{detail.summary.totalSkipped} skipped</Tag>
                )}
              </Space>
            </Descriptions.Item>
          </Descriptions>
          <Tabs items={tabItems} size="small" />
        </>
      )}
    </Drawer>
  );
};

const HealthTab: React.FC<{ results: HealthResult[] }> = ({ results }) => (
  <Table<HealthResult>
    dataSource={results}
    rowKey="id"
    size="small"
    pagination={false}
    columns={[
      {
        title: 'Project',
        dataIndex: 'project_name',
        key: 'project_name',
      },
      {
        title: 'Status',
        dataIndex: 'healthy',
        key: 'healthy',
        width: 100,
        render: (v: boolean) =>
          v ? (
            <Tag color="green" icon={<CheckCircleOutlined />}>
              Healthy
            </Tag>
          ) : (
            <Tag color="red" icon={<CloseCircleOutlined />}>
              Down
            </Tag>
          ),
      },
      {
        title: 'Checked',
        dataIndex: 'checked_at',
        key: 'checked_at',
        width: 150,
        render: (v: string) => dayjs(v).format('HH:mm:ss'),
      },
    ]}
    expandable={{
      expandedRowRender: (record) => (
        <Table
          dataSource={record.endpoints}
          rowKey="url"
          size="small"
          pagination={false}
          columns={[
            { title: 'Label', dataIndex: 'label', key: 'label', width: 120 },
            { title: 'URL', dataIndex: 'url', key: 'url', ellipsis: true },
            {
              title: 'Status',
              dataIndex: 'healthy',
              key: 'healthy',
              width: 80,
              render: (v: boolean) => (
                <Badge status={v ? 'success' : 'error'} text={v ? 'OK' : 'Fail'} />
              ),
            },
            {
              title: 'Code',
              dataIndex: 'statusCode',
              key: 'statusCode',
              width: 60,
              render: (v: number | null) => v ?? '-',
            },
            {
              title: 'Response',
              dataIndex: 'responseTimeMs',
              key: 'responseTimeMs',
              width: 90,
              render: (v: number) => `${Math.round(v)}ms`,
            },
          ]}
        />
      ),
      rowExpandable: (record) => record.endpoints && record.endpoints.length > 0,
    }}
  />
);

const TestTab: React.FC<{ results: TestResult[] }> = ({ results }) => (
  <Table<TestResult>
    dataSource={results}
    rowKey="id"
    size="small"
    pagination={false}
    columns={[
      { title: 'Project', dataIndex: 'project_name', key: 'project_name' },
      {
        title: 'Executed',
        dataIndex: 'executed',
        key: 'executed',
        width: 80,
        render: (v: boolean) => (v ? <Tag color="blue">Yes</Tag> : <Tag>No</Tag>),
      },
      {
        title: 'Results',
        key: 'results',
        width: 200,
        render: (_: unknown, r: TestResult) =>
          r.executed ? (
            <Space size={4}>
              <Tag color="green">{r.passed}</Tag>
              <Tag color="red">{r.failed}</Tag>
              {r.skipped > 0 && <Tag>{r.skipped}</Tag>}
              <Text type="secondary">/ {r.total}</Text>
            </Space>
          ) : (
            <Text type="secondary">{r.skipped_reason || 'Skipped'}</Text>
          ),
      },
      {
        title: 'Duration',
        dataIndex: 'duration_ms',
        key: 'duration_ms',
        width: 90,
        render: (v: number) => formatDuration(v),
      },
      {
        title: 'Exit',
        dataIndex: 'exit_code',
        key: 'exit_code',
        width: 60,
        render: (v: number) =>
          v === 0 ? (
            <Tag color="green">0</Tag>
          ) : (
            <Tag color="red">{v}</Tag>
          ),
      },
    ]}
  />
);

const FailureTab: React.FC<{ failures: FailureDetail[] }> = ({ failures }) => {
  if (failures.length === 0) {
    return <Text type="secondary">No failures</Text>;
  }

  const items = failures.map((f) => ({
    key: String(f.id),
    label: (
      <Space>
        <BugOutlined style={{ color: '#ff4d4f' }} />
        <Text>{f.test_name}</Text>
        {f.category && <Tag>{f.category}</Tag>}
      </Space>
    ),
    children: (
      <div>
        {f.suite_name && (
          <div>
            <Text type="secondary">Suite: </Text>
            <Text>{f.suite_name}</Text>
          </div>
        )}
        {f.file_path && (
          <div>
            <Text type="secondary">File: </Text>
            <Text code>{f.file_path}</Text>
          </div>
        )}
        {f.error_message && (
          <div style={{ marginTop: 8 }}>
            <Text type="secondary">Error:</Text>
            <pre
              style={{
                background: '#fff2f0',
                padding: 12,
                borderRadius: 4,
                fontSize: 12,
                maxHeight: 200,
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {f.error_message}
            </pre>
          </div>
        )}
      </div>
    ),
  }));

  return <Collapse items={items} size="small" />;
};

const SuggestionTab: React.FC<{ suggestions: Suggestion[] }> = ({ suggestions }) => {
  if (suggestions.length === 0) {
    return <Text type="secondary">No suggestions</Text>;
  }

  const severityColor: Record<string, string> = {
    critical: 'red',
    warning: 'orange',
    info: 'blue',
  };

  return (
    <Table<Suggestion>
      dataSource={suggestions}
      rowKey="id"
      size="small"
      pagination={false}
      columns={[
        {
          title: 'Severity',
          dataIndex: 'severity',
          key: 'severity',
          width: 90,
          render: (v: string) => (
            <Tag color={severityColor[v] || 'default'} icon={<WarningOutlined />}>
              {v}
            </Tag>
          ),
        },
        { title: 'Title', dataIndex: 'title', key: 'title' },
        {
          title: 'Project',
          dataIndex: 'project_name',
          key: 'project_name',
          width: 130,
          render: (v: string | null) => v || '-',
        },
      ]}
      expandable={{
        expandedRowRender: (record) =>
          record.description ? (
            <div style={{ padding: 8 }}>
              <Text>{record.description}</Text>
            </div>
          ) : null,
        rowExpandable: (record) => !!record.description,
      }}
    />
  );
};

const fixStatusConfig: Record<string, { color: string; label: string }> = {
  pending: { color: 'default', label: 'Pending' },
  in_progress: { color: 'processing', label: 'In Progress' },
  fix_applied: { color: 'blue', label: 'Fix Applied' },
  build_verified: { color: 'cyan', label: 'Build Verified' },
  test_verified: { color: 'geekblue', label: 'Test Verified' },
  pr_created: { color: 'purple', label: 'PR Created' },
  verification_requested: { color: 'orange', label: 'Verifying' },
  verification_passed: { color: 'green', label: 'Verified' },
  verification_failed: { color: 'red', label: 'Verify Failed' },
  merged: { color: 'green', label: 'Merged' },
  deployed: { color: 'green', label: 'Deployed' },
  failed: { color: 'red', label: 'Failed' },
  skipped: { color: 'default', label: 'Skipped' },
};

const priorityColor: Record<string, string> = {
  P0: 'red',
  P1: 'orange',
  P2: 'gold',
  P3: 'blue',
};

const complianceColor: Record<string, string> = {
  pass: 'green',
  review_needed: 'orange',
  rework_needed: 'red',
};

const lifecycleStatusColor: Record<string, string> = {
  detected: 'orange',
  fixing: 'processing',
  fixed: 'blue',
  verifying: 'purple',
  resolved: 'green',
  regression: 'red',
  failed: 'red',
};

const IssueTab: React.FC<{ issues: IssueResult[] }> = ({ issues }) => {
  if (issues.length === 0) {
    return <Text type="secondary">No issue reports</Text>;
  }

  return (
    <Table<IssueResult>
      dataSource={issues}
      rowKey="id"
      size="small"
      pagination={false}
      columns={[
        { title: 'Project', dataIndex: 'project_name', key: 'project_name', width: 120 },
        {
          title: 'Action',
          dataIndex: 'action',
          key: 'action',
          width: 90,
          render: (v: string) => {
            const colorMap: Record<string, string> = {
              created: 'green',
              commented: 'blue',
              skipped: 'default',
              failed: 'red',
            };
            return <Tag color={colorMap[v] || 'default'}>{v}</Tag>;
          },
        },
        {
          title: 'Issue',
          key: 'issue',
          width: 80,
          render: (_: unknown, r: IssueResult) =>
            r.issue_url ? (
              <Tooltip title={r.issue_url}>
                <a href={r.issue_url} target="_blank" rel="noopener noreferrer">
                  <LinkOutlined /> #{r.issue_number}
                </a>
              </Tooltip>
            ) : r.error ? (
              <Text type="danger">{r.error}</Text>
            ) : (
              '-'
            ),
        },
        {
          title: 'Lifecycle',
          key: 'lifecycle_status',
          width: 100,
          render: (_: unknown, r: IssueResult) =>
            r.lifecycle_status ? (
              <Tag color={lifecycleStatusColor[r.lifecycle_status] || 'default'}>
                {r.lifecycle_status}
              </Tag>
            ) : (
              <Text type="secondary">-</Text>
            ),
        },
        {
          title: 'Fix',
          key: 'fix',
          width: 120,
          render: (_: unknown, r: IssueResult) => {
            if (!r.fix_status) return <Text type="secondary">-</Text>;
            return (
              <Space size={4}>
                <Tag color={fixStatusConfig[r.fix_status]?.color || 'default'}>
                  {fixStatusConfig[r.fix_status]?.label || r.fix_status}
                </Tag>
                {r.fix_pr_url && (
                  <a href={r.fix_pr_url} target="_blank" rel="noopener noreferrer">
                    <PullRequestOutlined /> #{r.fix_pr_number}
                  </a>
                )}
              </Space>
            );
          },
        },
      ]}
    />
  );
};

const FixTab: React.FC<{ fixes: FixResult[] }> = ({ fixes }) => {
  if (fixes.length === 0) {
    return <Text type="secondary">No fix results for this run</Text>;
  }

  const succeeded = fixes.filter(f => !['failed', 'skipped', 'pending'].includes(f.status)).length;
  const failed = fixes.filter(f => f.status === 'failed').length;

  const items = fixes.map((f) => ({
    key: String(f.id),
    label: (
      <Space>
        <Tag color={priorityColor[f.priority] || 'default'}>{f.priority}</Tag>
        <Text strong>{f.project_name}</Text>
        <Text type="secondary">#{f.issue_number}</Text>
        <Tag color={fixStatusConfig[f.status]?.color || 'default'}>
          {fixStatusConfig[f.status]?.label || f.status}
        </Tag>
      </Space>
    ),
    children: (
      <div style={{ padding: '8px 0' }}>
        <Descriptions size="small" column={2} bordered>
          <Descriptions.Item label="Category">
            <Tag>{f.category}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Strategy">{f.strategy}</Descriptions.Item>
          {f.branch_name && (
            <Descriptions.Item label="Branch">
              <Space size={4}>
                <BranchesOutlined />
                <Text code>{f.branch_name}</Text>
              </Space>
            </Descriptions.Item>
          )}
          {f.pr_url && (
            <Descriptions.Item label="PR">
              <a href={f.pr_url} target="_blank" rel="noopener noreferrer">
                <PullRequestOutlined /> #{f.pr_number}
              </a>
            </Descriptions.Item>
          )}
          {f.duration_ms != null && (
            <Descriptions.Item label="Duration">
              <ClockCircleOutlined /> {formatDuration(f.duration_ms)}
            </Descriptions.Item>
          )}
          {f.compliance_score && (
            <Descriptions.Item label="Compliance">
              <Tag color={complianceColor[f.compliance_score] || 'default'}>
                {f.compliance_score}
              </Tag>
            </Descriptions.Item>
          )}
          {f.retry_count > 0 && (
            <Descriptions.Item label="Retries">{f.retry_count}</Descriptions.Item>
          )}
          {f.commit_hash && (
            <Descriptions.Item label="Commit">
              <Text code>{f.commit_hash.substring(0, 8)}</Text>
            </Descriptions.Item>
          )}
        </Descriptions>

        {f.modified_files.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Text type="secondary" strong>Modified Files ({f.modified_files.length})</Text>
            <Table
              dataSource={f.modified_files}
              rowKey="path"
              size="small"
              pagination={false}
              style={{ marginTop: 4 }}
              columns={[
                {
                  title: 'Path',
                  dataIndex: 'path',
                  key: 'path',
                  ellipsis: true,
                  render: (v: string) => <Text code style={{ fontSize: 12 }}>{v}</Text>,
                },
                {
                  title: 'Type',
                  dataIndex: 'changeType',
                  key: 'changeType',
                  width: 80,
                  render: (v: string) => {
                    const c = v === 'added' ? 'green' : v === 'deleted' ? 'red' : 'blue';
                    return <Tag color={c}>{v}</Tag>;
                  },
                },
                {
                  title: 'Changes',
                  key: 'changes',
                  width: 100,
                  render: (_: unknown, r: { linesAdded: number; linesDeleted: number }) => (
                    <Space size={4}>
                      <Text style={{ color: '#52c41a' }}>+{r.linesAdded}</Text>
                      <Text style={{ color: '#ff4d4f' }}>-{r.linesDeleted}</Text>
                    </Space>
                  ),
                },
              ]}
            />
          </div>
        )}

        {f.verifications.length > 0 && (
          <div style={{ marginTop: 12 }}>
            <Text type="secondary" strong>Verifications</Text>
            <div style={{ marginTop: 4 }}>
              {f.verifications.map((v, i) => (
                <Tag
                  key={i}
                  color={v.passed ? 'green' : 'red'}
                  icon={v.passed ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  style={{ marginBottom: 4 }}
                >
                  {v.type} {v.durationMs ? `(${formatDuration(v.durationMs)})` : ''}
                </Tag>
              ))}
            </div>
          </div>
        )}

        {f.error && (
          <div style={{ marginTop: 12 }}>
            <Text type="secondary" strong>Error</Text>
            <pre
              style={{
                background: '#fff2f0',
                padding: 12,
                borderRadius: 4,
                fontSize: 12,
                maxHeight: 150,
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                marginTop: 4,
              }}
            >
              {f.error}
            </pre>
          </div>
        )}
      </div>
    ),
  }));

  return (
    <div>
      <Space style={{ marginBottom: 12 }}>
        <Tag color="green">{succeeded} succeeded</Tag>
        {failed > 0 && <Tag color="red">{failed} failed</Tag>}
        <Text type="secondary">Total: {fixes.length}</Text>
      </Space>
      <Collapse items={items} size="small" />
    </div>
  );
};

const lifecycleStatusConfig: Record<string, { color: string; icon: React.ReactNode }> = {
  detected: { color: 'orange', icon: <WarningOutlined /> },
  fixing: { color: 'processing', icon: <SyncOutlined spin /> },
  fixed: { color: 'blue', icon: <ToolOutlined /> },
  verifying: { color: 'purple', icon: <SyncOutlined spin /> },
  resolved: { color: 'green', icon: <CheckCircleOutlined /> },
  regression: { color: 'red', icon: <CloseCircleOutlined /> },
  failed: { color: 'red', icon: <CloseCircleOutlined /> },
};

const LifecycleTab: React.FC<{ items: LifecycleItem[] }> = ({ items }) => {
  if (items.length === 0) {
    return <Text type="secondary">No lifecycle tracking for this run</Text>;
  }

  return (
    <Table<LifecycleItem>
      dataSource={items}
      rowKey="id"
      size="small"
      pagination={false}
      columns={[
        {
          title: 'Project',
          dataIndex: 'project_name',
          key: 'project_name',
          width: 130,
        },
        {
          title: 'Issue',
          dataIndex: 'issue_number',
          key: 'issue_number',
          width: 70,
          render: (v: number) => `#${v}`,
        },
        {
          title: 'Status',
          dataIndex: 'lifecycle_status',
          key: 'lifecycle_status',
          width: 120,
          render: (v: string) => {
            const cfg = lifecycleStatusConfig[v] || { color: 'default', icon: null };
            return (
              <Tag color={cfg.color} icon={cfg.icon}>
                {v}
              </Tag>
            );
          },
        },
        {
          title: 'Fix',
          key: 'fix',
          width: 110,
          render: (_: unknown, r: LifecycleItem) => {
            if (!r.fix_detail_status) return <Text type="secondary">-</Text>;
            const cfg = fixStatusConfig[r.fix_detail_status] || { color: 'default', label: r.fix_detail_status };
            return <Tag color={cfg.color}>{cfg.label}</Tag>;
          },
        },
        {
          title: 'PR',
          key: 'pr',
          width: 70,
          render: (_: unknown, r: LifecycleItem) =>
            r.fix_pr_url ? (
              <a href={r.fix_pr_url} target="_blank" rel="noopener noreferrer">
                <LinkOutlined /> #{r.fix_pr_number}
              </a>
            ) : (
              <Text type="secondary">-</Text>
            ),
        },
        {
          title: 'Compliance',
          key: 'compliance',
          width: 100,
          render: (_: unknown, r: LifecycleItem) =>
            r.fix_compliance_score ? (
              <Tag color={complianceColor[r.fix_compliance_score] || 'default'}>
                {r.fix_compliance_score}
              </Tag>
            ) : (
              <Text type="secondary">-</Text>
            ),
        },
        {
          title: 'Verified',
          key: 'verified',
          width: 80,
          render: (_: unknown, r: LifecycleItem) => {
            if (r.verification_passed === null || r.verification_passed === undefined) {
              return <Text type="secondary">-</Text>;
            }
            return r.verification_passed ? (
              <Tag color="green" icon={<CheckCircleOutlined />}>Pass</Tag>
            ) : (
              <Tag color="red" icon={<CloseCircleOutlined />}>Fail</Tag>
            );
          },
        },
      ]}
      expandable={{
        expandedRowRender: (record) => (
          <Descriptions size="small" column={2} bordered>
            {record.detected_at && (
              <Descriptions.Item label="Detected">
                {dayjs(record.detected_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            )}
            {record.detection_type && (
              <Descriptions.Item label="Type">{record.detection_type}</Descriptions.Item>
            )}
            {record.fix_started_at && (
              <Descriptions.Item label="Fix Started">
                {dayjs(record.fix_started_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            )}
            {record.fix_completed_at && (
              <Descriptions.Item label="Fix Completed">
                {dayjs(record.fix_completed_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            )}
            {record.verified_at && (
              <Descriptions.Item label="Verified At">
                {dayjs(record.verified_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            )}
            {record.resolved_at && (
              <Descriptions.Item label="Resolved At">
                {dayjs(record.resolved_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
            )}
          </Descriptions>
        ),
        rowExpandable: () => true,
      }}
    />
  );
};

export default RunDetailDrawer;
