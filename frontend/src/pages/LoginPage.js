import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../App';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { Eye, EyeOff, Settings, Users, Wrench } from 'lucide-react';

const LoginPage = () => {
  const { login, register, isAuthenticated, loading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  
  // Register form state
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: '',
    phone: ''
  });

  useEffect(() => {
    // Demo hesapları için toast göster
    const timer = setTimeout(() => {
      toast.info('Demo hesapları mevcuttur', {
        description: 'Hızlı giriş için demo hesaplarını kullanabilirsiniz.',
        duration: 5000
      });
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginData.email || !loginData.password) {
      toast.error('Lütfen tüm alanları doldurun');
      return;
    }

    setIsLoading(true);
    const result = await login(loginData.email, loginData.password);
    
    if (result.success) {
      toast.success('Başarıyla giriş yapıldı!');
    } else {
      toast.error(result.error || 'Giriş yapılamadı');
    }
    setIsLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!registerData.email || !registerData.password || !registerData.full_name || !registerData.role) {
      toast.error('Lütfen tüm zorunlu alanları doldurun');
      return;
    }

    setIsLoading(true);
    const result = await register(registerData);
    
    if (result.success) {
      toast.success('Hesap başarıyla oluşturuldu! Giriş yapabilirsiniz.');
      // Reset form
      setRegisterData({
        email: '',
        password: '',
        full_name: '',
        role: '',
        phone: ''
      });
    } else {
      toast.error(result.error || 'Kayıt oluşturulamadı');
    }
    setIsLoading(false);
  };

  const fillDemoLogin = (role) => {
    const demoAccounts = {
      admin: { email: 'admin@demo.com', password: 'admin123' },
      teknisyen: { email: 'teknisyen@demo.com', password: 'teknisyen123' },
      musteri: { email: 'musteri@demo.com', password: 'musteri123' }
    };
    
    setLoginData(demoAccounts[role]);
    toast.success(`${role.charAt(0).toUpperCase() + role.slice(1)} demo hesabı yüklendi`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center mb-4">
            <Wrench className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800">Teknik Servis</h1>
          <p className="text-slate-600">Arıza yönetim sistemi</p>
        </div>

        {/* Demo Accounts */}
        <Card className="glass border-0 shadow-xl">
          <CardHeader className="text-center pb-4">
            <CardTitle className="text-lg text-slate-700">Demo Hesapları</CardTitle>
            <CardDescription>Hızlı test için hazır hesaplar</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => fillDemoLogin('admin')}
                className="flex flex-col items-center p-3 h-auto hover:bg-red-50 hover:border-red-200"
                data-testid="demo-admin-btn"
              >
                <Settings className="w-4 h-4 mb-1 text-red-600" />
                <span className="text-xs">Admin</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fillDemoLogin('teknisyen')}
                className="flex flex-col items-center p-3 h-auto hover:bg-blue-50 hover:border-blue-200"
                data-testid="demo-technician-btn"
              >
                <Wrench className="w-4 h-4 mb-1 text-blue-600" />
                <span className="text-xs">Teknisyen</span>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fillDemoLogin('musteri')}
                className="flex flex-col items-center p-3 h-auto hover:bg-green-50 hover:border-green-200"
                data-testid="demo-customer-btn"
              >
                <Users className="w-4 h-4 mb-1 text-green-600" />
                <span className="text-xs">Müşteri</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Main Form */}
        <Card className="glass border-0 shadow-xl">
          <CardContent className="p-6">
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="login" data-testid="login-tab">Giriş Yap</TabsTrigger>
                <TabsTrigger value="register" data-testid="register-tab">Kayıt Ol</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login" className="space-y-4">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">E-posta</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="ornek@email.com"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      data-testid="login-email-input"
                      className="form-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Şifre</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={loginData.password}
                        onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                        data-testid="login-password-input"
                        className="form-input pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <Button
                    type="submit"
                    className="w-full btn-primary"
                    disabled={isLoading}
                    data-testid="login-submit-btn"
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center">
                        <div className="loading-spinner w-4 h-4 mr-2"></div>
                        Giriş yapılıyor...
                      </div>
                    ) : (
                      'Giriş Yap'
                    )}
                  </Button>
                </form>
              </TabsContent>
              
              <TabsContent value="register" className="space-y-4">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-name">Ad Soyad *</Label>
                    <Input
                      id="register-name"
                      type="text"
                      placeholder="Adınız Soyadınız"
                      value={registerData.full_name}
                      onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                      data-testid="register-name-input"
                      className="form-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-email">E-posta *</Label>
                    <Input
                      id="register-email"
                      type="email"
                      placeholder="ornek@email.com"
                      value={registerData.email}
                      onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                      data-testid="register-email-input"
                      className="form-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-phone">Telefon</Label>
                    <Input
                      id="register-phone"
                      type="tel"
                      placeholder="05XX XXX XX XX"
                      value={registerData.phone}
                      onChange={(e) => setRegisterData({ ...registerData, phone: e.target.value })}
                      data-testid="register-phone-input"
                      className="form-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-role">Rol *</Label>
                    <Select value={registerData.role} onValueChange={(value) => setRegisterData({ ...registerData, role: value })}>
                      <SelectTrigger data-testid="register-role-select">
                        <SelectValue placeholder="Rolünüzü seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="admin">Admin</SelectItem>
                        <SelectItem value="teknisyen">Teknisyen</SelectItem>
                        <SelectItem value="musteri">Müşteri</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="register-password">Şifre *</Label>
                    <div className="relative">
                      <Input
                        id="register-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="••••••••"
                        value={registerData.password}
                        onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                        data-testid="register-password-input"
                        className="form-input pr-10"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <Button
                    type="submit"
                    className="w-full btn-primary"
                    disabled={isLoading}
                    data-testid="register-submit-btn"
                  >
                    {isLoading ? (
                      <div className="flex items-center justify-center">
                        <div className="loading-spinner w-4 h-4 mr-2"></div>
                        Kayıt oluşturuluyor...
                      </div>
                    ) : (
                      'Kayıt Ol'
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        
        <div className="text-center text-sm text-slate-500">
          Teknik servis arıza yönetim sistemi
        </div>
      </div>
    </div>
  );
};

export default LoginPage;