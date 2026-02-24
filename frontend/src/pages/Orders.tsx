import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';
import './Orders.css';

interface OrderItem {
    name: string;
    base_price: number;
    tax_percent: number;
    commission_percent: number;
    quantity: number;
    // readonly
    final_price?: number;
}

interface Order {
    id: string;
    client_id: string;
    status: string;
    total_tax: number;
    total_commission: number;
    total_profit: number;
    total_amount: number;
    date: string;
    payment_method: string;
    created_at: string;
    items: OrderItem[];
}

interface Client {
    id: string;
    name: string;
    last_name: string;
}

export default function Orders() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);

    // Modal states
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Form state
    const [formData, setFormData] = useState({
        client_id: '',
        payment_bank: '',
        payment_method: '',
        date: new Date().toISOString().split('T')[0],
        notes: '',
    });

    const [items, setItems] = useState<OrderItem[]>([{
        name: '', base_price: 0, tax_percent: 0, commission_percent: 0, quantity: 1
    }]);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [ordersRes, clientsRes] = await Promise.all([
                apiClient.get<Order[]>('/orders/'),
                apiClient.get<Client[]>('/clients/')
            ]);
            setOrders(ordersRes.data);
            setClients(clientsRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const openModal = () => {
        setFormData({
            client_id: clients.length > 0 ? clients[0].id : '',
            payment_bank: '',
            payment_method: 'Zelle',
            date: new Date().toISOString().split('T')[0],
            notes: ''
        });
        setItems([{ name: '', base_price: 0, tax_percent: 0, commission_percent: 0, quantity: 1 }]);
        setIsModalOpen(true);
    };

    const handleItemChange = (index: number, field: keyof OrderItem, value: any) => {
        const newItems = [...items];
        newItems[index] = { ...newItems[index], [field]: value };
        setItems(newItems);
    };

    const addItemRow = () => {
        setItems([...items, { name: '', base_price: 0, tax_percent: 0, commission_percent: 0, quantity: 1 }]);
    };

    const removeItemRow = (index: number) => {
        setItems(items.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!formData.client_id) return alert("Please select a client");
        if (items.some(i => !i.name || i.base_price <= 0)) return alert("Please review order items");

        try {
            const payload = {
                ...formData,
                items
            };
            await apiClient.post('/orders/', payload);
            setIsModalOpen(false);
            fetchData();
        } catch (err) {
            console.error(err);
            alert("Error creating order");
        }
    };

    const handleStatusChange = async (id: string, newStatus: string) => {
        try {
            await apiClient.patch(`/orders/${id}/status`, { status: newStatus });
            fetchData();
        } catch (err) {
            alert("Error updating status");
        }
    };

    const downloadPDF = async (id: string) => {
        try {
            const response = await apiClient.get(`/orders/${id}/pdf`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `invoice_${id.substring(0, 8)}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert("Error generating PDF");
        }
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Orders Management</h1>
                <button className="btn btn-primary" onClick={openModal}>+ New Order</button>
            </div>

            <div className="card table-container">
                {loading ? <p>Loading...</p> : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Status</th>
                                <th>Total ($)</th>
                                <th>Profit ($)</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {orders.map(order => (
                                <tr key={order.id}>
                                    <td>{order.date}</td>
                                    <td>
                                        <select
                                            className={`status-badge status-${order.status.toLowerCase()}`}
                                            value={order.status}
                                            onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                        >
                                            <option value="PENDING">PENDING</option>
                                            <option value="PURCHASED">PURCHASED</option>
                                            <option value="SHIPPED">SHIPPED</option>
                                            <option value="DELIVERED">DELIVERED</option>
                                            <option value="CANCELLED">CANCELLED</option>
                                        </select>
                                    </td>
                                    <td>${Number(order.total_amount).toFixed(2)}</td>
                                    <td className="text-success">+${Number(order.total_profit).toFixed(2)}</td>
                                    <td className="actions-cell">
                                        <button className="btn btn-outline btn-sm" onClick={() => downloadPDF(order.id)}>
                                            PDF
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content card order-modal">
                        <h2>Create New Order</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label className="form-label">Client *</label>
                                    <select
                                        className="form-control"
                                        value={formData.client_id}
                                        onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                                        required
                                    >
                                        <option value="" disabled>Select a client</option>
                                        {clients.map(c => (
                                            <option key={c.id} value={c.id}>{c.name} {c.last_name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group flex-1">
                                    <label className="form-label">Date *</label>
                                    <input type="date" required className="form-control" value={formData.date} onChange={e => setFormData({ ...formData, date: e.target.value })} />
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label className="form-label">Payment Bank</label>
                                    <input className="form-control" value={formData.payment_bank} onChange={e => setFormData({ ...formData, payment_bank: e.target.value })} />
                                </div>
                                <div className="form-group flex-1">
                                    <label className="form-label">Method</label>
                                    <input className="form-control" placeholder="Cash, Zelle..." value={formData.payment_method} onChange={e => setFormData({ ...formData, payment_method: e.target.value })} />
                                </div>
                            </div>

                            <hr className="divider" />
                            <h3>Order Items</h3>

                            {items.map((item, index) => (
                                <div key={index} className="item-row card bg-light mb-3">
                                    <button type="button" className="btn-close" onClick={() => removeItemRow(index)}>×</button>
                                    <div className="form-row">
                                        <div className="form-group flex-2">
                                            <label className="form-label">Product Name</label>
                                            <input required className="form-control" value={item.name} onChange={e => handleItemChange(index, 'name', e.target.value)} />
                                        </div>
                                        <div className="form-group flex-1">
                                            <label className="form-label">Quantity</label>
                                            <input type="number" min="1" required className="form-control" value={item.quantity} onChange={e => handleItemChange(index, 'quantity', parseInt(e.target.value))} />
                                        </div>
                                    </div>
                                    <div className="form-row">
                                        <div className="form-group flex-1">
                                            <label className="form-label">Base Price ($)</label>
                                            <input type="number" step="0.01" required className="form-control" value={item.base_price} onChange={e => handleItemChange(index, 'base_price', parseFloat(e.target.value))} />
                                        </div>
                                        <div className="form-group flex-1">
                                            <label className="form-label">Tax (%)</label>
                                            <input type="number" step="0.1" className="form-control" value={item.tax_percent} onChange={e => handleItemChange(index, 'tax_percent', parseFloat(e.target.value))} />
                                        </div>
                                        <div className="form-group flex-1">
                                            <label className="form-label">Com (%)</label>
                                            <input type="number" step="0.1" className="form-control" value={item.commission_percent} onChange={e => handleItemChange(index, 'commission_percent', parseFloat(e.target.value))} />
                                        </div>
                                    </div>
                                </div>
                            ))}

                            <button type="button" className="btn btn-outline mb-3" onClick={addItemRow}>+ Add Product</button>

                            <div className="form-group">
                                <label className="form-label">Notes (Optional)</label>
                                <textarea className="form-control" value={formData.notes} onChange={e => setFormData({ ...formData, notes: e.target.value })} />
                            </div>

                            <div className="modal-actions">
                                <button type="button" className="btn btn-outline" onClick={() => setIsModalOpen(false)}>Cancel</button>
                                <button type="submit" className="btn btn-primary">Create Order</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
