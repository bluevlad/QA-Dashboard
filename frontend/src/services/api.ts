import axios from 'axios';
import type {
  DashboardSummary,
  RunDetail,
  RunListItem,
  TrendPoint,
  DurationTrendPoint,
  ProjectStatus,
} from '../types/dashboard';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('qa_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function fetchSummary(): Promise<DashboardSummary> {
  const { data } = await api.get('/summary');
  return data;
}

export async function fetchRuns(
  page = 1,
  limit = 20,
): Promise<{ total: number; page: number; limit: number; runs: RunListItem[] }> {
  const { data } = await api.get('/runs', { params: { page, limit } });
  return data;
}

export async function fetchRunDetail(runId: string): Promise<RunDetail> {
  const { data } = await api.get(`/runs/${runId}`);
  return data;
}

export async function fetchProjects(): Promise<{ projects: ProjectStatus[] }> {
  const { data } = await api.get('/projects');
  return data;
}

export async function fetchPassRateTrend(days = 30): Promise<TrendPoint[]> {
  const { data } = await api.get('/trends/pass-rate', { params: { days } });
  return data;
}

export async function fetchDurationTrend(days = 30): Promise<DurationTrendPoint[]> {
  const { data } = await api.get('/trends/duration', { params: { days } });
  return data;
}

export default api;
