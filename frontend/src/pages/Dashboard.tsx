import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';
import './Dashboard.css';

interface Metrics {
    month: number;
    year: number;
    total_revenue: number;
    total_profit: number;
    order_count: number;
    ticket_promedio: number;
}

interface TopClient {
    client_id: string;
    name: string;
    total_orders: number;
    total_spent: number;
}

export default function Dashboard() {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [topClients, setTopClients] = useState<TopClient[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                const [metricsRes, clientsRes] = await Promise.all([
                    apiClient.get<Metrics>('/dashboard/metrics'),
                    apiClient.get<TopClient[]>('/dashboard/best-clients')
                ]);
                setMetrics(metricsRes.data);
                setTopClients(clientsRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboardData();
    }, []);

    if (loading) return <div className="page-container"><p>Loading metrics...</p></div>;
    if (!metrics) return null;

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Dashboard Overview</h1>
                <p className="text-muted">Metrics for {new Date(metrics.year, metrics.month - 1).toLocaleString('default', { month: 'long', year: 'numeric' })}</p>
            </div>

            <div className="metrics-grid">
                <div className="metric-card card">
                    <h3>Total Revenue</h3>
                    <div className="metric-val primary">${metrics.total_revenue.toFixed(2)}</div>
                </div>
                <div className="metric-card card">
                    <h3>Net Profit (Commissions)</h3>
                    <div className="metric-val success">+ ${metrics.total_profit.toFixed(2)}</div>
                </div>
                <div className="metric-card card">
                    <h3>Orders This Month</h3>
                    <div className="metric-val text-main">{metrics.order_count}</div>
                </div>
                <div className="metric-card card">
                    <h3>Average Ticket</h3>
                    <div className="metric-val warning">${metrics.ticket_promedio.toFixed(2)}</div>
                </div>
            </div>

            <div className="dashboard-sections">
                <div className="card flex-2">
                    <h2>Top Clients VIP</h2>
                    {topClients.length === 0 ? <p>No clients yet.</p> : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Client</th>
                                    <th>Orders</th>
                                    <th>Total Spent</th>
                                </tr>
                            </thead>
                            <tbody>
                                {topClients.map((c, i) => (
                                    <tr key={c.client_id}>
                                        <td>
                                            <span className="rank-badge">{i + 1}</span>
                                            <strong>{c.name}</strong>
                                        </td>
                                        <td>{c.total_orders}</td>
                                        <td className="primary fw-bold">${Number(c.total_spent).toFixed(2)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Placeholder for Quick Actions or Announcements */}
                <div className="card flex-1 bg-primary text-white text-center d-flex-col-center">
                    <div style={{ color: 'white' }}>
                        <h2>Need a hand?</h2>
                        <p>Remember that you can configure your invoice PDF logo in the Settings view.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
