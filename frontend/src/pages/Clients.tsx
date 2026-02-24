import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';
import './Clients.css';

interface Client {
    id: string;
    name: string;
    last_name: string;
    email: string | null;
    phone: string | null;
    address: string | null;
    created_at: string;
}

export default function Clients() {
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Form State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingClient, setEditingClient] = useState<Client | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        last_name: '',
        email: '',
        phone: '',
        address: ''
    });

    const fetchClients = async () => {
        try {
            setLoading(true);
            const { data } = await apiClient.get<Client[]>('/clients/');
            setClients(data);
        } catch (err) {
            setError('Error loading clients');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const openModal = (client?: Client) => {
        if (client) {
            setEditingClient(client);
            setFormData({
                name: client.name,
                last_name: client.last_name,
                email: client.email || '',
                phone: client.phone || '',
                address: client.address || ''
            });
        } else {
            setEditingClient(null);
            setFormData({ name: '', last_name: '', email: '', phone: '', address: '' });
        }
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setEditingClient(null);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (editingClient) {
                await apiClient.put(`/clients/${editingClient.id}`, formData);
            } else {
                await apiClient.post('/clients/', formData);
            }
            closeModal();
            fetchClients();
        } catch (err) {
            console.error(err);
            alert("Error saving client");
        }
    };

    const handleDelete = async (id: string) => {
        if (window.confirm("Are you sure you want to delete this client?")) {
            try {
                await apiClient.delete(`/clients/${id}`);
                fetchClients();
            } catch (err) {
                console.error(err);
                alert("Error deleting client");
            }
        }
    };

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Clients Management</h1>
                <button className="btn btn-primary" onClick={() => openModal()}>+ Add Client</button>
            </div>

            {error && <div className="alert alert-danger">{error}</div>}

            <div className="card table-container">
                {loading ? (
                    <p>Loading clients...</p>
                ) : clients.length === 0 ? (
                    <p>No clients found. Add your first client to get started!</p>
                ) : (
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Joined</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {clients.map(client => (
                                <tr key={client.id}>
                                    <td><strong>{client.name} {client.last_name}</strong></td>
                                    <td>{client.email || '-'}</td>
                                    <td>{client.phone || '-'}</td>
                                    <td>{new Date(client.created_at).toLocaleDateString()}</td>
                                    <td className="actions-cell">
                                        <button className="btn btn-outline btn-sm" onClick={() => openModal(client)}>Edit</button>
                                        <button className="btn btn-outline btn-sm text-danger" onClick={() => handleDelete(client.id)}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* Basic Modal */}
            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content card">
                        <h2>{editingClient ? 'Edit Client' : 'New Client'}</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-row">
                                <div className="form-group flex-1">
                                    <label className="form-label">First Name *</label>
                                    <input required name="name" value={formData.name} onChange={handleInputChange} className="form-control" />
                                </div>
                                <div className="form-group flex-1">
                                    <label className="form-label">Last Name *</label>
                                    <input required name="last_name" value={formData.last_name} onChange={handleInputChange} className="form-control" />
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email</label>
                                <input type="email" name="email" value={formData.email} onChange={handleInputChange} className="form-control" />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Phone</label>
                                <input name="phone" value={formData.phone} onChange={handleInputChange} className="form-control" />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Address</label>
                                <input name="address" value={formData.address} onChange={handleInputChange} className="form-control" />
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn btn-outline" onClick={closeModal}>Cancel</button>
                                <button type="submit" className="btn btn-primary">Save Client</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
