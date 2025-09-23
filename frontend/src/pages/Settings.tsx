import { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Users, 
  Plane, 
  Shield, 
  Bell, 
  Database,
  Key,
  Monitor,
  Save,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';

const Settings = () => {
  const [settings, setSettings] = useState({
    // System Settings
    apiUrl: 'http://localhost:8000',
    useMockData: true,
    autoRefreshInterval: 30,
    
    // Notification Settings
    emailNotifications: true,
    pushNotifications: false,
    disruptionAlerts: true,
    violationAlerts: true,
    
    // Roster Settings
    defaultRosterWeeks: 2,
    autoOptimization: false,
    confidenceThreshold: 0.8,
    maxDutyHours: 14,
    minRestHours: 10,
    
    // Security Settings
    sessionTimeout: 8,
    requireMFA: false,
    auditLogging: true,
  });

  const { toast } = useToast();

  const handleSettingChange = (
    key: keyof typeof settings,
    value: string | number | boolean,
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    // Mock save functionality
    toast({
      title: "Settings Saved",
      description: "Your preferences have been updated successfully.",
    });
  };

  const handleReset = () => {
    // Reset to defaults
    setSettings({
      apiUrl: 'http://localhost:8000',
      useMockData: true,
      autoRefreshInterval: 30,
      emailNotifications: true,
      pushNotifications: false,
      disruptionAlerts: true,
      violationAlerts: true,
      defaultRosterWeeks: 2,
      autoOptimization: false,
      confidenceThreshold: 0.8,
      maxDutyHours: 14,
      minRestHours: 10,
      sessionTimeout: 8,
      requireMFA: false,
      auditLogging: true,
    });
    
    toast({
      title: "Settings Reset",
      description: "All settings have been reset to default values.",
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">System Settings</h1>
          <p className="text-muted-foreground">
            Configure system preferences and operational parameters
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={handleReset}
            className="glass-button"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button
            onClick={handleSave}
            className="glass-button bg-primary hover:bg-primary/90"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Configuration */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="h-5 w-5 text-primary" />
              <span>System Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiUrl">API Base URL</Label>
              <Input
                id="apiUrl"
                value={settings.apiUrl}
                onChange={(e) => handleSettingChange('apiUrl', e.target.value)}
                className="glass"
                placeholder="Enter API URL"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Use Mock Data</Label>
                <p className="text-sm text-muted-foreground">
                  Use local seed data when API is unavailable
                </p>
              </div>
              <Switch
                checked={settings.useMockData}
                onCheckedChange={(checked) => handleSettingChange('useMockData', checked)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="refreshInterval">Auto Refresh (seconds)</Label>
              <Input
                id="refreshInterval"
                type="number"
                value={settings.autoRefreshInterval}
                onChange={(e) => handleSettingChange('autoRefreshInterval', parseInt(e.target.value))}
                className="glass"
                min="10"
                max="300"
              />
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="h-5 w-5 text-accent" />
              <span>Notifications</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive notifications via email
                </p>
              </div>
              <Switch
                checked={settings.emailNotifications}
                onCheckedChange={(checked) => handleSettingChange('emailNotifications', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Browser push notifications
                </p>
              </div>
              <Switch
                checked={settings.pushNotifications}
                onCheckedChange={(checked) => handleSettingChange('pushNotifications', checked)}
              />
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Disruption Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Get notified of new disruptions
                </p>
              </div>
              <Switch
                checked={settings.disruptionAlerts}
                onCheckedChange={(checked) => handleSettingChange('disruptionAlerts', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Violation Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Alert on policy violations
                </p>
              </div>
              <Switch
                checked={settings.violationAlerts}
                onCheckedChange={(checked) => handleSettingChange('violationAlerts', checked)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Roster Settings */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Plane className="h-5 w-5 text-success" />
              <span>Roster Configuration</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="rosterWeeks">Default Roster Period (weeks)</Label>
              <Input
                id="rosterWeeks"
                type="number"
                value={settings.defaultRosterWeeks}
                onChange={(e) => handleSettingChange('defaultRosterWeeks', parseInt(e.target.value))}
                className="glass"
                min="1"
                max="8"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Auto Optimization</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically optimize rosters
                </p>
              </div>
              <Switch
                checked={settings.autoOptimization}
                onCheckedChange={(checked) => handleSettingChange('autoOptimization', checked)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confidence">Min AI Confidence Threshold</Label>
              <Input
                id="confidence"
                type="number"
                step="0.1"
                min="0.1"
                max="1.0"
                value={settings.confidenceThreshold}
                onChange={(e) => handleSettingChange('confidenceThreshold', parseFloat(e.target.value))}
                className="glass"
              />
            </div>

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="maxDuty">Max Duty Hours</Label>
                <Input
                  id="maxDuty"
                  type="number"
                  value={settings.maxDutyHours}
                  onChange={(e) => handleSettingChange('maxDutyHours', parseInt(e.target.value))}
                  className="glass"
                  min="8"
                  max="16"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="minRest">Min Rest Hours</Label>
                <Input
                  id="minRest"
                  type="number"
                  value={settings.minRestHours}
                  onChange={(e) => handleSettingChange('minRestHours', parseInt(e.target.value))}
                  className="glass"
                  min="8"
                  max="24"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-warning" />
              <span>Security & Access</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="sessionTimeout">Session Timeout (hours)</Label>
              <Input
                id="sessionTimeout"
                type="number"
                value={settings.sessionTimeout}
                onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                className="glass"
                min="1"
                max="24"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Require Multi-Factor Auth</Label>
                <p className="text-sm text-muted-foreground">
                  Enable MFA for all users
                </p>
              </div>
              <Switch
                checked={settings.requireMFA}
                onCheckedChange={(checked) => handleSettingChange('requireMFA', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Audit Logging</Label>
                <p className="text-sm text-muted-foreground">
                  Log all user actions
                </p>
              </div>
              <Switch
                checked={settings.auditLogging}
                onCheckedChange={(checked) => handleSettingChange('auditLogging', checked)}
              />
            </div>

            <Separator />

            <Button variant="outline" className="w-full glass-button">
              <Key className="h-4 w-4 mr-2" />
              Manage API Keys
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* System Status Panel */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Monitor className="h-5 w-5 text-primary" />
            <span>System Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Connection</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse-glow"></div>
                  <span className="text-sm text-success">Connected</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Database</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success rounded-full animate-pulse-glow"></div>
                  <span className="text-sm text-success">Healthy</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">AI Service</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-warning rounded-full"></div>
                  <span className="text-sm text-warning">Degraded</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Memory Usage</span>
                <span className="text-sm text-muted-foreground">2.4 GB / 8 GB</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Active Users</span>
                <span className="text-sm text-muted-foreground">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Uptime</span>
                <span className="text-sm text-muted-foreground">99.98%</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Last Backup</span>
                <span className="text-sm text-muted-foreground">2 hours ago</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Version</span>
                <span className="text-sm text-muted-foreground">v1.0.0</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Environment</span>
                <span className="text-sm text-muted-foreground">Production</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
