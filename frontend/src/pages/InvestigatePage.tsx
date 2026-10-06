import React, { useState } from 'react';
import { Search, ArrowRight, ShieldAlert, Globe, Server, Cpu } from 'lucide-react';
import { fetchTransactions, fetchTransactionDetail } from '../services/api';

interface InvestigatePageProps {
  onNavigateToTrace?: (id: string) => void;
  onNavigateToGraph?: (id: string) => void;
}

export const InvestigatePage: React.FC<InvestigatePageProps> = ({
  onNavigateToTrace,
  onNavigateToGraph,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [selectedTx, setSelectedTx] = useState<any | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setIsSearching(true);
    setSelectedTx(null);
    try {
      const data = await fetchTransactions(searchTerm.trim(), 20);
      setResults(data);
      if (data.length === 1) {
        const detail = await fetchTransactionDetail(data[0].txid);
        setSelectedTx(detail);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectTx = async (txid: string) => {
    try {
      const detail = await fetchTransactionDetail(txid);
      setSelectedTx(detail);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="page-scrollable">
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, color: '#f8fafc', marginBottom: 4 }}>
          Digital Forensics Investigator
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Deep telemetry inspection across Bitcoin transaction hashes, wallet addresses, and relay IPs.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 10, marginBottom: 24, maxWidth: '800px' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            type="text"
            placeholder="Search by TXID (64 hex), Wallet Address (1.../3.../bc1...), or Relay IP..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px 12px 40px',
              background: '#111827',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#f8fafc',
              fontSize: '13px',
              fontFamily: 'monospace',
            }}
          />
          <Search size={16} color="#64748b" style={{ position: 'absolute', left: 14, top: 14 }} />
        </div>
        <button type="submit" className="btn-primary" disabled={isSearching}>
          Search
        </button>
      </form>

      {/* Main Investigation Split */}
      <div style={{ display: 'grid', gridTemplateColumns: selectedTx ? '1fr 1fr' : '1fr', gap: 20 }}>
        {/* Results List */}
        <div className="nexus-card">
          <h2 style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: 12 }}>
            Search Results ({results.length})
          </h2>
          {results.length === 0 ? (
            <div style={{ color: '#64748b', fontSize: '13px', textAlign: 'center', padding: '40px 0' }}>
              Enter a transaction hash or wallet address to inspect on-chain telemetry.
            </div>
          ) : (
            <div className="table-container">
              <table className="nexus-table">
                <thead>
                  <tr>
                    <th>TXID</th>
                    <th>Volume</th>
                    <th>Relay IP</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r) => (
                    <tr
                      key={r.txid}
                      onClick={() => handleSelectTx(r.txid)}
                      style={{ cursor: 'pointer', background: selectedTx?.txid === r.txid ? 'rgba(56, 189, 248, 0.08)' : undefined }}
                    >
                      <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>
                        {r.txid.slice(0, 12)}...{r.txid.slice(-6)}
                      </td>
                      <td style={{ fontFamily: 'monospace' }}>
                        {r.output_amount_btc.toFixed(4)} BTC
                      </td>
                      <td style={{ fontFamily: 'monospace', color: '#94a3b8' }}>
                        {r.src_ip}
                      </td>
                      <td>
                        <span className={`score-pill ${r.risk_score >= 80 ? 'score-critical' : r.risk_score >= 50 ? 'score-high' : 'score-low'}`}>
                          {r.risk_score.toFixed(0)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Selected Transaction Deep Forensic Dossier */}
        {selectedTx && (
          <div className="nexus-card" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: 10 }}>
              <div>
                <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 'bold' }}>TRANSACTION DOSSIER</span>
                <div style={{ fontFamily: 'monospace', fontSize: '12px', color: '#f8fafc', wordBreak: 'break-all' }}>
                  {selectedTx.txid}
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div style={{ display: 'flex', gap: 10 }}>
              {onNavigateToTrace && (
                <button className="btn-secondary" onClick={() => onNavigateToTrace(selectedTx.txid)} style={{ flex: 1, fontSize: '12px' }}>
                  Trace Funds
                </button>
              )}
              {onNavigateToGraph && (
                <button className="btn-secondary" onClick={() => onNavigateToGraph(selectedTx.txid)} style={{ flex: 1, fontSize: '12px' }}>
                  Ego Subgraph
                </button>
              )}
            </div>

            {/* Meta Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              <div style={{ background: '#111827', padding: '10px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: '#94a3b8' }}>VOLUME (BTC)</div>
                <div style={{ fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f8fafc' }}>
                  {selectedTx.output_amount.toFixed(4)}
                </div>
              </div>
              <div style={{ background: '#111827', padding: '10px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: '#94a3b8' }}>MINER FEE</div>
                <div style={{ fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace', color: '#f8fafc' }}>
                  {selectedTx.fee.toFixed(6)}
                </div>
              </div>
              <div style={{ background: '#111827', padding: '10px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: '#94a3b8' }}>SCRIPT TYPE</div>
                <div style={{ fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace', color: '#38bdf8' }}>
                  {selectedTx.script_type}
                </div>
              </div>
            </div>

            {/* Network Telemetry */}
            <div style={{ background: '#111827', padding: '12px', borderRadius: '6px', border: '1px solid #1e293b' }}>
              <div style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 'bold', marginBottom: 6 }}>
                NETWORK TELEMETRY CORRELATION
              </div>
              <div style={{ display: 'flex', gap: 16, fontSize: '12px' }}>
                <span>Source IP: <strong style={{ fontFamily: 'monospace', color: '#f8fafc' }}>{selectedTx.src_ip}</strong></span>
                <span>Country: <strong style={{ color: '#10b981' }}>{selectedTx.country}</strong></span>
                <span>ASN: <strong style={{ color: '#f8fafc' }}>AS{selectedTx.asn}</strong></span>
              </div>
            </div>

            {/* Inputs & Outputs Breakdown */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#38bdf8', marginBottom: 6 }}>
                  INPUTS ({selectedTx.input_addresses.length})
                </div>
                <div style={{ maxHeight: '160px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {selectedTx.input_addresses.map((addr: string, i: number) => (
                    <div key={i} style={{ background: '#090d16', padding: '6px 8px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>
                      <div style={{ color: '#cbd5e1', overflow: 'hidden', textOverflow: 'ellipsis' }}>{addr}</div>
                      <div style={{ color: '#94a3b8', fontSize: '10px' }}>
                        {selectedTx.input_amounts[i] ? `${selectedTx.input_amounts[i].toFixed(4)} BTC` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#10b981', marginBottom: 6 }}>
                  OUTPUTS ({selectedTx.output_addresses.length})
                </div>
                <div style={{ maxHeight: '160px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {selectedTx.output_addresses.map((addr: string, i: number) => (
                    <div key={i} style={{ background: '#090d16', padding: '6px 8px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>
                      <div style={{ color: '#cbd5e1', overflow: 'hidden', textOverflow: 'ellipsis' }}>{addr}</div>
                      <div style={{ color: '#94a3b8', fontSize: '10px' }}>
                        {selectedTx.output_amounts[i] ? `${selectedTx.output_amounts[i].toFixed(4)} BTC` : ''}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
