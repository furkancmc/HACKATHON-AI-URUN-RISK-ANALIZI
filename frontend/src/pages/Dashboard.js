import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Table, 
  message, 
  Spin,
  Progress,
  Tag
} from 'antd';
import { 
  ShoppingOutlined, 
  DatabaseOutlined, 
  DollarOutlined, 
  StarOutlined 
} from '@ant-design/icons';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { apiService } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([]);
  const [salesData, setSalesData] = useState([]);
  const [totalMetrics, setTotalMetrics] = useState({
    totalProducts: 0,
    totalEmbeddings: 0,
    avgPrice: 0,
    avgRating: 0,
    totalTables: 0
  });

  useEffect(() => {
    fetchTableStats();
    fetchSalesData();
  }, []);

  const fetchTableStats = async () => {
    try {
      const response = await apiService.getTableStats();
      
      if (response.data.success) {
        const tableStats = response.data.data;
        setStats(tableStats);
        
        // Toplam metrikleri hesapla
        const totalProducts = tableStats.reduce((sum, table) => sum + table.total_products, 0);
        const totalEmbeddings = tableStats.reduce((sum, table) => sum + table.embeddings_count, 0);
        const avgPrice = totalProducts > 0 
          ? tableStats.reduce((sum, table) => sum + (table.avg_price * table.total_products), 0) / totalProducts
          : 0;
        const avgRating = totalProducts > 0
          ? tableStats.reduce((sum, table) => sum + (table.avg_rating * table.total_products), 0) / totalProducts
          : 0;
        
        setTotalMetrics({
          totalProducts,
          totalEmbeddings,
          avgPrice,
          avgRating,
          totalTables: tableStats.length
        });
        
        message.success('Dashboard verileri yüklendi');
      } else {
        message.error('Dashboard verileri yüklenemedi');
      }
    } catch (error) {
      message.error(`Dashboard hatası: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchSalesData = async () => {
    try {
      const response = await apiService.getSalesData();
      
      if (response.data.success) {
        setSalesData(response.data.data);
        message.success('Satış verileri yüklendi');
      } else {
        message.error('Satış verileri yüklenemedi');
      }
    } catch (error) {
      message.error(`Satış verileri hatası: ${error.message}`);
    }
  };

  const tableColumns = [
    {
      title: 'Tablo Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Toplam Ürün',
      dataIndex: 'total_products',
      key: 'total_products',
      render: (value) => value.toLocaleString()
    },
    {
      title: 'Embedding Sayısı',
      dataIndex: 'embeddings_count',
      key: 'embeddings_count',
      render: (value) => value.toLocaleString()
    },
    {
      title: 'Kapsama (%)',
      dataIndex: 'embedding_coverage',
      key: 'embedding_coverage',
      render: (value) => (
        <Progress 
          percent={value} 
          size="small" 
          status={value === 100 ? 'success' : value > 50 ? 'active' : 'exception'}
        />
      )
    },
    {
      title: 'Ort. Fiyat (₺)',
      dataIndex: 'avg_price',
      key: 'avg_price',
      render: (value) => `₺${value.toLocaleString()}`
    },
    {
      title: 'Ort. Rating',
      dataIndex: 'avg_rating',
      key: 'avg_rating',
      render: (value) => `${value.toFixed(1)}⭐`
    }
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <Spin size="large" />
        <p style={{ marginTop: 16 }}>Dashboard yükleniyor...</p>
      </div>
    );
  }

  return (
    <div>
      <h2>📊 Satıcı Dashboard - Risk ve Karlılık Analizi</h2>
      
      {/* Genel Metrikler */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Toplam Ürün"
              value={totalMetrics.totalProducts}
              prefix={<ShoppingOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="AI Embeddings"
              value={totalMetrics.totalEmbeddings}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Ortalama Fiyat"
              value={totalMetrics.avgPrice}
              prefix={<DollarOutlined />}
              suffix="₺"
              precision={0}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Ortalama Rating"
              value={totalMetrics.avgRating}
              prefix={<StarOutlined />}
              suffix="⭐"
              precision={1}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Grafikler */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="📊 Tablo Bazında Ürün Dağılımı">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip formatter={(value) => value.toLocaleString()} />
                <Legend />
                <Bar dataKey="total_products" fill="#8884d8" name="Ürün Sayısı" />
                <Bar dataKey="embeddings_count" fill="#82ca9d" name="Embedding Sayısı" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card title="🥧 Ürün Dağılım Oranları">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total_products"
                >
                  {stats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => value.toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Detaylı Tablo */}
      <Card title="📋 Detaylı İstatistikler">
        <Table
          columns={tableColumns}
          dataSource={stats.map((item, index) => ({ ...item, key: index }))}
          pagination={false}
          size="middle"
        />
      </Card>

      {/* Satış Verileri Tablosu */}
      {salesData.length > 0 && (
        <Card title="💰 Satış Verileri" style={{ marginTop: 24 }}>
          <Table
            columns={[
              {
                title: 'Ürün Adı',
                dataIndex: 'product_name',
                key: 'product_name',
                render: (text) => <strong>{text}</strong>
              },
              {
                title: 'Marka',
                dataIndex: 'brand',
                key: 'brand',
                render: (text) => <Tag color="blue">{text}</Tag>
              },
              {
                title: 'Fiyat (₺)',
                dataIndex: 'price',
                key: 'price',
                render: (value) => <span style={{ color: '#52c41a', fontWeight: 'bold' }}>₺{value.toLocaleString()}</span>
              },
              {
                title: 'Rating',
                dataIndex: 'rating',
                key: 'rating',
                render: (value) => (
                  <div>
                    <span style={{ color: '#faad14' }}>{value.toFixed(1)}⭐</span>
                    <Progress percent={value * 20} size="small" style={{ marginTop: 4 }} />
                  </div>
                )
              },
              {
                title: 'Risk Skoru',
                dataIndex: 'risk_score',
                key: 'risk_score',
                render: (value) => (
                  <Tag color={value > 7 ? 'red' : value > 4 ? 'orange' : 'green'}>
                    {value}/10
                  </Tag>
                )
              },
              {
                title: 'Satıcı',
                dataIndex: 'seller',
                key: 'seller',
                render: (text) => <span style={{ fontSize: '12px' }}>{text}</span>
              },
              {
                title: 'Stok Durumu',
                dataIndex: 'stock_status',
                key: 'stock_status',
                render: (text) => (
                  <Tag color={text === 'Stokta' ? 'green' : 'red'}>
                    {text}
                  </Tag>
                )
              }
            ]}
            dataSource={salesData.map((item, index) => ({ ...item, key: index }))}
            pagination={{ pageSize: 10 }}
            size="middle"
          />
        </Card>
      )}

      {/* Sistem Sağlığı */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="🎯 Embedding Verimliliği" style={{ textAlign: 'center' }}>
            <Progress
              type="circle"
              percent={totalMetrics.totalProducts > 0 
                ? Math.round((totalMetrics.totalEmbeddings / totalMetrics.totalProducts) * 100)
                : 0
              }
              format={(percent) => `${percent}%`}
            />
            <p style={{ marginTop: 16 }}>
              {totalMetrics.totalEmbeddings.toLocaleString()} / {totalMetrics.totalProducts.toLocaleString()} ürün
            </p>
          </Card>
        </Col>
        
        <Col span={8}>
          <Card title="📊 Aktif Tablolar" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', color: '#1890ff' }}>
              {totalMetrics.totalTables}
            </div>
            <p>Tablo aktif</p>
          </Card>
        </Col>
        
        <Col span={8}>
          <Card title="🟢 Sistem Sağlığı" style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem' }}>
              {totalMetrics.totalTables > 0 ? '🟢 İyi' : '🔴 Sorunlu'}
            </div>
            <p>{totalMetrics.totalTables > 0 ? 'Tüm sistemler çalışıyor' : 'Sistem kontrolü gerekli'}</p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;