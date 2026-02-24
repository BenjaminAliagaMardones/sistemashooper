import { useState, useEffect } from 'react';
import { apiClient } from '../api/axios';
import './Settings.css';

interface BusinessConfig {
    business_name: string;
    logo_url: string;
    base_currency: string;
    contact_email: string;
}

export default function Settings() {
    const [config, setConfig] = useState<BusinessConfig>({
        business_name: '',
        logo_url: '',
        base_currency: 'USD',
        contact_email: '',
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const { data } = await apiClient.get<BusinessConfig>('/settings/');
                setConfig(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchConfig();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setConfig({ ...config, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);
        try {
            await apiClient.put('/settings/', config);
            setMessage({ type: 'success', text: 'Settings saved successfully' });
        } catch (err) {
            setMessage({ type: 'error', text: 'Error saving settings' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="page-container"><p>Loading settings...</p></div>;

    return (
        <div className="page-container">
            <div className="page-header">
                <h1>Business Settings</h1>
                <p className="text-muted">Configure how your invoices and dashboard look</p>
            </div>

            <div className="settings-container card">
                {message && (
                    <div className={`alert alert-${message.type === 'success' ? 'success' : 'danger'}`}>
                        {message.text}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="settings-form">
                    <div className="form-group">
                        <label className="form-label">Business Name</label>
                        <input
                            required
                            name="business_name"
                            className="form-control"
                            value={config.business_name || ''}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Contact Email (Shown on Invoice)</label>
                        <input
                            type="email"
                            name="contact_email"
                            className="form-control"
                            value={config.contact_email || ''}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Base Currency</label>
                        <select
                            name="base_currency"
                            className="form-control"
                            value={config.base_currency || 'USD'}
                            onChange={handleChange}
                        >
                            <option value="USD">USD ($)</option>
                            <option value="CLP">CLP ($)</option>
                            <option value="EUR">EUR (€)</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Logo URL</label>
                        <input
                            type="url"
                            name="logo_url"
                            className="form-control"
                            placeholder="https://example.com/logo.png"
                            value={config.logo_url || ''}
                            onChange={handleChange}
                        />
                        <small className="text-muted" style={{ display: 'block', marginTop: '0.5rem' }}>
                            Provide a direct URL to an image hosted online (e.g. AWS S3, Cloudinary). This will be printed on PDFs.
                        </small>

                        {config.logo_url && (
                            <div className="logo-preview mt-3">
                                <p>Preview:</p>
                                <img src={config.logo_url} alt="Logo preview" style={{ maxHeight: '100px' }} />
                            </div>
                        )}
                    </div>

                    <div className="form-actions" style={{ marginTop: '2rem' }}>
                        <button type="submit" className="btn btn-primary" disabled={saving}>
                            {saving ? 'Saving...' : 'Save Configuration'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
