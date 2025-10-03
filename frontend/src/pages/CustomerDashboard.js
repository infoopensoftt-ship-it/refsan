import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { 
  Users, 
  LogOut, 
  Clock, 
  AlertCircle,
  Eye,
  Calendar,
  DollarSign,
  User,
  Wrench,
  Plus
} from 'lucide-react';
  const [showRepairForm, setShowRepairForm] = useState(false);
  const [customers, setCustomers] = useState([]);
  
  // Repair form state
  const [repairForm, setRepairForm] = useState({
    customer_id: '',
    device_type: '',
    brand: '',
    model: '',
    description: '',
    priority: 'orta',
    cost_estimate: '',
    images: []
  });

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [repairs, setRepairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRepairForm, setShowRepairForm] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, repairsRes] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/repairs`)
      ]);
      
      setStats(statsRes.data);
      setRepairs(repairsRes.data);
    } catch (error) {
      console.error('Data fetch error:', error);
      toast.error('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'beklemede': return 'bg-yellow-100 text-yellow-800';
      case 'isleniyor': return 'bg-blue-100 text-blue-800';
      case 'tamamlandi': return 'bg-green-100 text-green-800';
      case 'iptal': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'dusuk': return 'bg-gray-100 text-gray-800';
      case 'orta': return 'bg-yellow-100 text-yellow-800';
      case 'yuksek': return 'bg-orange-100 text-orange-800';
      case 'acil': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPaymentStatusColor = (status) => {
    switch (status) {
      case 'beklemede': return 'bg-yellow-100 text-yellow-800';
      case 'odendi': return 'bg-green-100 text-green-800';
      case 'kismi': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'beklemede': return 'Beklemede';
      case 'isleniyor': return 'İşleniyor';
      case 'tamamlandi': return 'Tamamlandı';
      case 'iptal': return 'İptal Edildi';
      default: return status;
    }
  };

  const getPriorityText = (priority) => {
    switch (priority) {
      case 'dusuk': return 'Düşük';
      case 'orta': return 'Orta';
      case 'yuksek': return 'Yüksek';
      case 'acil': return 'Acil';
      default: return priority;
    }
  };

  const getPaymentStatusText = (status) => {
    switch (status) {
      case 'beklemede': return 'Beklemede';
      case 'odendi': return 'Ödendi';
      case 'kismi': return 'Kısmi Ödendi';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-green-700 rounded-lg flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Refsan Müşteri Panel</h1>
                <p className="text-sm text-slate-600">Hoş geldin, {user?.full_name}</p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <Button
                onClick={() => setShowRepairForm(true)}
                className="btn-primary"
                data-testid="add-repair-btn"
              >
                <Plus className="w-4 h-4 mr-2" />
                Yeni Arıza
              </Button>
              <Button
                variant="outline"
                onClick={logout}
                className="hover:bg-red-50 hover:text-red-600 hover:border-red-300"
                data-testid="logout-btn"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Çıkış Yap
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="card-hover bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-700">Toplam Başvurularım</p>
                  <p className="text-3xl font-bold text-blue-900">{stats?.my_repairs || 0}</p>
                </div>
                <Wrench className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-700">Bekleyen İşlerim</p>
                  <p className="text-3xl font-bold text-yellow-900">{stats?.my_pending || 0}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Repairs List */}
        <Card>
          <CardHeader>
            <CardTitle>Arıza Başvurularım</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {repairs.map(repair => (
                <div key={repair.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="space-y-3 flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-slate-800">
                          {repair.device_type} - {repair.brand} {repair.model}
                        </h3>
                        <Badge className={getStatusColor(repair.status)}>
                          {getStatusText(repair.status)}
                        </Badge>
                        <Badge className={getPriorityColor(repair.priority)}>
                          {getPriorityText(repair.priority)}
                        </Badge>
                      </div>
                      
                      <div>
                        <p className="text-sm font-medium text-slate-700">Arıza Açıklaması</p>
                        <p className="text-sm text-slate-600">{repair.description}</p>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                        <div className="flex items-center space-x-1 text-slate-500">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(repair.created_at).toLocaleDateString('tr-TR')}</span>
                        </div>
                        
                        {repair.assigned_technician_name && (
                          <div className="flex items-center space-x-1 text-blue-600">
                            <Wrench className="w-4 h-4" />
                            <span>Teknisyen: {repair.assigned_technician_name}</span>
                          </div>
                        )}
                        
                        {repair.cost_estimate && (
                          <div className="flex items-center space-x-1 text-orange-600">
                            <DollarSign className="w-4 h-4" />
                            <span>Tahmini: ₺{repair.cost_estimate}</span>
                          </div>
                        )}
                        
                        {repair.final_cost && (
                          <div className="flex items-center space-x-1 text-green-600">
                            <DollarSign className="w-4 h-4" />
                            <span>Tutar: ₺{repair.final_cost}</span>
                          </div>
                        )}
                      </div>
                      
                      {repair.payment_status && (
                        <div>
                          <Badge className={getPaymentStatusColor(repair.payment_status)}>
                            Ödeme: {getPaymentStatusText(repair.payment_status)}
                          </Badge>
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-4">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button size="sm" variant="outline" data-testid={`view-repair-${repair.id}`}>
                            <Eye className="w-4 h-4 mr-2" />
                            Detay
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Arıza Detayları</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium text-slate-700">Başvuru Tarihi</p>
                                <p className="text-sm">{new Date(repair.created_at).toLocaleDateString('tr-TR', {
                                  year: 'numeric',
                                  month: 'long',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}</p>
                              </div>
                              
                              {repair.completed_at && (
                                <div>
                                  <p className="text-sm font-medium text-slate-700">Tamamlanma Tarihi</p>
                                  <p className="text-sm">{new Date(repair.completed_at).toLocaleDateString('tr-TR', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}</p>
                                </div>
                              )}
                            </div>
                            
                            <div className="grid grid-cols-3 gap-4">
                              <div>
                                <p className="text-sm font-medium text-slate-700">Cihaz Türü</p>
                                <p className="text-sm">{repair.device_type}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-slate-700">Marka</p>
                                <p className="text-sm">{repair.brand}</p>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-slate-700">Model</p>
                                <p className="text-sm">{repair.model}</p>
                              </div>
                            </div>
                            
                            <div>
                              <p className="text-sm font-medium text-slate-700">Arıza Açıklaması</p>
                              <div className="bg-gray-50 p-3 rounded mt-2">
                                <p className="text-sm">{repair.description}</p>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium text-slate-700">Durum</p>
                                <Badge className={getStatusColor(repair.status)}>
                                  {getStatusText(repair.status)}
                                </Badge>
                              </div>
                              <div>
                                <p className="text-sm font-medium text-slate-700">Öncelik</p>
                                <Badge className={getPriorityColor(repair.priority)}>
                                  {getPriorityText(repair.priority)}
                                </Badge>
                              </div>
                            </div>
                            
                            {repair.assigned_technician_name && (
                              <div>
                                <p className="text-sm font-medium text-slate-700">Atanan Teknisyen</p>
                                <p className="text-sm text-blue-600">{repair.assigned_technician_name}</p>
                              </div>
                            )}
                            
                            {(repair.cost_estimate || repair.final_cost) && (
                              <div className="bg-green-50 p-4 rounded">
                                <p className="text-sm font-medium text-green-800 mb-2">Maliyet Bilgileri</p>
                                <div className="grid grid-cols-2 gap-4">
                                  {repair.cost_estimate && (
                                    <div>
                                      <p className="text-xs text-green-700">Tahmini Tutar</p>
                                      <p className="text-lg font-bold text-green-800">₺{repair.cost_estimate}</p>
                                    </div>
                                  )}
                                  {repair.final_cost && (
                                    <div>
                                      <p className="text-xs text-green-700">Final Tutar</p>
                                      <p className="text-lg font-bold text-green-800">₺{repair.final_cost}</p>
                                    </div>
                                  )}
                                </div>
                                {repair.payment_status && (
                                  <div className="mt-3">
                                    <p className="text-xs text-green-700">Ödeme Durumu</p>
                                    <Badge className={getPaymentStatusColor(repair.payment_status)}>
                                      {getPaymentStatusText(repair.payment_status)}
                                    </Badge>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </div>
              ))}
              
              {repairs.length === 0 && (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-slate-700 mb-2">Henüz arıza başvurunuz bulunmuyor</h3>
                  <p className="text-slate-500">Yeni arıza başvuruları için admin veya teknisyen ile iletişime geçin.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CustomerDashboard;