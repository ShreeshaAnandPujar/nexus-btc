import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  Search,
  Users,
  Network,
  GitFork,
  HelpCircle,
  BarChart2,
  Cpu,
  Server,
} from 'lucide-react';

interface NavigationProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  alertCount?: number;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentTab,
  onSelectTab,
  alertCount = 0,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Command Center', icon: LayoutDashboard },
    { id: 'alerts', label: 'Alert Queue', icon: AlertTriangle, badge: alertCount },
    { id: 'investigate', label: 'Investigate', icon: Search },
    { id: 'entities', label: 'Inferred Entities', icon: Users },
    { id: 'graph', label: 'Forensic Graph', icon: Network },
    { id: 'trace', label: 'Fund Tracer', icon: GitFork },
    { id: 'explain', label: 'XAI Studio', icon: HelpCircle },
    { id: 'models', label: 'Model Metrics', icon: BarChart2 },
    { id: 'scenarios', label: 'Scenario Studio', icon: Cpu },
    { id: 'system', label: 'System Health', icon: Server },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: '20px 16px', borderBottom: '1px solid #1e293b', display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '6px', background: 'linear-gradient(135deg, #0284c7, #10b981)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
          ₿
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '15px', letterSpacing: '1px', color: '#f8fafc' }}>NEXUS-BTC</div>
          <div style={{ fontSize: '10px', color: '#10b981', fontWeight: 600 }}>OFFLINE SURVEILLANCE</div>
        </div>
      </div>

      {/* Nav list */}
      <nav style={{ padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 4, flex: 1, overflowY: 'auto' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                borderRadius: '6px',
                border: 'none',
                background: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                color: isActive ? '#38bdf8' : '#94a3b8',
                fontWeight: isActive ? 600 : 500,
                fontSize: '13px',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <Icon size={18} color={isActive ? '#38bdf8' : '#64748b'} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span
                  style={{
                    background: '#ef4444',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 'bold',
                    padding: '1px 6px',
                    borderRadius: '10px',
                  }}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer provenance notice */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid #1e293b', fontSize: '10px', color: '#64748b' }}>
        <div>NTRO SIH 2026 PS-05</div>
        <div>Air-Gapped Clean Room v1.0</div>
      </div>
    </aside>
  );
};
