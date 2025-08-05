import React, { useState, useEffect } from 'react';
import { Layout, Tabs, message, ConfigProvider, theme } from 'antd';
import { 
  SearchOutlined, 
  DashboardOutlined, 
  RobotOutlined, 
  SettingOutlined 
} from '@ant-design/icons';
import ProductSearch from './pages/ProductSearch';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import SystemManagement from './pages/SystemManagement';
import { apiService } from './services/api';

const { Header, Content } = Layout;
const { TabPane } = Tabs;

function App() {
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await apiService.checkHealth();
      setSystemHealth(response.data);
      
      if (!response.data.services.rag_service || !response.data.services.gemini_service) {
        message.warning('Bazı servisler çalışmıyor. Sistem Yönetimi sekmesini kontrol edin.');
      }
    } catch (error) {
      message.error('Backend bağlantısı kurulamadı. Lütfen backend sunucusunu başlatın.');
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ConfigProvider
              theme={{
          algorithm: theme.darkAlgorithm,
          token: {
            colorBgContainer: '#1e1e1e',
            colorBgElevated: '#262626',
            colorBgLayout: '#121212',
            colorBgSpotlight: '#262626',
            colorBorder: '#444',
            colorBorderSecondary: '#333',
            colorText: '#e0e0e0',
            colorTextSecondary: '#d9d9d9',
            colorTextTertiary: '#b0b0b0',
            colorPrimary: '#1890ff',
            colorPrimaryHover: '#40a9ff',
            colorPrimaryActive: '#096dd9',
            colorSuccess: '#52c41a',
            colorWarning: '#faad14',
            colorError: '#ff4d4f',
            colorInfo: '#1890ff',
          }
        }}
    >
              <Layout style={{ minHeight: '100vh', background: '#121212' }}>
          <Header style={{ 
            background: '#1e1e1e', 
            padding: 0,
            height: 'auto',
            borderBottom: '1px solid #444'
          }}>
          <div className="main-header">
            <h1>🤖 AI Destekli Satıcı Risk Analiz Sistemi</h1>
            <p>Satıcılar için akıllı ürün risk analizi, karlılık değerlendirmesi ve satış stratejileri</p>
          </div>
        </Header>
        
        <Content style={{ 
          padding: '20px',
          background: '#121212'
        }}>
          <div style={{
            background: '#1e1e1e',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            border: '1px solid #444'
          }}>
            <Tabs 
              defaultActiveKey="1" 
              size="large"
              style={{ minHeight: '70vh' }}
            >
              <TabPane 
                tab={<span><SearchOutlined />Ürün Risk Arama</span>} 
                key="1"
              >
                <ProductSearch />
              </TabPane>
              
              <TabPane 
                tab={<span><DashboardOutlined />Satış Dashboard</span>} 
                key="2"
              >
                <Dashboard />
              </TabPane>
              
              <TabPane 
                tab={<span><RobotOutlined />AI Satış Danışmanı</span>} 
                key="3"
              >
                <AIAssistant />
              </TabPane>
              
              <TabPane 
                tab={<span><SettingOutlined />Sistem Yönetimi</span>} 
                key="4"
              >
                <SystemManagement systemHealth={systemHealth} onHealthUpdate={checkSystemHealth} />
              </TabPane>
            </Tabs>
          </div>
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;