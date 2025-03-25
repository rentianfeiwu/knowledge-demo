import request from '../utils/request'
import type { AxiosResponse } from 'axios'

export interface SearchResult {
  filename: string;
  content: string;
  score: number;
}

export interface SearchResponse {
  ai_response: string | null;
  search_results: SearchResult[];
}

export interface FileItem {
  filename: string;
  size: number;
  upload_time: string;
  file_type: string;
}

export interface FileListResponse {
  total: number;
  items: FileItem[];
}

export const uploadFile = (formData: FormData, onProgress?: (progressEvent: any) => void) => {
  return request({
    url: 'api/knowledge/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: onProgress
  })
}

export const searchDocuments = async (query: string, searchType: string = 'hybrid'): Promise<SearchResponse> => {
  const response = await request<SearchResponse>({
    url: '/api/knowledge/search',
    method: 'get',
    params: {
      query,
      search_type: searchType
    }
  });
  return response.data;
};

export const getFileList = async (): Promise<FileListResponse> => {
  const response = await request<FileListResponse>({
    url: '/api/knowledge/files',
    method: 'get'
  });
  return response.data;
}; 