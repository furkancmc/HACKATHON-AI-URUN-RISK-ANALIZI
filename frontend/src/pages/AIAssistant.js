import React, { useState, useRef, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  message, 
  Space, 
  Avatar,
  Divider
} from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined,
  ClearOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';

const { TextArea } = Input;

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Merhaba! 👋 Ben sizin satıcı koçunuzum. Ürün risk analizleri, satış stratejileri, fiyatlandırma önerileri, rekabet durumu ve karlılık değerlendirmesi konularında size özel tavsiyeler verebilirim. Hangi ürünü satmayı düşünüyorsunuz veya mevcut satışlarınızı nasıl artırabiliriz?'
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) {
      message.warning('Lütfen bir mesaj yazın');
      return;
    }

    const userMessage = currentMessage.trim();
    setCurrentMessage('');
    
    // Kullanıcı mesajını ekle
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await apiService.chatWithAI(userMessage);
      
      if (response.data.success) {
        // AI yanıtını ekle
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: response.data.data.response 
        }]);
        
        if (response.data.data.context_products > 0) {
          message.success(`${response.data.data.context_products} ilgili ürün bulundu ve analiz edildi`);
        }
      } else {
        message.error('AI yanıtı alınamadı');
      }
    } catch (error) {
      message.error(`AI hatası: ${error.message}`);
      
      // Hata mesajını ekle
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `❌ Üzgünüm, bir hata oluştu: ${error.message}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Merhaba! 👋 Ben sizin satıcı koçunuzum. Ürün risk analizleri, satış stratejileri, fiyatlandırma önerileri, rekabet durumu ve karlılık değerlendirmesi konularında size özel tavsiyeler verebilirim. Hangi ürünü satmayı düşünüyorsunuz veya mevcut satışlarınızı nasıl artırabiliriz?'
      }
    ]);
    message.info('Sohbet geçmişi temizlendi');
  };

  const exampleQuestions = [
    "Samsung klima satacağım, ne önerirsin?",
    "Hangi ürünlerde daha yüksek kâr marjı var?",
    "Fiyatlandırma stratejimi nasıl optimize edebilirim?",
    "Rekabetçi avantajımı nasıl artırabilirim?",
    "Stok yönetimi için hangi ürünlere odaklanmalıyım?"
  ];

  const handleExampleClick = (question) => {
    setCurrentMessage(question);
  };

  return (
    <div>
      <Card 
        title="🤖 AI Satış Danışmanı"
        extra={
          <Button 
            icon={<ClearOutlined />} 
            onClick={clearChat}
            type="text"
          >
            Temizle
          </Button>
        }
      >
        <div style={{ marginBottom: 16 }}>
          <p><strong>Satıcı odaklı AI danışmanınız size yardımcı olmaya hazır!</strong></p>
          <p>Ürünler hakkında risk analizi, satış stratejileri, fiyatlandırma önerileri ve rekabet analizi yapabilirsiniz.</p>
          
          <div style={{ marginTop: 16 }}>
            <strong>Örnek Sorular:</strong>
            <ul>
              <li>"Bu ürünü satmak riskli mi?"</li>
              <li>"Hangi ürünler daha karlı?"</li>
              <li>"Fiyat stratejim nasıl olmalı?"</li>
              <li>"Rekabet durumu nasıl?"</li>
            </ul>
          </div>
        </div>

        {/* Chat Container */}
        <div className="chat-container">
          {messages.map((message, index) => (
            <div key={index} className={`chat-message ${message.role}`}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <Avatar 
                  icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  style={{ 
                    backgroundColor: message.role === 'user' ? '#1890ff' : '#52c41a',
                    flexShrink: 0
                  }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    lineHeight: '1.6',
                    fontSize: '14px'
                  }}>
                    {message.content}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="chat-message assistant">
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <Avatar 
                  icon={<RobotOutlined />}
                  style={{ backgroundColor: '#52c41a' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ color: '#666' }}>
                    🤖 Düşünüyorum...
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ marginTop: 16 }}>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Sorunuzu yazın... (Enter ile gönder, Shift+Enter ile yeni satır)"
              autoSize={{ minRows: 2, maxRows: 4 }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              loading={loading}
              style={{ height: 'auto' }}
            >
              Gönder
            </Button>
          </Space.Compact>
        </div>

        <Divider />

        {/* Example Questions */}
        <div>
          <h4>💡 Satıcı İçin Örnek Sorular</h4>
          <Space wrap>
            {exampleQuestions.map((question, index) => (
              <Button
                key={index}
                size="small"
                onClick={() => handleExampleClick(question)}
                disabled={loading}
              >
                {question}
              </Button>
            ))}
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default AIAssistant;