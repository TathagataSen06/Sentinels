"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Settings, Users, Building2, ShieldCheck, UserPlus, Search, Building } from 'lucide-react';

export default function Administration() {
  const [activeTab, setActiveTab] = useState<'users' | 'orgs' | 'roles'>('users');

  const users = [
    { name: 'Tathagata Sen', email: 'tsen@sentinels.local', role: 'Global Admin', org: 'All', mfa: true, status: 'Active' },
    { name: 'Alice Smith', email: 'asmith@tenant01.com', role: 'L2 Analyst', org: 'Tenant-01', mfa: true, status: 'Active' },
    { name: 'Bob Jones', email: 'bjones@tenant01.com', role: 'L1 Analyst', org: 'Tenant-01', mfa: false, status: 'Active' },
    { name: 'Charlie Davis', email: 'cdavis@tenant02.com', role: 'Org Admin', org: 'Tenant-02', mfa: true, status: 'Pending' },
  ];

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
      <header className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            <Settings className="text-blue-500" size={32} />
            Administration
          </h2>
          <p className="text-gray-400 mt-2">Manage multi-tenant settings, users, and RBAC policies</p>
        </div>
      </header>

      <div className="flex gap-4 border-b border-gray-800 pb-px">
        <button 
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'users' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
        >
          <Users size={16} /> Users
        </button>
        <button 
          onClick={() => setActiveTab('orgs')}
          className={`px-4 py-2 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'orgs' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
        >
          <Building2 size={16} /> Organizations
        </button>
        <button 
          onClick={() => setActiveTab('roles')}
          className={`px-4 py-2 font-medium text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'roles' ? 'border-blue-500 text-blue-400' : 'border-transparent text-gray-400 hover:text-gray-200'}`}
        >
          <ShieldCheck size={16} /> Roles & Permissions
        </button>
      </div>

      <div className="flex-1">
        {activeTab === 'users' && (
          <Card className="bg-gray-900 border-gray-800 h-full flex flex-col">
            <CardHeader className="border-b border-gray-800 flex flex-row items-center justify-between pb-4">
              <div className="relative w-64">
                <Search className="absolute left-3 top-2.5 text-gray-500" size={16} />
                <Input placeholder="Search users..." className="pl-9" />
              </div>
              <Button className="bg-blue-600 hover:bg-blue-500 gap-2"><UserPlus size={16} /> Invite User</Button>
            </CardHeader>
            <CardContent className="p-0 flex-1 overflow-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Organization</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>MFA Status</TableHead>
                    <TableHead>Account Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((user, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-semibold">{user.name}</TableCell>
                      <TableCell className="text-gray-400">{user.email}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-gray-300 gap-1 border-gray-700">
                          <Building size={12} /> {user.org}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="bg-gray-800 text-gray-300">{user.role}</Badge>
                      </TableCell>
                      <TableCell>
                        {user.mfa ? 
                          <span className="text-green-400 text-sm font-medium flex items-center gap-1"><ShieldCheck size={14}/> Enabled</span> : 
                          <span className="text-orange-400 text-sm font-medium">Disabled</span>
                        }
                      </TableCell>
                      <TableCell>
                        <Badge variant={user.status === 'Active' ? 'success' : 'warning'}>{user.status}</Badge>
                      </TableCell>
                      <TableCell className="text-right text-blue-400 hover:text-blue-300 cursor-pointer text-sm font-medium">
                        Edit
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {activeTab === 'orgs' && (
          <Card className="bg-gray-900 border-gray-800 p-8 flex flex-col items-center justify-center text-center h-[400px]">
             <Building2 size={48} className="text-gray-700 mb-4" />
             <h3 className="text-xl font-semibold mb-2">Organization Management</h3>
             <p className="text-gray-400 max-w-md mb-6">Create and manage multi-tenant environments, configure data boundaries, and set global organization policies.</p>
             <Button>Register New Organization</Button>
          </Card>
        )}

        {activeTab === 'roles' && (
          <Card className="bg-gray-900 border-gray-800 p-8 flex flex-col items-center justify-center text-center h-[400px]">
             <ShieldCheck size={48} className="text-gray-700 mb-4" />
             <h3 className="text-xl font-semibold mb-2">RBAC Configuration</h3>
             <p className="text-gray-400 max-w-md mb-6">Define custom roles, map permissions to Active Directory groups, and configure resource access policies.</p>
             <Button>Create Custom Role</Button>
          </Card>
        )}
      </div>
    </div>
  );
}
