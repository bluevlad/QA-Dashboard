import React from 'react';
import {
  Typography,
  Tag,
  Table,
  Tabs,
  Card,
  Anchor,
  Button,
  message,
  Row,
  Col,
} from 'antd';
import { CopyOutlined } from '@ant-design/icons';
import { API_ENDPOINTS, API_CATEGORIES } from '../constants/apiEndpoints';
import type { ApiEndpoint, ApiParam } from '../types/api';

const { Title, Text, Paragraph } = Typography;

const METHOD_COLORS: Record<string, string> = {
  GET: 'blue',
  POST: 'green',
  DELETE: 'red',
};

const paramColumns = [
  { title: 'Name', dataIndex: 'name', key: 'name', render: (v: string) => <code>{v}</code> },
  { title: 'Type', dataIndex: 'type', key: 'type' },
  {
    title: 'Required',
    dataIndex: 'required',
    key: 'required',
    render: (v: boolean) => (v ? <Tag color="red">Required</Tag> : <Tag>Optional</Tag>),
  },
  { title: 'Description', dataIndex: 'description', key: 'description' },
  { title: 'Default', dataIndex: 'defaultValue', key: 'defaultValue', render: (v?: string) => v ? <code>{v}</code> : '-' },
];

function CopyButton({ text }: { text: string }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('Copied to clipboard');
    } catch {
      message.error('Copy failed');
    }
  };

  return (
    <Button
      size="small"
      icon={<CopyOutlined />}
      onClick={handleCopy}
      style={{ position: 'absolute', top: 8, right: 8 }}
    >
      Copy
    </Button>
  );
}

function CodeBlock({ code }: { code: string }) {
  return (
    <div style={{ position: 'relative' }}>
      <CopyButton text={code} />
      <pre
        style={{
          background: '#f5f5f5',
          padding: '16px',
          borderRadius: 6,
          overflow: 'auto',
          fontSize: 13,
          lineHeight: 1.6,
          margin: 0,
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
}

function EndpointCard({ endpoint }: { endpoint: ApiEndpoint }) {
  const codeTabs = [
    { key: 'curl', label: 'cURL', children: <CodeBlock code={endpoint.curlExample} /> },
    { key: 'python', label: 'Python', children: <CodeBlock code={endpoint.pythonExample} /> },
    { key: 'js', label: 'JavaScript', children: <CodeBlock code={endpoint.jsExample} /> },
  ];

  return (
    <Card
      id={endpoint.id}
      size="small"
      style={{ marginBottom: 20 }}
      title={
        <span>
          <Tag color={METHOD_COLORS[endpoint.method]}>{endpoint.method}</Tag>
          <code style={{ fontSize: 15 }}>{endpoint.path}</code>
        </span>
      }
    >
      <Paragraph>{endpoint.description}</Paragraph>

      {endpoint.params && endpoint.params.length > 0 && (
        <>
          <Title level={5}>Parameters</Title>
          <Table<ApiParam>
            columns={paramColumns}
            dataSource={endpoint.params}
            rowKey="name"
            pagination={false}
            size="small"
            bordered
          />
        </>
      )}

      {endpoint.requestSchema && (
        <>
          <Title level={5} style={{ marginTop: 16 }}>Request Body</Title>
          <CodeBlock code={endpoint.requestSchema} />
        </>
      )}

      {endpoint.responseSchema && (
        <>
          <Title level={5} style={{ marginTop: 16 }}>Response</Title>
          <CodeBlock code={endpoint.responseSchema} />
        </>
      )}

      <Title level={5} style={{ marginTop: 16 }}>Examples</Title>
      <Tabs items={codeTabs} size="small" />
    </Card>
  );
}

const ApiGuidePage: React.FC = () => {
  const anchorItems = API_CATEGORIES.map((cat) => {
    const endpoints = API_ENDPOINTS.filter((e) => e.category === cat);
    return {
      key: cat,
      href: `#category-${cat}`,
      title: `${cat} (${endpoints.length})`,
      children: endpoints.map((ep) => ({
        key: ep.id,
        href: `#${ep.id}`,
        title: (
          <span>
            <Tag color={METHOD_COLORS[ep.method]} style={{ marginRight: 4 }}>
              {ep.method}
            </Tag>
            {ep.path}
          </span>
        ),
      })),
    };
  });

  return (
    <div>
      <Title level={2}>API Guide</Title>
      <Paragraph type="secondary">
        Complete reference for all QA Dashboard API endpoints. Base URL: <code>http://localhost:9095</code>
      </Paragraph>

      <Row gutter={24}>
        <Col xs={24} lg={6}>
          <Card size="small" style={{ position: 'sticky', top: 24 }}>
            <Title level={5} style={{ marginTop: 0 }}>Table of Contents</Title>
            <Anchor
              items={anchorItems}
              affix={false}
              onClick={(e) => e.preventDefault()}
            />
          </Card>
        </Col>

        <Col xs={24} lg={18}>
          {API_CATEGORIES.map((category) => {
            const endpoints = API_ENDPOINTS.filter((e) => e.category === category);
            return (
              <div key={category} id={`category-${category}`} style={{ marginBottom: 32 }}>
                <Title level={3}>{category}</Title>
                {endpoints.map((ep) => (
                  <EndpointCard key={ep.id} endpoint={ep} />
                ))}
              </div>
            );
          })}
        </Col>
      </Row>
    </div>
  );
};

export default ApiGuidePage;
