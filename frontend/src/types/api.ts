export interface ApiParam {
  name: string;
  type: string;
  required: boolean;
  description: string;
  defaultValue?: string;
}

export interface ApiEndpoint {
  id: string;
  method: 'GET' | 'POST' | 'DELETE';
  path: string;
  category: string;
  description: string;
  params?: ApiParam[];
  requestSchema?: string;
  responseSchema?: string;
  curlExample: string;
  pythonExample: string;
  jsExample: string;
}
