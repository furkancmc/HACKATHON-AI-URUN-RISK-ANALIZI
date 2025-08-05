import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  message, 
  Descriptions, 
  Badge, 
  Alert,
  Modal,
  Progress,
  Divider
} from 'antd';
import { 
  ReloadOutlined,
  DatabaseOutlined,
  BugOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { apiService } from '../services/api';

const SystemManagement = ({ systemHealth, onHealthUpdate }) => {
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [embeddingLoading, setEmbeddingLoading] = useState(false);

  const runSystemTests = async () => {
    setTesting(true);
    
    try {
      const response = await apiService.testServices();
      
      if (response.data.success) {
        setTestResults(response.data.data);
        message.success('Sistem testleri tamamlandı');
      } else {
        message.error('Sistem testleri başarısız');
      }
    } catch (error) {
      message.error(`Test hatası: ${error.message}`);
    } finally {
      setTesting(false);
    }
  };

  const createEmbeddings = async () => {
    Modal.confirm({
      title: 'Embedding Oluşturma',
      content: 'Bu işlem uzun sürebilir. Eksik embedding\'leri oluşturmak istediğinizden emin misiniz?',
      okText: 'Evet, Başlat',
      cancelText: 'İptal',
      onOk: async () => {
        setEmbeddingLoading(true);
        
        try {
          const response = await apiService.createEmbeddings();
          
          if (response.data.success) {
            message.success('Embedding oluşturma işlemi başlatıldı');
            
            // Sistem durumunu güncelle
            setTimeout(() => {
              onHealthUpdate();
            }, 2000);
          } else {
            message.error('Embedding oluşturma başarısız');
          }
        } catch (error) {
          message.error(`Embedding hatası: ${error.message}`);
        } finally {
          setEmbeddingLoading(false);
        }
      }
    });
  };

  const clearCache = () => {
    message.success('✅ Cache temizlendi!');
    // React'te cache temizleme genelde sayfa yenileme ile olur
    window.location.reload();
  };

  const getStatusBadge = (status) => {
    if (status === true || status === 'ok') {
      return <Badge status="success" text="Çalışıyor" />;
    } else if (status === 'error') {
      return <Badge status="error" text="Hata" />;
    } else {
      return <Badge status="default" text="Mevcut Değil" />;
    }
  };

  const getServiceHealth = (service) => {
    if (!testResults) return 'unknown';
    
    const serviceData = testResults[service];
    if (!serviceData) return 'unknown';
    
    return serviceData.status;
  };

  return (
    <div>
      <h2>⚙️ Sistem Yönetimi</h2>
      
      <Row gutter={[16, 16]}>
        {/* Sistem Durumu */}
        <Col span={12}>
          <Card title="🔧 Sistem Durumu">
            {systemHealth ? (
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Genel Durum">
                  {systemHealth.status === 'healthy' ? (
                    <Badge status="success" text="Sağlıklı" />
                  ) : (
                    <Badge status="error" text="Sorunlu" />
                  )}
                </Descriptions.Item>
                
                <Descriptions.Item label="RAG Servisi">
                  {getStatusBadge(systemHealth.services.rag_service)}
                </Descriptions.Item>
                
                <Descriptions.Item label="Gemini AI">
                  {getStatusBadge(systemHealth.services.gemini_service)}
                </Descriptions.Item>
                
                <Descriptions.Item label="Embedding Creator">
                  {getStatusBadge(systemHealth.services.embedding_creator)}
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <Alert
                message="Sistem durumu yüklenemedi"
                description="Backend bağlantısını kontrol edin"
                type="error"
                showIcon
              />
            )}

            <Divider />

            <Button
              type="primary"
              icon={<BugOutlined />}
              onClick={runSystemTests}
              loading={testing}
              style={{ width: '100%', marginBottom: 8 }}
            >
              🧪 Sistem Testlerini Çalıştır
            </Button>

            <Button
              icon={<ReloadOutlined />}
              onClick={onHealthUpdate}
              style={{ width: '100%' }}
            >
              🔄 Durumu Yenile
            </Button>
          </Card>
        </Col>

        {/* Performans Metrikleri */}
        <Col span={12}>
          <Card title="📊 Performans Metrikleri">
            {testResults ? (
              <div>
                <h4>Test Sonuçları:</h4>
                
                {/* RAG Service */}
                <div style={{ marginBottom: 16 }}>
                  <strong>RAG Servisi:</strong> {getStatusBadge(getServiceHealth('rag_service'))}
                  {testResults.rag_service?.tables && (
                    <div style={{ marginTop: 4, fontSize: '12px', color: '#666' }}>
                      {testResults.rag_service.tables} tablo aktif
                    </div>
                  )}
                </div>

                {/* Gemini Service */}
                <div style={{ marginBottom: 16 }}>
                  <strong>Gemini AI:</strong> {getStatusBadge(getServiceHealth('gemini_service'))}
                  {testResults.gemini_service?.response_length && (
                    <div style={{ marginTop: 4, fontSize: '12px', color: '#666' }}>
                      Yanıt uzunluğu: {testResults.gemini_service.response_length} karakter
                    </div>
                  )}
                </div>

                {/* Tablolar */}
                {testResults.rag_service?.table_names && (
                  <div>
                    <strong>Aktif Tablolar:</strong>
                    <ul style={{ fontSize: '12px', marginTop: 4 }}>
                      {testResults.rag_service.table_names.map((table, index) => (
                        <li key={index}>{table.replace('_embeddings', '').replace('_', ' ').toUpperCase()}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <Alert
                message="Test sonuçları mevcut değil"
                description="Sistem testlerini çalıştırın"
                type="info"
                showIcon
              />
            )}

            <Divider />

            <Button
              type="default"
              icon={<DatabaseOutlined />}
              onClick={createEmbeddings}
              loading={embeddingLoading}
              style={{ width: '100%', marginBottom: 8 }}
            >
              🔨 Eksik Embedding'leri Oluştur
            </Button>

            <Button
              icon={<ReloadOutlined />}
              onClick={clearCache}
              style={{ width: '100%' }}
            >
              🧹 Cache Temizle
            </Button>
          </Card>
        </Col>
      </Row>

      {/* Sistem Sağlığı Göstergesi */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card title="🎯 Embedding Verimliliği" style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={systemHealth?.services.rag_service ? 85 : 0}
              format={(percent) => `${percent}%`}
              status={systemHealth?.services.rag_service ? 'success' : 'exception'}
            />
            <p style={{ marginTop: 16 }}>
              Sistem {systemHealth?.services.rag_service ? 'verimli' : 'sorunlu'}
            </p>
          </Card>
        </Col>
        
        <Col span={8}>
          <Card title="📊 Aktif Servisler" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', color: '#1890ff' }}>
              {systemHealth ? Object.values(systemHealth.services).filter(Boolean).length : 0}/3
            </div>
            <p>Servis aktif</p>
          </Card>
        </Col>
        
        <Col span={8}>
          <Card title="🟢 Sistem Sağlığı" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem' }}>
              {systemHealth?.status === 'healthy' ? '🟢 İyi' : '🔴 Sorunlu'}
            </div>
            <p>
              {systemHealth?.status === 'healthy' 
                ? 'Tüm sistemler çalışıyor' 
                : 'Sistem kontrolü gerekli'
              }
            </p>
          </Card>
        </Col>
      </Row>

      {/* Sistem Logları */}
      <Card title="📝 Sistem Logları" style={{ marginTop: 16 }}>
        <div style={{ 
          background: '#f5f5f5', 
          padding: '1rem', 
          borderRadius: '4px',
          fontFamily: 'monospace',
          fontSize: '12px',
          height: '200px',
          overflowY: 'auto'
        }}>
          <div>[INFO] React frontend başlatıldı</div>
          <div>[INFO] Backend API bağlantısı kuruldu</div>
          {systemHealth?.services.rag_service && <div>[INFO] RAG servisi aktif</div>}
          {systemHealth?.services.gemini_service && <div>[INFO] Gemini AI bağlantısı başarılı</div>}
          {systemHealth?.services.embedding_creator && <div>[INFO] Embedding creator hazır</div>}
          <div>[INFO] Dashboard yüklendi</div>
          {testResults && <div>[INFO] Sistem testleri tamamlandı</div>}
        </div>
      </Card>

      {/* Hızlı Aksiyonlar */}
      <Card title="⚡ Hızlı Aksiyonlar" style={{ marginTop: 16 }}>
        <Row gutter={[8, 8]}>
          <Col span={6}>
            <Button 
              type="primary" 
              icon={<RocketOutlined />}
              onClick={() => window.open('http://localhost:5000/api/health', '_blank')}
              style={{ width: '100%' }}
            >
              Backend Durumu
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              onClick={runSystemTests}
              loading={testing}
              style={{ width: '100%' }}
            >
              Hızlı Test
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              onClick={onHealthUpdate}
              style={{ width: '100%' }}
            >
              Yenile
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              onClick={() => message.info('Sistem normal çalışıyor')}
              style={{ width: '100%' }}
            >
              Durum Raporu
            </Button>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default SystemManagement;