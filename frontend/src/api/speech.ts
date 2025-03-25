import request from '@/utils/request'
import { AxiosResponse } from 'axios';

export const speechToText = (audioFile: File): Promise<AxiosResponse<{ text: string }>> => {
  const formData = new FormData()
  formData.append('audio', audioFile)
  
  return request({
    url: '/api/whisper/speech-to-text',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}