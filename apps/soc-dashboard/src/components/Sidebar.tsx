import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Target, 
  Search, 
  Server, 
  Settings,
  ShieldAlert,
  Globe
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/incidents', label: 'Incident Management', icon: ShieldAlert },
    { href: '/hunting', label: 'Threat Hunting', icon: Search },
    { href: '/mitre', label: 'MITRE ATT&CK', icon: Target },
    { href: '/intel', label: 'Threat Intel Center', icon: Globe },
    { href: '/sensors', label: 'Sensor Fleet', icon: Server },
    { href: '/settings', label: 'Administration', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-gray-300 min-h-screen border-r border-gray-800 flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
            <LayoutDashboard size={20} className="text-white" />
          </div>
          <span className="text-blue-500">SENTINELS</span>
        </h1>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href || (pathname.startsWith(link.href) && link.href !== '/');
          
          return (
            <Link 
              key={link.href} 
              href={link.href} 
              className={cn(
                "flex items-center gap-3 p-3 rounded-lg transition-colors font-medium text-sm",
                isActive 
                  ? "bg-blue-600/10 text-blue-500" 
                  : "hover:bg-gray-800 hover:text-white"
              )}
            >
              <Icon size={18} />
              {link.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        Tenant: <strong className="text-gray-300">tenant-01</strong><br/>
        Role: <span className="text-gray-400">L2 Analyst</span>
      </div>
    </aside>
  );
}
