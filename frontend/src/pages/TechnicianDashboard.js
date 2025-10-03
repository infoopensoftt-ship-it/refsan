import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import FileUpload from '../components/FileUpload';
import { 
  Wrench, 
  LogOut, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Edit,
  Eye,
  Phone,
  Calendar,
  DollarSign,
  Plus,
  UserPlus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TechnicianDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [repairs, setRepairs] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRepair, setSelectedRepair] = useState(null);
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const [showRepairForm, setShowRepairForm] = useState(false);
  
  // Update form state
  const [updateForm, setUpdateForm] = useState({
    status: '',
    final_cost: '',
    payment_status: '',
    notes: ''
  });

  // Customer form state
  const [customerForm, setCustomerForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    address: ''
  });
  
  // Repair form state
  const [repairForm, setRepairForm] = useState({
    customer_id: '',
    device_type: '',
    brand: '',
    model: '',
    description: '',
    priority: 'orta',
    cost_estimate: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, repairsRes, customersRes] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/repairs`),
        axios.get(`${API}/customers`)
      ]);
      
      setStats(statsRes.data);
      setRepairs(repairsRes.data);
      setCustomers(customersRes.data);
    } catch (error) {
      console.error('Data fetch error:', error);
      toast.error('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRepair = async (repairId) => {
    try {
      const updateData = {};
      
      if (updateForm.status) updateData.status = updateForm.status;
      if (updateForm.final_cost) updateData.final_cost = parseFloat(updateForm.final_cost);
      if (updateForm.payment_status) updateData.payment_status = updateForm.payment_status;
      
      await axios.put(`${API}/repairs/${repairId}`, updateData);
      toast.success('Arıza durumu güncellendi');
      setShowUpdateForm(false);
      setUpdateForm({ status: '', final_cost: '', payment_status: '', notes: '' });
      fetchData();
    } catch (error) {
      toast.error('Güncelleme başarısız');
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
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <Wrench className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Refsan Teknisyen Panel</h1>
                <p className="text-sm text-slate-600">Hoş geldin, {user?.full_name}</p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowCustomerForm(true)}
                className="hover:bg-green-50 hover:text-green-600 hover:border-green-300"
                data-testid="add-customer-btn"
              >
                <UserPlus className="w-4 h-4 mr-2" />
                Yeni Müşteri
              </Button>
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="card-hover bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-700">Toplam İşlerim</p>
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
                  <p className="text-sm font-medium text-yellow-700">Bekleyen İşler</p>
                  <p className="text-3xl font-bold text-yellow-900">{stats?.my_pending || 0}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700">Tamamlananlar</p>
                  <p className="text-3xl font-bold text-green-900">{stats?.my_completed || 0}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Repairs List */}
        <Card>
          <CardHeader>
            <CardTitle>Atanan İşler</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {repairs.map(repair => (
                <div key={repair.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-slate-800">{repair.customer_name}</h3>
                        <Badge className={getStatusColor(repair.status)}>
                          {repair.status}
                        </Badge>
                        <Badge className={getPriorityColor(repair.priority)}>
                          {repair.priority}
                        </Badge>
                        {repair.payment_status && (
                          <Badge className={getPaymentStatusColor(repair.payment_status)}>
                            Ödeme: {repair.payment_status}
                          </Badge>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium text-slate-700">Cihaz Bilgileri</p>
                          <p className="text-sm text-slate-600">
                            {repair.device_type} - {repair.brand} {repair.model}
                          </p>
                        </div>
                        
                        <div>
                          <p className="text-sm font-medium text-slate-700">Arıza Açıklaması</p>
                          <p className="text-sm text-slate-600">{repair.description}</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        {repair.cost_estimate && (
                          <div className="flex items-center space-x-1 text-blue-600">
                            <DollarSign className="w-4 h-4" />
                            <span>Tahmini: ₺{repair.cost_estimate}</span>
                          </div>
                        )}
                        {repair.final_cost && (
                          <div className="flex items-center space-x-1 text-green-600">
                            <DollarSign className="w-4 h-4" />
                            <span>Final: ₺{repair.final_cost}</span>
                          </div>
                        )}
                        <div className="flex items-center space-x-1 text-slate-500">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(repair.created_at).toLocaleDateString('tr-TR')}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button size="sm" variant="outline" data-testid={`view-repair-${repair.id}`}>
                            <Eye className="w-4 h-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Arıza Detayları</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <Label>Müşteri</Label>
                                <p className="text-sm font-medium">{repair.customer_name}</p>
                              </div>
                              <div>
                                <Label>Tarih</Label>
                                <p className="text-sm">{new Date(repair.created_at).toLocaleDateString('tr-TR')}</p>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-4">
                              <div>
                                <Label>Cihaz Türü</Label>
                                <p className="text-sm">{repair.device_type}</p>
                              </div>
                              <div>
                                <Label>Marka</Label>
                                <p className="text-sm">{repair.brand}</p>
                              </div>
                              <div>
                                <Label>Model</Label>
                                <p className="text-sm">{repair.model}</p>
                              </div>
                            </div>
                            
                            <div>
                              <Label>Arıza Açıklaması</Label>
                              <p className="text-sm bg-gray-50 p-3 rounded">{repair.description}</p>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <Label>Mevcut Durum</Label>
                                <Badge className={getStatusColor(repair.status)}>
                                  {repair.status}
                                </Badge>
                              </div>
                              <div>
                                <Label>Öncelik</Label>
                                <Badge className={getPriorityColor(repair.priority)}>
                                  {repair.priority}
                                </Badge>
                              </div>
                            </div>
                            
                            {(repair.cost_estimate || repair.final_cost) && (
                              <div className="grid grid-cols-2 gap-4">
                                {repair.cost_estimate && (
                                  <div>
                                    <Label>Tahmini Tutar</Label>
                                    <p className="text-sm font-medium text-blue-600">₺{repair.cost_estimate}</p>
                                  </div>
                                )}
                                {repair.final_cost && (
                                  <div>
                                    <Label>Final Tutar</Label>
                                    <p className="text-sm font-medium text-green-600">₺{repair.final_cost}</p>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>
                      
                      <Dialog open={showUpdateForm && selectedRepair?.id === repair.id} onOpenChange={(open) => {
                        setShowUpdateForm(open);
                        if (open) {
                          setSelectedRepair(repair);
                          setUpdateForm({
                            status: repair.status,
                            final_cost: repair.final_cost || '',
                            payment_status: repair.payment_status || '',
                            notes: ''
                          });
                        }
                      }}>
                        <DialogTrigger asChild>
                          <Button size="sm" className="btn-primary" data-testid={`edit-repair-${repair.id}`}>
                            <Edit className="w-4 h-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>İş Durumunu Güncelle</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <Label>Durum</Label>
                              <Select value={updateForm.status} onValueChange={(value) => setUpdateForm({ ...updateForm, status: value })}>
                                <SelectTrigger data-testid="status-select">
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="beklemede">Beklemede</SelectItem>
                                  <SelectItem value="isleniyor">İşleniyor</SelectItem>
                                  <SelectItem value="tamamlandi">Tamamlandı</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Final Tutar (₺)</Label>
                              <Input
                                type="number"
                                value={updateForm.final_cost}
                                onChange={(e) => setUpdateForm({ ...updateForm, final_cost: e.target.value })}
                                placeholder="Final tutar"
                                data-testid="final-cost-input"
                              />
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Ödeme Durumu</Label>
                              <Select value={updateForm.payment_status} onValueChange={(value) => setUpdateForm({ ...updateForm, payment_status: value })}>
                                <SelectTrigger data-testid="payment-status-select">
                                  <SelectValue placeholder="Ödeme durumu seç" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="beklemede">Beklemede</SelectItem>
                                  <SelectItem value="kismi">Kısmi Ödendi</SelectItem>
                                  <SelectItem value="odendi">Ödendi</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Notlar</Label>
                              <Textarea
                                value={updateForm.notes}
                                onChange={(e) => setUpdateForm({ ...updateForm, notes: e.target.value })}
                                placeholder="Güncelleme notları (opsiyonel)"
                                data-testid="notes-textarea"
                              />
                            </div>
                            
                            <Button
                              onClick={() => handleUpdateRepair(repair.id)}
                              className="w-full btn-primary"
                              data-testid="update-repair-btn"
                            >
                              Güncelle
                            </Button>
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
                  <h3 className="text-lg font-medium text-slate-700 mb-2">Henüz atanan iş bulunmuyor</h3>
                  <p className="text-slate-500">Size atanan işler burada görünecek.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TechnicianDashboard;