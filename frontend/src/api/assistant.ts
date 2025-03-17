
import request from '@/utils/request' 

export interface ChatResponse {
  response: string
}

export const chatWithAssistant = (
  message: string, 
  context: string[] = []
): Promise<ChatResponse> => {
  return request({
    url: 'api/chat',
    method: 'post',
    data: { message, context }
  })
} 