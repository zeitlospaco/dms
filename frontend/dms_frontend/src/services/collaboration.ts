interface CursorPosition {
  x: number;
  y: number;
  selection?: {
    start: number;
    end: number;
  };
}

interface DocumentChange {
  type: 'insert' | 'delete' | 'replace';
  position: number;
  content?: string;
  length?: number;
}

interface CollaborationMessage {
  type: string;
  user_id?: string;
  position?: CursorPosition;
  change?: DocumentChange;
  locked?: boolean;
  users?: string[];
  message?: string;
}

export class CollaborationService {
  private ws: WebSocket | null = null;
  private documentId: string;
  private userId: string;
  private onMessageCallback: ((message: CollaborationMessage) => void) | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(documentId: string, userId: string) {
    this.documentId = documentId;
    this.userId = userId;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/collaboration/${this.documentId}/ws/${this.userId}`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          if (this.onMessageCallback) {
            this.onMessageCallback(message);
          }
        };

        this.ws.onclose = () => {
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              this.connect();
            }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onMessage(callback: (message: CollaborationMessage) => void): void {
    this.onMessageCallback = callback;
  }

  updateCursor(position: CursorPosition): void {
    this.sendMessage({
      type: 'cursor',
      position
    });
  }

  makeChange(change: DocumentChange): void {
    this.sendMessage({
      type: 'change',
      change
    });
  }

  async lockDocument(): Promise<boolean> {
    this.sendMessage({ type: 'lock' });
    return new Promise((resolve) => {
      const handleResponse = (message: CollaborationMessage) => {
        if (message.type === 'lock_response') {
          this.onMessageCallback = this.onMessageCallback;  // Restore original callback
          resolve(message.locked || false);
        }
      };
      this.onMessageCallback = handleResponse;
    });
  }

  async unlockDocument(): Promise<boolean> {
    this.sendMessage({ type: 'unlock' });
    return new Promise((resolve) => {
      const handleResponse = (message: CollaborationMessage) => {
        if (message.type === 'unlock_response') {
          this.onMessageCallback = this.onMessageCallback;  // Restore original callback
          resolve(!message.locked);
        }
      };
      this.onMessageCallback = handleResponse;
    });
  }

  private sendMessage(message: Partial<CollaborationMessage>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...message,
        user_id: this.userId
      }));
    } else {
      console.warn('WebSocket is not connected');
    }
  }
}

export const createCollaborationService = (documentId: string, userId: string): CollaborationService => {
  return new CollaborationService(documentId, userId);
};
