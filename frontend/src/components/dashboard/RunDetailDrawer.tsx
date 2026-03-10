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
        { title: 'Project', dataIndex: 'project_name', key: 'project_name' },
        {
          title: 'Action',
          dataIndex: 'action',
          key: 'action',
          width: 100,
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
      ]}
    />
  );
};

export default RunDetailDrawer;
