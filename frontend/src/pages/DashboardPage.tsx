import React, { useEffect, useState, useCallback } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Spin,
  Alert,
  Progress,
  Badge,
  Tooltip,
  Button,
  Space,
  Typography,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ProjectOutlined,
  ExperimentOutlined,
  ReloadOutlined,
  RiseOutlined,
  FallOutlined,
  ToolOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import dayjs from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import { fetchSummary, fetchDurationTrend } from '../services/api';
import type {
  DashboardSummary,
  RunListItem,
  ProjectStatus,
  DurationTrendPoint,
} from '../types/dashboard';
import RunDetailDrawer from '../components/dashboard/RunDetailDrawer';

const { Text } = Typography;

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  const sec = Math.round(ms / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  const remSec = sec % 60;
  return `${min}m ${remSec}s`;
};

const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [durationTrend, setDurationTrend] = useState<DurationTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, durationData] = await Promise.all([
        fetchSummary(),
        fetchDurationTrend(30),
      ]);
      setSummary(summaryData);
      setDurationTrend(durationData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard data';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        type="error"
        message="Dashboard Load Error"
        description={error}
        showIcon
        action={
          <Button size="small" onClick={loadData}>
            Retry
          </Button>
        }
      />
    );
  }

  if (!summary) return null;

  const latestRun = summary.latest_run;
  const latestPassRate = latestRun
    ? latestRun.total_tests > 0
      ? ((latestRun.total_passed / latestRun.total_tests) * 100).toFixed(1)
      : '0.0'
    : '-';
  const healthyCount = summary.projects.filter((p) => p.last_healthy === true).length;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Text strong style={{ fontSize: 20 }}>
          QA Dashboard
        </Text>
        <Button icon={<ReloadOutlined />} onClick={loadData}>
          Refresh
        </Button>
      </div>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Runs"
              value={summary.total_runs}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Latest Pass Rate"
              value={latestPassRate}
              suffix="%"
              prefix={
                Number(latestPassRate) >= 80 ? (
                  <RiseOutlined />
                ) : (
                  <FallOutlined />
                )
              }
              valueStyle={{
                color: Number(latestPassRate) >= 80 ? '#52c41a' : '#ff4d4f',
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Healthy Projects"
              value={healthyCount}
              suffix={`/ ${summary.projects.length}`}
              prefix={<CheckCircleOutlined />}
              valueStyle={{
                color: healthyCount === summary.projects.length ? '#52c41a' : '#faad14',
              }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Latest Duration"
              value={latestRun ? formatDuration(latestRun.duration_ms) : '-'}
              prefix={<ClockCircleOutlined />}
            />
            {latestRun && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {dayjs(latestRun.started_at).format('YYYY-MM-DD HH:mm')}
              </Text>
            )}
          </Card>
        </Col>
      </Row>

      {/* Lifecycle Summary */}
      {summary.lifecycle_summary && summary.lifecycle_summary.total > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Issues Tracked"
                value={summary.lifecycle_summary.total}
                prefix={<SyncOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Resolved"
                value={summary.lifecycle_summary.resolved}
                suffix={`/ ${summary.lifecycle_summary.total}`}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="In Progress"
                value={summary.lifecycle_summary.fixing + summary.lifecycle_summary.fixed + summary.lifecycle_summary.verifying}
                prefix={<ToolOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
              <Space size={4} style={{ marginTop: 4 }}>
                {summary.lifecycle_summary.fixing > 0 && <Tag color="processing">Fixing {summary.lifecycle_summary.fixing}</Tag>}
                {summary.lifecycle_summary.fixed > 0 && <Tag color="blue">Fixed {summary.lifecycle_summary.fixed}</Tag>}
                {summary.lifecycle_summary.verifying > 0 && <Tag color="purple">Verifying {summary.lifecycle_summary.verifying}</Tag>}
              </Space>
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Needs Attention"
                value={summary.lifecycle_summary.failed + summary.lifecycle_summary.regression + summary.lifecycle_summary.detected}
                prefix={<CloseCircleOutlined />}
                valueStyle={{
                  color: (summary.lifecycle_summary.failed + summary.lifecycle_summary.regression) > 0 ? '#ff4d4f' : '#faad14',
                }}
              />
              <Space size={4} style={{ marginTop: 4 }}>
                {summary.lifecycle_summary.detected > 0 && <Tag color="orange">Detected {summary.lifecycle_summary.detected}</Tag>}
                {summary.lifecycle_summary.failed > 0 && <Tag color="red">Failed {summary.lifecycle_summary.failed}</Tag>}
                {summary.lifecycle_summary.regression > 0 && <Tag color="red">Regression {summary.lifecycle_summary.regression}</Tag>}
              </Space>
            </Card>
          </Col>
        </Row>
      )}

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Pass Rate Trend (14 days)" size="small">
            {summary.pass_rate_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={summary.pass_rate_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(v) => dayjs(v).format('MM/DD')}
                    fontSize={12}
                  />
                  <YAxis domain={[0, 100]} unit="%" fontSize={12} />
                  <RechartsTooltip
                    labelFormatter={(v) => dayjs(v).format('YYYY-MM-DD')}
                    formatter={(value: number) => [`${value.toFixed(1)}%`, 'Pass Rate']}
                  />
                  <Line
                    type="monotone"
                    dataKey="pass_rate"
                    stroke="#52c41a"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No trend data available
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Test Duration Trend (30 days)" size="small">
            {durationTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={durationTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(v) => dayjs(v).format('MM/DD')}
                    fontSize={12}
                  />
                  <YAxis
                    tickFormatter={(v) => formatDuration(v)}
                    fontSize={12}
                  />
                  <RechartsTooltip
                    labelFormatter={(v) => dayjs(v).format('YYYY-MM-DD')}
                    formatter={(value: number, name: string) => [
                      formatDuration(value),
                      name === 'avg_duration_ms'
                        ? 'Avg'
                        : name === 'max_duration_ms'
                          ? 'Max'
                          : 'Min',
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="max_duration_ms"
                    stackId="1"
                    stroke="#ff7875"
                    fill="#fff1f0"
                    fillOpacity={0.3}
                  />
                  <Area
                    type="monotone"
                    dataKey="avg_duration_ms"
                    stackId="2"
                    stroke="#1890ff"
                    fill="#e6f7ff"
                    fillOpacity={0.5}
                  />
                  <Legend
                    formatter={(value) =>
                      value === 'avg_duration_ms'
                        ? 'Average'
                        : value === 'max_duration_ms'
                          ? 'Max'
                          : 'Min'
                    }
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No duration data available
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Project Status */}
      <Card title="Project Status" size="small" style={{ marginTop: 16 }}>
        <Row gutter={[12, 12]}>
          {summary.projects.map((project) => (
            <Col xs={24} sm={12} md={8} lg={6} key={project.project_name}>
              <ProjectCard project={project} />
            </Col>
          ))}
          {summary.projects.length === 0 && (
            <Col span={24}>
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No project data available
              </div>
            </Col>
          )}
        </Row>
      </Card>

      {/* Recent Runs Table */}
      <Card title="Recent Runs" size="small" style={{ marginTop: 16 }}>
        <Table<RunListItem>
          dataSource={summary.recent_runs}
          columns={runColumns(setSelectedRunId)}
          rowKey="run_id"
          size="small"
          pagination={false}
          scroll={{ x: 900 }}
        />
      </Card>

      {/* Run Detail Drawer */}
      <RunDetailDrawer
        runId={selectedRunId}
        onClose={() => setSelectedRunId(null)}
      />
    </div>
  );
};

const ProjectCard: React.FC<{ project: ProjectStatus }> = ({ project }) => {
  const passRate = project.avg_pass_rate != null ? project.avg_pass_rate : null;
  const isHealthy = project.last_healthy === true;

  return (
    <Card
      size="small"
      style={{
        borderLeft: `3px solid ${isHealthy ? '#52c41a' : project.last_healthy === false ? '#ff4d4f' : '#d9d9d9'}`,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Badge status={isHealthy ? 'success' : project.last_healthy === false ? 'error' : 'default'} />
          <Text strong style={{ fontSize: 13 }}>
            {project.project_name}
          </Text>
        </Space>
        {project.recent_failures > 0 && (
          <Tag color="red" style={{ margin: 0 }}>
            {project.recent_failures} fail
          </Tag>
        )}
      </div>
      <div style={{ marginTop: 8 }}>
        {passRate != null ? (
          <Tooltip title={`Average pass rate across ${project.total_runs} runs`}>
            <Progress
              percent={Number(passRate.toFixed(1))}
              size="small"
              strokeColor={passRate >= 80 ? '#52c41a' : passRate >= 50 ? '#faad14' : '#ff4d4f'}
            />
          </Tooltip>
        ) : (
          <Text type="secondary" style={{ fontSize: 12 }}>
            No test data
          </Text>
        )}
      </div>
      {project.last_checked_at && (
        <Text type="secondary" style={{ fontSize: 11 }}>
          {dayjs(project.last_checked_at).format('MM/DD HH:mm')}
        </Text>
      )}
    </Card>
  );
};

const runColumns = (
  onClickRun: (runId: string) => void,
): ColumnsType<RunListItem> => [
  {
    title: 'Run ID',
    dataIndex: 'run_id',
    key: 'run_id',
    width: 200,
    render: (runId: string) => (
      <Button type="link" size="small" onClick={() => onClickRun(runId)} style={{ padding: 0 }}>
        {runId}
      </Button>
    ),
  },
  {
    title: 'Started',
    dataIndex: 'started_at',
    key: 'started_at',
    width: 150,
    render: (v: string) => dayjs(v).format('YYYY-MM-DD HH:mm'),
  },
  {
    title: 'Duration',
    dataIndex: 'duration_ms',
    key: 'duration_ms',
    width: 100,
    render: (v: number) => formatDuration(v),
  },
  {
    title: 'Projects',
    key: 'projects',
    width: 100,
    render: (_: unknown, record: RunListItem) => (
      <Tooltip title={`${record.healthy_projects} healthy / ${record.total_projects} total`}>
        <Space size={4}>
          <ProjectOutlined />
          <span>
            {record.healthy_projects}/{record.total_projects}
          </span>
        </Space>
      </Tooltip>
    ),
  },
  {
    title: 'Tests',
    key: 'tests',
    width: 180,
    render: (_: unknown, record: RunListItem) => {
      const passRate =
        record.total_tests > 0
          ? ((record.total_passed / record.total_tests) * 100).toFixed(1)
          : '0';
      return (
        <Space size={4}>
          <Tag color="green" icon={<CheckCircleOutlined />}>
            {record.total_passed}
          </Tag>
          <Tag color="red" icon={<CloseCircleOutlined />}>
            {record.total_failed}
          </Tag>
          <Text type="secondary" style={{ fontSize: 12 }}>
            ({passRate}%)
          </Text>
        </Space>
      );
    },
  },
  {
    title: 'Pass Rate',
    key: 'pass_rate',
    width: 120,
    render: (_: unknown, record: RunListItem) => {
      const rate =
        record.total_tests > 0
          ? (record.total_passed / record.total_tests) * 100
          : 0;
      return (
        <Progress
          percent={Number(rate.toFixed(1))}
          size="small"
          strokeColor={rate >= 80 ? '#52c41a' : rate >= 50 ? '#faad14' : '#ff4d4f'}
        />
      );
    },
  },
];

export default DashboardPage;
