import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { 
  Settings, 
  LogOut, 
  Users, 
  Wrench, 
  FileText, 
  TrendingUp, 
  Plus,
  Edit,
  Eye,
  UserPlus,
  Phone,
  Mail,
  Calendar,
  Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const [selectedTechnician, setSelectedTechnician] = useState(null);
  const [technicianReport, setTechnicianReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [repairs, setRepairs] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRepair, setSelectedRepair] = useState(null);
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const [showRepairForm, setShowRepairForm] = useState(false);
  
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
      const [statsRes, repairsRes, customersRes, usersRes] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/repairs`),
        axios.get(`${API}/customers`),
        axios.get(`${API}/users`)
      ]);
      
      setStats(statsRes.data);
      setRepairs(repairsRes.data);
      setCustomers(customersRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error('Data fetch error:', error);
      toast.error('Veriler yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCustomer = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/customers`, customerForm);
      toast.success('Müşteri başarıyla oluşturuldu');
      setShowCustomerForm(false);
      setCustomerForm({ full_name: '', email: '', phone: '', address: '' });
      fetchData();
    } catch (error) {
      toast.error('Müşteri oluşturulamadı');
    }
  };

  const handleCreateRepair = async (e) => {
    e.preventDefault();
    try {
      const formData = { ...repairForm };
      if (formData.cost_estimate) {
        formData.cost_estimate = parseFloat(formData.cost_estimate);
      }
      
      await axios.post(`${API}/repairs`, formData);
      toast.success('Arıza kaydı başarıyla oluşturuldu');
      setShowRepairForm(false);
      setRepairForm({
        customer_id: '',
        device_type: '',
        brand: '',
        model: '',
        description: '',
        priority: 'orta',
        cost_estimate: ''
      });
      fetchData();
    } catch (error) {
      toast.error('Arıza kaydı oluşturulamadı');
    }
  };

  const updateRepairStatus = async (repairId, updateData) => {
    try {
      await axios.put(`${API}/repairs/${repairId}`, updateData);
      toast.success('Arıza durumu güncellendi');
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
              <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-800">Refsan Türkiye Admin</h1>
                <p className="text-sm text-slate-600">Hoş geldin, {user?.full_name}</p>
              </div>
            </div>
            
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <Card className="card-hover bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-700">Toplam Arıza</p>
                  <p className="text-3xl font-bold text-blue-900">{stats?.total_repairs || 0}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-700">Bekleyen</p>
                  <p className="text-3xl font-bold text-yellow-900">{stats?.pending_repairs || 0}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700">Tamamlanan</p>
                  <p className="text-3xl font-bold text-green-900">{stats?.completed_repairs || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-700">Müşteriler</p>
                  <p className="text-3xl font-bold text-purple-900">{stats?.total_customers || 0}</p>
                </div>
                <Users className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="card-hover bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-700">Teknisyenler</p>
                  <p className="text-3xl font-bold text-orange-900">{stats?.total_technicians || 0}</p>
                </div>
                <Wrench className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="repairs" className="space-y-6">
          <div className="flex items-center justify-between">
            <TabsList className="bg-white shadow-sm">
              <TabsTrigger value="repairs" data-testid="repairs-tab">Arızalar</TabsTrigger>
              <TabsTrigger value="customers" data-testid="customers-tab">Müşteriler</TabsTrigger>
              <TabsTrigger value="users" data-testid="users-tab">Kullanıcılar</TabsTrigger>
              <TabsTrigger value="reports" data-testid="reports-tab">Teknisyen Raporları</TabsTrigger>
            </TabsList>
            
            <div className="flex space-x-3">
              <Dialog open={showCustomerForm} onOpenChange={setShowCustomerForm}>
                <DialogTrigger asChild>
                  <Button className="btn-secondary" data-testid="add-customer-btn">
                    <UserPlus className="w-4 h-4 mr-2" />
                    Yeni Müşteri
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Yeni Müşteri Ekle</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleCreateCustomer} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="customer-name">Ad Soyad *</Label>
                      <Input
                        id="customer-name"
                        value={customerForm.full_name}
                        onChange={(e) => setCustomerForm({ ...customerForm, full_name: e.target.value })}
                        placeholder="Müşteri adı"
                        required
                        data-testid="customer-name-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="customer-phone">Telefon *</Label>
                      <Input
                        id="customer-phone"
                        value={customerForm.phone}
                        onChange={(e) => setCustomerForm({ ...customerForm, phone: e.target.value })}
                        placeholder="05XX XXX XX XX"
                        required
                        data-testid="customer-phone-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="customer-email">E-posta</Label>
                      <Input
                        id="customer-email"
                        type="email"
                        value={customerForm.email}
                        onChange={(e) => setCustomerForm({ ...customerForm, email: e.target.value })}
                        placeholder="ornek@email.com"
                        data-testid="customer-email-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="customer-address">Adres</Label>
                      <Input
                        id="customer-address"
                        value={customerForm.address}
                        onChange={(e) => setCustomerForm({ ...customerForm, address: e.target.value })}
                        placeholder="Müşteri adresi"
                        data-testid="customer-address-input"
                      />
                    </div>
                    <Button type="submit" className="w-full btn-primary" data-testid="create-customer-btn">
                      Müşteri Oluştur
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
              
              <Dialog open={showRepairForm} onOpenChange={setShowRepairForm}>
                <DialogTrigger asChild>
                  <Button className="btn-primary" data-testid="add-repair-btn">
                    <Plus className="w-4 h-4 mr-2" />
                    Yeni Arıza
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Yeni Arıza Kaydı</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleCreateRepair} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="repair-customer">Müşteri *</Label>
                      <Select value={repairForm.customer_id} onValueChange={(value) => setRepairForm({ ...repairForm, customer_id: value })}>
                        <SelectTrigger data-testid="repair-customer-select">
                          <SelectValue placeholder="Müşteri seçin" />
                        </SelectTrigger>
                        <SelectContent>
                          {customers.map(customer => (
                            <SelectItem key={customer.id} value={customer.id}>
                              {customer.full_name} - {customer.phone}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="device-type">Cihaz Türü *</Label>
                        <Select value={repairForm.device_type} onValueChange={(value) => setRepairForm({ ...repairForm, device_type: value })}>
                          <SelectTrigger data-testid="device-type-select">
                            <SelectValue placeholder="Makine türü seçin" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Seramik Makinesi">Seramik Makinesi</SelectItem>
                            <SelectItem value="Porselen Üretim Makinesi">Porselen Üretim Makinesi</SelectItem>
                            <SelectItem value="Çini İşleme Makinesi">Çini İşleme Makinesi</SelectItem>
                            <SelectItem value="Fırın Sistemi">Fırın Sistemi</SelectItem>
                            <SelectItem value="Glazür Makinesi">Glazür Makinesi</SelectItem>
                            <SelectItem value="Karışım Makinesi">Karışım Makinesi</SelectItem>
                            <SelectItem value="Diğer">Diğer</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="brand">Marka *</Label>
                        <Select value={repairForm.brand} onValueChange={(value) => setRepairForm({ ...repairForm, brand: value })}>
                          <SelectTrigger data-testid="brand-select">
                            <SelectValue placeholder="Marka seçin" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Refsan">Refsan</SelectItem>
                            <SelectItem value="Sacmi">Sacmi</SelectItem>
                            <SelectItem value="System Ceramics">System Ceramics</SelectItem>
                            <SelectItem value="LB">LB</SelectItem>
                            <SelectItem value="Barbieri e Tarozzi">Barbieri e Tarozzi</SelectItem>
                            <SelectItem value="Diğer">Diğer</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="model">Model *</Label>
                      <Input
                        id="model"
                        value={repairForm.model}
                        onChange={(e) => setRepairForm({ ...repairForm, model: e.target.value })}
                        placeholder="Makine modeli (ör: RS-1000, SP-250...)"
                        required
                        data-testid="model-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Arıza Açıklaması *</Label>
                      <Input
                        id="description"
                        value={repairForm.description}
                        onChange={(e) => setRepairForm({ ...repairForm, description: e.target.value })}
                        placeholder="Arıza detayları..."
                        required
                        data-testid="description-input"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="priority">Öncelik</Label>
                        <Select value={repairForm.priority} onValueChange={(value) => setRepairForm({ ...repairForm, priority: value })}>
                          <SelectTrigger data-testid="priority-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="dusuk">Düşük</SelectItem>
                            <SelectItem value="orta">Orta</SelectItem>
                            <SelectItem value="yuksek">Yüksek</SelectItem>
                            <SelectItem value="acil">Acil</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="cost-estimate">Tahmini Tutar (₺)</Label>
                        <Input
                          id="cost-estimate"
                          type="number"
                          value={repairForm.cost_estimate}
                          onChange={(e) => setRepairForm({ ...repairForm, cost_estimate: e.target.value })}
                          placeholder="0"
                          data-testid="cost-estimate-input"
                        />
                      </div>
                    </div>
                    <Button type="submit" className="w-full btn-primary" data-testid="create-repair-btn">
                      Arıza Kaydı Oluştur
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>

          <TabsContent value="repairs" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Arıza Kayıtları</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {repairs.map(repair => (
                    <div key={repair.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center space-x-3">
                            <h3 className="font-semibold text-slate-800">{repair.customer_name}</h3>
                            <Badge className={getStatusColor(repair.status)}>
                              {repair.status}
                            </Badge>
                            <Badge className={getPriorityColor(repair.priority)}>
                              {repair.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-slate-600">
                            <span className="font-medium">{repair.device_type}</span> - {repair.brand} {repair.model}
                          </p>
                          <p className="text-sm text-slate-700">{repair.description}</p>
                          {repair.cost_estimate && (
                            <p className="text-sm text-green-600 font-medium">Tahmini: ₺{repair.cost_estimate}</p>
                          )}
                          {repair.assigned_technician_name && (
                            <p className="text-sm text-blue-600">Teknisyen: {repair.assigned_technician_name}</p>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button size="sm" variant="outline">
                                <Eye className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Arıza Detayları</DialogTitle>
                              </DialogHeader>
                              <div className="space-y-4">
                                <div>
                                  <Label>Müşteri</Label>
                                  <p className="text-sm">{repair.customer_name}</p>
                                </div>
                                <div>
                                  <Label>Cihaz</Label>
                                  <p className="text-sm">{repair.device_type} - {repair.brand} {repair.model}</p>
                                </div>
                                <div>
                                  <Label>Açıklama</Label>
                                  <p className="text-sm">{repair.description}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                  <div>
                                    <Label>Durum</Label>
                                    <Select 
                                      value={repair.status} 
                                      onValueChange={(value) => updateRepairStatus(repair.id, { status: value })}
                                    >
                                      <SelectTrigger>
                                        <SelectValue />
                                      </SelectTrigger>
                                      <SelectContent>
                                        <SelectItem value="beklemede">Beklemede</SelectItem>
                                        <SelectItem value="isleniyor">İşleniyor</SelectItem>
                                        <SelectItem value="tamamlandi">Tamamlandı</SelectItem>
                                        <SelectItem value="iptal">İptal</SelectItem>
                                      </SelectContent>
                                    </Select>
                                  </div>
                                  <div>
                                    <Label>Teknisyen Ata</Label>
                                    <Select 
                                      value={repair.assigned_technician_id || ''} 
                                      onValueChange={(value) => updateRepairStatus(repair.id, { assigned_technician_id: value })}
                                    >
                                      <SelectTrigger>
                                        <SelectValue placeholder="Teknisyen seç" />
                                      </SelectTrigger>
                                      <SelectContent>
                                        {users.filter(u => u.role === 'teknisyen').map(tech => (
                                          <SelectItem key={tech.id} value={tech.id}>
                                            {tech.full_name}
                                          </SelectItem>
                                        ))}
                                      </SelectContent>
                                    </Select>
                                  </div>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {repairs.length === 0 && (
                    <div className="text-center py-8 text-slate-500">
                      Henüz arıza kaydı bulunmuyor
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="customers" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Müşteri Listesi</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {customers.map(customer => (
                    <div key={customer.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <h3 className="font-semibold text-slate-800">{customer.full_name}</h3>
                          <div className="flex items-center space-x-4 text-sm text-slate-600">
                            <div className="flex items-center space-x-1">
                              <Phone className="w-4 h-4" />
                              <span>{customer.phone}</span>
                            </div>
                            {customer.email && (
                              <div className="flex items-center space-x-1">
                                <Mail className="w-4 h-4" />
                                <span>{customer.email}</span>
                              </div>
                            )}
                          </div>
                          {customer.address && (
                            <p className="text-sm text-slate-600">{customer.address}</p>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-sm text-slate-500 flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{new Date(customer.created_at).toLocaleDateString('tr-TR')}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {customers.length === 0 && (
                    <div className="text-center py-8 text-slate-500">
                      Henüz müşteri kaydı bulunmuyor
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Kullanıcı Listesi</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {users.map(userItem => (
                    <div key={userItem.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-3">
                            <h3 className="font-semibold text-slate-800">{userItem.full_name}</h3>
                            <Badge className={
                              userItem.role === 'admin' ? 'bg-red-100 text-red-800' :
                              userItem.role === 'teknisyen' ? 'bg-blue-100 text-blue-800' :
                              'bg-green-100 text-green-800'
                            }>
                              {userItem.role}
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-slate-600">
                            <div className="flex items-center space-x-1">
                              <Mail className="w-4 h-4" />
                              <span>{userItem.email}</span>
                            </div>
                            {userItem.phone && (
                              <div className="flex items-center space-x-1">
                                <Phone className="w-4 h-4" />
                                <span>{userItem.phone}</span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-sm text-slate-500 flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(userItem.created_at).toLocaleDateString('tr-TR')}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {users.length === 0 && (
                    <div className="text-center py-8 text-slate-500">
                      Kullanıcı bulunamadı
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;