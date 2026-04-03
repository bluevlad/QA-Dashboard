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
  Select,
  Button,
  Space,
  Typography,
  Empty,
} from 'antd';
import {
  ThunderboltOutlined,
  CloudOutlined,
  DesktopOutlined,
  ReloadOutlined,
  SwapOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { fetchEngineStats, fetchEngineTrend } from '../services/api';
import type {
  EngineComparisonData,
  EngineDailyTrendPoint,
} from '../types/dashboard';

const { Text, Title } = Typography;

const ENGINE_COLORS: Record<string, string> = {
  'claude-code-cli': '#722ed1',
  'local-llm': '#13c2c2',
};

const ENGINE_LABELS: Record<string, string> = {
  'claude-code-cli': 'Claude Code CLI',
  'local-llm': 'Local LLM (Ollama)',
};

const formatDuration = (ms: number | null): string => {
  if (ms === null || ms === undefined) return '-';
  if (ms < 1000) return `${ms}ms`;
  const sec = Math.round(ms / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.floor(sec / 60);
  const remSec = sec % 60;
  return `${min}m ${remSec}s`;
};

const EngineComparisonPage: React.FC = () => {
  const [data, setData] = useState<EngineComparisonData | null>(null);
  const [trend, setTrend] = useState<EngineDailyTrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, trendData] = await Promise.all([
        fetchEngineStats(days),
        fetchEngineTrend(days),
      ]);
      setData(statsData);
      setTrend(trendData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load engine stats');
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="Loading engine statistics..." />
      </div>
    );
  }

  if (error) {
    return <Alert type="error" message="Error" description={error} showIcon />;
  }

  if (!data || data.engines.length === 0) {
    return <Empty description="No engine data available yet. Fix results with engine metadata will appear here." />;
  }

  // Prepare bar chart data
  const barData = data.engines.map((e) => ({
    engine: ENGINE_LABELS[e.engine_type] ?? e.engine_type,
    succeeded: e.success_count,
    failed: e.failure_count,
    skipped: e.skipped_count,
  }));

  // Prepare trend chart data (pivot by date, merge engines)
  const trendByDate: Record<string, Record<string, number | string>> = {};
  for (const point of trend) {
    if (!trendByDate[point.date]) {
      trendByDate[point.date] = { date: point.date };
    }
    const label = ENGINE_LABELS[point.engine_type] ?? point.engine_type;
    trendByDate[point.date][`${label} Duration`] = point.avg_duration_ms ?? 0;
    trendByDate[point.date][`${label} Success`] = point.succeeded;
  }
  const trendData = Object.values(trendByDate).sort((a, b) =>
    String(a.date).localeCompare(String(b.date)),
  );

  // Project breakdown table data
  const projectTableData: Array<{
    key: string;
    engine: string;
    project: string;
    total: number;
    succeeded: number;
    failed: number;
    successRate: number;
    avgDuration: number | null;
  }> = [];
  for (const [engine, projects] of Object.entries(data.by_project)) {
    for (const p of projects) {
      projectTableData.push({
        key: `${engine}-${p.project_name}`,
        engine,
        project: p.project_name,
        total: p.total,
        succeeded: p.succeeded,
        failed: p.failed,
        successRate: p.success_rate,
        avgDuration: p.avg_duration_ms,
      });
    }
  }

  const engineNames = data.engines.map(
    (e) => ENGINE_LABELS[e.engine_type] ?? e.engine_type,
  );

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <Title level={4} style={{ margin: 0 }}>
            <ThunderboltOutlined /> Engine Comparison
          </Title>
        </Col>
        <Col>
          <Space>
            <Select
              value={days}
              onChange={setDays}
              options={[
                { value: 7, label: '7 Days' },
                { value: 14, label: '14 Days' },
                { value: 30, label: '30 Days' },
                { value: 90, label: '90 Days' },
              ]}
              style={{ width: 120 }}
            />
            <Button icon={<ReloadOutlined />} onClick={loadData}>
              Refresh
            </Button>
          </Space>
        </Col>
      </Row>

      {/* Engine Summary Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {data.engines.map((engine) => (
          <Col key={engine.engine_type} xs={24} md={12}>
            <Card
              title={
                <Space>
                  {engine.engine_type === 'claude-code-cli' ? (
                    <CloudOutlined style={{ color: ENGINE_COLORS['claude-code-cli'] }} />
                  ) : (
                    <DesktopOutlined style={{ color: ENGINE_COLORS['local-llm'] }} />
                  )}
                  <span>{ENGINE_LABELS[engine.engine_type] ?? engine.engine_type}</span>
                  <Tag>{engine.model_name}</Tag>
                </Space>
              }
              bordered
            >
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic title="Total Fixes" value={engine.total_fixes} />
                </Col>
                <Col span={8}>
                  <div style={{ textAlign: 'center' }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      Success Rate
                    </Text>
                    <Progress
                      type="circle"
                      percent={engine.success_rate}
                      size={80}
                      strokeColor={
                        engine.success_rate >= 80
                          ? '#52c41a'
                          : engine.success_rate >= 50
                            ? '#faad14'
                            : '#ff4d4f'
                      }
                      format={(p) => `${p}%`}
                    />
                  </div>
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Avg Duration"
                    value={formatDuration(engine.avg_duration_ms)}
                  />
                  <Statistic
                    title="Avg Inference"
                    value={formatDuration(engine.avg_inference_ms)}
                    style={{ marginTop: 8 }}
                  />
                </Col>
              </Row>
              {engine.fallback_count > 0 && (
                <div style={{ marginTop: 12 }}>
                  <Tag icon={<SwapOutlined />} color="warning">
                    Fallback to Claude: {engine.fallback_count} times
                  </Tag>
                </div>
              )}
            </Card>
          </Col>
        ))}
      </Row>

      {/* Success/Failure Comparison Bar Chart */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="Fix Results by Engine">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="engine" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="succeeded" fill="#52c41a" name="Succeeded" />
                <Bar dataKey="failed" fill="#ff4d4f" name="Failed" />
                <Bar dataKey="skipped" fill="#d9d9d9" name="Skipped" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Duration Trend Line Chart */}
      {trendData.length > 0 && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Card title="Daily Average Duration Trend">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis
                    tickFormatter={(v: number) => formatDuration(v)}
                  />
                  <RechartsTooltip
                    formatter={(value: number) => formatDuration(value)}
                  />
                  <Legend />
                  {engineNames.map((name, i) => (
                    <Line
                      key={name}
                      type="monotone"
                      dataKey={`${name} Duration`}
                      stroke={Object.values(ENGINE_COLORS)[i] ?? '#8884d8'}
                      dot={false}
                      name={name}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>
      )}

      {/* Per-Project Breakdown Table */}
      <Card title="Per-Project Breakdown">
        <Table
          dataSource={projectTableData}
          rowKey="key"
          pagination={false}
          size="small"
          columns={[
            {
              title: 'Engine',
              dataIndex: 'engine',
              render: (val: string) => (
                <Tag color={ENGINE_COLORS[val] ?? 'default'}>
                  {ENGINE_LABELS[val] ?? val}
                </Tag>
              ),
            },
            { title: 'Project', dataIndex: 'project' },
            { title: 'Total', dataIndex: 'total', align: 'right' as const },
            {
              title: 'Succeeded',
              dataIndex: 'succeeded',
              align: 'right' as const,
              render: (v: number) => <Text type="success">{v}</Text>,
            },
            {
              title: 'Failed',
              dataIndex: 'failed',
              align: 'right' as const,
              render: (v: number) =>
                v > 0 ? <Text type="danger">{v}</Text> : <Text>0</Text>,
            },
            {
              title: 'Success Rate',
              dataIndex: 'successRate',
              align: 'right' as const,
              render: (v: number) => (
                <Progress
                  percent={v}
                  size="small"
                  strokeColor={
                    v >= 80 ? '#52c41a' : v >= 50 ? '#faad14' : '#ff4d4f'
                  }
                  format={(p) => `${p}%`}
                />
              ),
            },
            {
              title: 'Avg Duration',
              dataIndex: 'avgDuration',
              align: 'right' as const,
              render: (v: number | null) => formatDuration(v),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default EngineComparisonPage;
